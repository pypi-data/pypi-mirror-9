"""
    The MIT License (MIT)

    The Original Code is PyBlox.

    The Initial Developer of the Original Code is Noel Morgan,
    http://www.pyblox.org/

    Copyright (c) 2014 Noel Morgan <noel@morganix.com>

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
"""
import os
import time
import logging

from webob import exc
from webob.exc import status_map
from webob import Response

import functools
from functools import wraps
import inspect

from genshi.core import Stream
from genshi.output import encode, get_serializer
from genshi.template import Context, TemplateLoader

from pyblox import tmpl_context as c, session, config
import pyblox
from paste.recursive import ForwardRequestException
from paste.recursive import RecursiveMiddleware
from paste.errordocument import StatusKeeper

from json import dumps, loads
from decorator import decorator

from jinja2 import Environment, PackageLoader

jinja_env = Environment(loader=PackageLoader(config['pyblox.package'],
                                             'templates/html'))

log = logging.getLogger(__name__)

# Loader used for Genshi
loader = TemplateLoader(
    os.path.join(config['pyblox.paths']['root'], 'templates'),
    auto_reload=True
)

# Forwarding for internals
def forward(url, code=301):
    raise ForwardRequestException(url)

# Redirect for urls
def redirect(url):
    raise exc.HTTPTemporaryRedirect(location=url)


class AuthenticationError(Exception):
    message="Authentication error or incorrect permissions."

    def __init__(self, message=None):
        Exception.__init__(self, message or self.message)


# Simple auth checking
class Authenticated(object):
    def fn(self):
        if 'user' in session:
            return True
        else:
            return False

authenticated = Authenticated()


class Credential(object):
    '''Credential class for getting current credential entitlements from the
    user session.

    '''
    error_msg = u'Needs to have at least this permission.'

    def __init__(self, credentials_needed):
        self.credentials_needed = str(credentials_needed).split()

    def fn(self):
        req = pyblox.request._current_obj()
        if 'REMOTE_USER' in req.environ:
            try:
                permissions = str(req.environ['PERMISSIONS']).strip("[]").split(",")
                if permissions:
                    for permission in permissions:
                        log.debug("Has permission: {0}".format(permission))
                        for credential in self.credentials_needed:
                            log.debug("Needed {0}".format(credential))
                            if str(credential).strip() == str(permission).strip():
                                return True
                    return False
                else:
                    return False
            except Exception, e:
                log.debug("Excepted in credential: %s" % e)
                return False
        else:
            return False

credential = Credential

# @authorize decorator that takes credential arguments in a space or comma
# separated list e.g. credential('admin droid') etc.
def authorize(valid):
    def validate(func, self, *args, **kwargs):
        try:
            if valid.fn():
                return func(self, *args, **kwargs)
            else:
                log.debug("User permissions or not logged in...")
                g = pyblox.app_globals._current_obj()
                return forward(g.login_path, 301)
        except AuthenticationError, e:
            return AuthenticationError(e)
    return decorator(validate)

# Decorator for Genshi rendering.
def xml(filename, method='html', encoding='utf-8', **options):
    """Decorator for exposed methods to specify what template they should use
    for rendering, and which serialization method and options should be
    applied.
    """
    xmldir = 'xml/'

    def decorate(func):
        def wrapper(*args, **kwargs):
            c = pyblox.tmpl_context._current_obj()
            c.template = loader.load(xmldir+filename)
            opt = options.copy()
            if method == 'html':
                opt.setdefault('doctype', 'html')
            serializer = get_serializer(method, **opt)
            stream = func(*args, **kwargs)
            if not isinstance(stream, Stream):
                return stream
            return encode(serializer(stream), method=serializer,
                encoding=encoding)
        return wrapper
    return decorate

# Genshi rendering for the decorator above.
def xml_render(*args, **kwargs):
    """Function to render the given data to the template specified via the
    ``@xml`` decorator.
    """
    c = pyblox.tmpl_context._current_obj()
    g = pyblox.app_globals._current_obj()
    session = pyblox.session._current_obj()

    if args:
        assert len(args) == 1,\
        'Expected exactly one argument, but got %r' % (args,)
        template = loader.load(args[0])
    else:
        template = c.template
    # XXX:
    # ctxt = Context()
    # ctxt.push(kwargs)
    return template.generate(g=g, c=c, session=session, *args, **kwargs)

# Jinjna2 Template decorator.
def html(filename):
    def decorate(func):
        def wrapper(*args, **kwargs):
            c = pyblox.tmpl_context._current_obj()
            c.template = jinja_env.get_template(filename)
            return func(*args, **kwargs)
        return wrapper
    return decorate

# Rendering for above...
def html_render(*args, **kwargs):
    g = pyblox.app_globals._current_obj()
    session = pyblox.session._current_obj()
    c = pyblox.tmpl_context._current_obj()

    if args:
        assert len(args) == 1, 'Expected exactly one argument'
        template = jinja_env.get_template(args[0])
    else:
        template = c.template
    return template.render(session=session, g=g, c=c, *args, **kwargs)

# JSON output decorator - (supports args, parenthesis, or not).
def jsonify(func):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            string = fn(*args, **kwargs)
            def json_response(string):
                res = Response(content_type='application/json')
                res.body = dumps(string)
                return res
            return json_response(string)
        return wrapper
    if inspect.isfunction(func):
        return decorator(func)
    else:
        return decorator

