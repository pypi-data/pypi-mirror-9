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
import sys
import re
import traceback
import itertools
import types
import random
import cgi
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from beaker.middleware import SessionMiddleware
from paste.cascade import Cascade
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool

from weberror import formatter, collector, reporter
from paste import wsgilib
from paste import request
from paste.util import import_string
from simplejson import loads

from webob import Request, Response
from webob import exc
from webob.exc import HTTPForbidden

from weberror.evalexception import make_eval_exception
from weberror.errormiddleware import ErrorMiddleware
from pyblox import tmpl_context as c, session


class CSRFMiddleware(object):
    """Middleware that adds protection against Cross Site
    Request Forgeries by adding hidden form fields to POST forms and
    checking requests for the correct value. It expects beaker to be upstream
    to insert the session into the environ.

    Added support for header check in xhr requests.

    For example, you will need to add the cookie to your post data if you use something like
    AngularJS without traditional form action methods.

    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

    """
    def __init__(self, app, config):
        self.app = app
        self.unprotected_path = config.get('csrf.unprotected_path')

    def __call__(self, environ, start_response):
        request = Request(environ)
        session = environ['beaker.session']
        csrftoken = session.get('csrftoken')
        if not csrftoken:
            csrftoken = session['csrftoken'] = str(random.getrandbits(128))
            session.save()

        if request.method == 'POST':
            if (self.unprotected_path is not None
                and request.path_info.startswith(self.unprotected_path)):
                resp = request.get_response(self.app)
                resp.headers['X-Frame-Options'] = 'SAMEORIGIN'
                resp.set_cookie('csrftoken', csrftoken, max_age=3600)
                return resp(environ, start_response)

            # check for incoming csrf token
            try:
                request_csrf_token = environ.get('HTTP_X_CSRFTOKEN',
                                                 request.POST.get('csrftoken'))
                if request_csrf_token != csrftoken:
                    resp = HTTPForbidden("CSRF - Aborted.")
                else:
                    resp = request.get_response(self.app)
            except KeyError:
                resp = HTTPForbidden("Forbidden: Administrator has been notified.")
        else:
            resp = request.get_response(self.app)

        if resp.status_int != 200:
            return resp(environ, start_response)

        resp.headers['X-Frame-Options'] = 'SAMEORIGIN'
        resp.set_cookie('csrftoken', csrftoken, max_age=3600)

        if resp.content_type.split(';')[0] in ['text/html', 'application/xhtml+xml']:
            # ensure we don't add the 'id' attribute twice (HTML validity)
            id_attr = itertools.chain(('id="csrftoken"',), itertools.repeat(''))
            def add_csrf_field(match):
                """Returns the matched <form> tag and adds the <input> element"""
                return match.group() + ('<input type="hidden" ' + id_attr.next() +
                       ' name="csrftoken" value="' + csrftoken + '" />')

            # Modify any POST forms and fix content-length
            body = re.compile(r'(<form\W.*)', re.IGNORECASE)
            resp.body = body.sub(add_csrf_field, resp.body)

        return resp(environ, start_response)

# Override the error middleware...
class PyBloxError(ErrorMiddleware):

    def exception_handler(self, exc_info, environ):
        simple_html_error = False
        if self.xmlhttp_key:
            get_vars = wsgilib.parse_querystring(environ)
            if dict(get_vars).get(self.xmlhttp_key):
                simple_html_error = True
        return handle_exception(
            exc_info, environ['wsgi.errors'],
            html=True,
            debug_mode=self.debug_mode,
            error_email=self.error_email,
            error_log=self.error_log,
            show_exceptions_in_wsgi_errors=self.show_exceptions_in_wsgi_errors,
            error_email_from=self.from_address,
            smtp_server=self.smtp_server,
            smtp_username=self.smtp_username,
            smtp_password=self.smtp_password,
            smtp_use_tls=self.smtp_use_tls,
            error_subject_prefix=self.error_subject_prefix,
            error_message=self.error_message,
            simple_html_error=simple_html_error,
            reporters=self.reporters)

# Handle it...
def handle_exception(exc_info, error_stream, html=True, debug_mode=False, error_email=None,
                     error_log=None, show_exceptions_in_wsgi_errors=False,
                     error_email_from='errors@localhost', smtp_server='localhost',
                     smtp_username=None, smtp_password=None, smtp_use_tls=False,
                     error_subject_prefix='', error_message=None, simple_html_error=False,
                     reporters=None):
    """
    For exception handling outside of a web context

    Use like::

        import sys
        import paste
        import paste.error_middleware
        try:
            do stuff
        except:
            paste.error_middleware.exception_handler(
                sys.exc_info(), paste.CONFIG, sys.stderr, html=False)

    If you want to report, but not fully catch the exception, call
    ``raise`` after ``exception_handler``, which (when given no argument)
    will reraise the exception.
    """

    reported = False
    exc_data = collector.collect_exception(*exc_info)
    extra_data = ''
    if error_email:
        rep = reporter.EmailReporter(
            to_addresses=error_email,
            from_address=error_email_from,
            smtp_server=smtp_server,
            smtp_username=smtp_username,
            smtp_password=smtp_password,
            smtp_use_tls=smtp_use_tls,
            subject_prefix=error_subject_prefix)
        rep_err = send_report(rep, exc_data, html=html)
        if rep_err:
            extra_data += rep_err
        else:
            reported = True
    if reporters:
        for rep in reporters:
            rep_err = send_report(rep, exc_data, html=html)
            if rep_err:
                extra_data += rep_err
            else:
                ## FIXME: should this be true?
                reported = True
    if error_log:
        rep = reporter.LogReporter(
            filename=error_log)
        rep_err = send_report(rep, exc_data, html=html)
        if rep_err:
            extra_data += rep_err
        else:
            reported = True
    if show_exceptions_in_wsgi_errors:
        rep = reporter.FileReporter(
            file=error_stream)
        rep_err = send_report(rep, exc_data, html=html)
        if rep_err:
            extra_data += rep_err
        else:
            reported = True
    else:
        error_stream.write('Error - %s: %s\n' % (
            exc_data.exception_type, exc_data.exception_value))
    if html:
        if debug_mode and simple_html_error:
            return_error = formatter.format_html(
                exc_data, include_hidden_frames=False,
                include_reusable=False, show_extra_data=False)
            reported = True
        elif debug_mode and not simple_html_error:
            error_html = formatter.format_html(
                exc_data,
                include_hidden_frames=True,
                include_reusable=False)
            head_html = ''
            return_error = error_template(
                head_html, error_html, extra_data)
            extra_data = ''
            reported = True
        else:
            msg = error_message or '''
            An error occurred.  See the error logs for more information.
            (Turn debug on to display exception reports here)
            '''
            return_error = error_template('', msg, '')
    else:
        return_error = None
    if not reported and error_stream:
        err_report = formatter.format_text(exc_data, show_hidden_frames=True)[0]
        err_report += '\n' + '-'*60 + '\n'
        error_stream.write(err_report)
    if extra_data:
        error_stream.write(extra_data)
    return return_error

# XXX: set by config
def send_report(rep, exc_data, html=True):
    try:
        rep.report(exc_data)
    except:
        output = StringIO()
        traceback.print_exc(file=output)
        if html:
            return """
            <p>Additionally, an error occurred while sending the %s report:

            <pre>%s</pre>
            </p>""" % (
                cgi.escape(str(rep)), output.getvalue())
        else:
            return (
                "Additionally, an error occurred while sending the "
                "%s report:\n%s" % (str(rep), output.getvalue()))
    else:
        return ''

# XXX: Customize and config
def error_template(head_html, exception, extra):
    return '''
<html>
    <head>
        <title>Server Error</title>
    %s
    </head>
    <body>
        <h1>Error</h1>
        <p>There has been an error processing this request. Please try again, or notify
        the server administrator if the error persists.</p>
    </body>
</html>''' % (head_html)

def make_error_middleware(app, global_conf, **kwargs):
    return PyBloxError(app, global_conf=global_conf, **kwargs)