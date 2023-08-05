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
import sys
import re
import pyblox
from webob import Request, Response
from webob import exc
from json import loads, dumps


# RouteMap container object for regex templates, actions, and variable storage.
class RouteMap():
    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])


class Router(object):
    '''This is the handler dispatching mechanism for the controllers/method
    matching, and request routing.


    init takes a list of Map objects and compiles regexes to match URI
    requests. Upon a matching request, dispatch looks up the module, imports
    it, calls the callable class derived from ControllerBase and dispatches the
    request to the response object, or returns 404.

    If you want to do more than two layers of variable matching for your API,
    or ReST engine, You may wish to add more regular expression templates for
    your URI to variable parsing here.

    Example:
        my other_var_name = match.group(3)
        my_other_expr = match.group(4)

        They will still be available in the req.urlvars.

    '''

    # URI regex template
    uri_regex = re.compile(r'''
         \{          # The exact character "{"
         (\w+)       # The variable name (restricted to a-z, 0-9, _)
         (?::([^}]+))? # The optional :regex part
         \}          # The exact character "}"
         ''', re.VERBOSE)

    def __init__(self, routes):
        self.routes = []

        for route in routes:
            self.add_route(route)

    def add_route(self, route):
        self.routes.append((re.compile(self.template_to_regex(route.template)),
                            route))

    def template_to_regex(self, template):
        regex = ''
        last_pos = 0
        for match in self.uri_regex.finditer(template):
            regex += re.escape(template[last_pos:match.start()])
            var_name = match.group(1)
            expr = match.group(2) or '[^/]+'
            expr = '(?P<%s>%s)' % (var_name, expr)
            regex += expr
            last_pos = match.end()
        regex += re.escape(template[last_pos:])
        regex = '^%s$' % regex
        return regex

    # Controller routing
    def __call__(self, environ, start_response):
        req = Request(environ)

        for regex, route in self.routes:
            match = regex.match(req.path_info)

            if match:
                req.urlvars = match.groupdict()
                req.urlvars.update(route.__dict__)

                if 'action' in req.urlvars:
                   return self.dispatch(environ, start_response,
                                        route.handler,
                                        req.urlvars['action'],
                                        req.urlvars)
                else:
                    # NOTE: This really should never happen...
                    return self.dispatch(environ, start_response,
                                         route.handler,
                                         route.action, req.urlvars)

        # Nothing matched sending 404
        return exc.HTTPNotFound()(environ, start_response)

    # Dispatch to the controller.
    def dispatch(self, environ, start_response, handler, action, vars):
        module_name, class_name = handler.split(':', 1)
        __import__(module_name)
        module = sys.modules[module_name]
        klass = getattr(module, class_name)
        return klass()(environ, start_response, action, vars)
