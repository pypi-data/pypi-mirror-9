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
import pyblox
from paste.recursive import ForwardRequestException
from pyblox import tmpl_context as c, session, app_globals, auth_id
from webob import Request, Response
from webob import exc


def auth_user_id():
    try:
        auth_id = angularpy.auth_id._current_obj()
        return auth_id
    except TypeError:
        return None

def save_auth(req, user):
    req.environ["REMOTE_USER"] = str(user.username)
    req.environ["AUTH_ID"] = str(user.id)
    req.environ['PERMISSIONS'] = user.permissions
    req.environ["paste.auth.cookie"].append('AUTH_ID')
    req.environ["paste.auth.cookie"].append('PERMISSIONS')
    session['user'] = user
    session.save()

    return req

def remove_auth(req, session):

    if 'REMOTE_USER' in req.environ:
        del req.environ["AUTH_ID"]
        del req.environ["REMOTE_USER"]
        del req.environ['PERMISSIONS']

    g = pyblox.app_globals._current_obj()

    if 'user' in session:
        del session['user']
    session.invalidate()
    session.delete()

    raise ForwardRequestException(g.login_path)