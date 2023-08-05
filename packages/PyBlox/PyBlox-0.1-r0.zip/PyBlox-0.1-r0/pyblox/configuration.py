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
import copy
import logging
import os
import sys

from paste.config import DispatchingConfig
from paste.deploy.converters import asbool
from webhelpers.mimehelper import MIMETypes

config = DispatchingConfig()

sys.setrecursionlimit(1500)


class PyBloxConfig(dict):
    '''Pylonsish/pastish config for global vars, setting up beaker cache, and
    environment defaults.
    '''

    defaults = {
            'debug': False,
            'pyblox.package': None,
            'pyblox.paths': {'root': None,
                             'controllers': None,
                             'templates': [],
                             'static': None},
            'pyblox.environ_config': dict(session='beaker.session',
                cache='beaker.cache'),
            'pyblox.app_globals': None,
            'pyblox.h': None,
            'pyblox.login_path': None
        }

    def init_defaults(self, global_conf, app_conf, package=None, paths=None):
        conf = global_conf.copy()
        conf.update(app_conf)
        conf.update(dict(app_conf=app_conf, global_conf=global_conf))
        conf.update(self.pop('environment_load', {}))

        if paths:
            conf['pyblox.paths'] = paths
        conf['pyblox.package'] = package
        conf['debug'] = asbool(conf.get('debug'))

        # Load the MIMETypes with its default types
        MIMETypes.init()

        for key, val in copy.deepcopy(self.defaults).iteritems():
            conf.setdefault(key, val)

        if 'cache_dir' in conf:
            conf.setdefault('beaker.session.data_dir',
                os.path.join(conf['cache_dir'], 'sessions'))
            conf.setdefault('beaker.cache.data_dir',
                os.path.join(conf['cache_dir'], 'cache'))

        conf['pyblox.cache_dir'] = conf.pop('cache_dir',
            conf['app_conf'].get('cache_dir'))

        # Save our errorware values
        # Pylons did this nicely... still thinking about it.
        # conf['pyblox.errorware'] = errorware
        self.update(conf)


# Push the config object down to the DC
pyblox_config = PyBloxConfig()
pyblox_config.update(copy.deepcopy(PyBloxConfig.defaults))
config.push_process_config(pyblox_config)