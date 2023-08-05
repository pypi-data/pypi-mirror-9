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
from webob import Request, Response
from json import loads, dumps
from webob import exc
from webob.exc import status_map

import inspect
import sys
import logging
import pyblox
from pyblox import config, auth_id, permissions
from paste.debug.profile import profile_decorator
from paste.recursive import ForwardRequestException
from paste.recursive import RecursiveMiddleware
from paste.errordocument import StatusKeeper

log = logging.getLogger(__name__)

class AngularPyContext(object):
    '''This is the class that holds all the context variables per request.

    '''
    pass

class WSGIApp(object):
    '''This is the base class from where all controllers are derived.

    '''

    def __init__(self):
        self.config = config or pyblox.config._current_obj()
        package_name = config['pyblox.package']
        self.helpers = config['pyblox.h']
        self.globals = config.get('pyblox.app_globals')
        self.environ_config = config['pyblox.environ_config']
        self.package_name = package_name
        self.log_debug = False
        self.config.setdefault('lang', 'en')
        self.auth_id = None
        self.permissions = None

        # Cache some options for use during requests
        self._session_key = self.environ_config.get('session', 'beaker.session')
        self._cache_key = self.environ_config.get('cache', 'beaker.cache')

    def _register(self, environ):
        # do the paste registry
        obj = environ['pyblox.pyblox']

        registry = environ['paste.registry']
        registry.register(pyblox.response, obj.response)
        registry.register(pyblox.request, obj.request)
        registry.register(pyblox.app_globals, self.globals)
        registry.register(pyblox.config, self.config)
        registry.register(pyblox.auth_id, self.auth_id)
        registry.register(pyblox.permissions, self.permissions)
        registry.register(pyblox.tmpl_context, obj.tmpl_context)

        if 'session' in obj.__dict__:
            registry.register(pyblox.session, obj.session)
        if 'cache' in obj.__dict__:
            registry.register(pyblox.cache, obj.cache)
        elif 'cache' in obj.app_globals.__dict__:
            registry.register(pyblox.cache, obj.app_globals.cache)

    def _setup_registery(self, environ, start_response):
        # Setup the basic pyblox thread-local objects
        req = Request(environ)
        req.config = self.config
        response = Response()

        # Store a copy of the request/response in environ for faster access
        obj = AngularPyContext()
        obj.config = self.config
        obj.request = req
        obj.response = response
        obj.app_globals = self.globals
        obj.auth_id = self.auth_id
        obj.permissions = self.permissions
        obj.h = self.helpers

        environ['pyblox.pyblox'] = obj
        environ['pyblox.environ_config'] = self.environ_config

        tmpl_context = AngularPyContext()
        obj.tmpl_context = req.tmpl_context = tmpl_context

        if self._session_key in environ:
            obj.session = req.session = environ[self._session_key]
        if self._cache_key in environ:
            obj.cache = environ[self._cache_key]

        # Load the globals with the registry if around
        if 'paste.registry' in environ:
            self._register(environ)

    # verify utility for dispatching to controller methods
    def _has_method(self, action):
        v = vars(self.__class__)
        return action in v and inspect.isroutine(v[action])

    def __call__(self, environ, start_response, action, vars):
        '''A requirement of the controller object, is that it is callable.
        Most of the routing is done in the Router.

        '''
        resp = None

        if 'REMOTE_USER' in environ:
            self.auth_id = environ['AUTH_ID']
            self.permissions = environ['PERMISSIONS']
        else:
            if 'AUTH_ID' in environ:
                del environ['AUTH_ID']
                self.auth_id = None
            if 'PERMISSIONS' in environ:
                del environ['PERMISSIONS']
                self.permissions = None

        # setup req
        self.request = Request(environ)

        # set session from cache
        self.request.session = environ[self._session_key]

        # Local this thread and register variables for this request.
        self._setup_registery(environ, start_response)

        try:
            if self._has_method(action):
                # Get the method from the derived class
                resp = getattr(self, action)(**vars)
            else:
                raise exc.HTTPNotFound("Method not found for controller: %s"
                                       % self.__class__.__name__)

            if isinstance(resp, dict):
                # Deprecated mostly...
                if 'redirect_login' in resp:
                    raise ForwardRequestException(self.globals.login_path)

            # See if it is just a string output
            if isinstance(resp, basestring):
                resp = Response(body=resp)

            if resp is None:
                resp = Response(body="Failed!")

            return resp(environ, start_response)

        except AttributeError as e:
            resp = Response(body="Failed AttributeError: {0}".format(e))

        except RuntimeError as e:
            resp = Response(body="Failed: %s" % e)

        except exc.HTTPException as e:
            # The exception object itself IS a WSGI application/response
            resp = e

        return resp(environ, start_response)
