"""Paster Commands, for use with paster in your project

.. highlight:: bash

The following commands are made available via paster utilizing
setuptools points discovery. These can be used from the command line
when the directory is the Pylons project.

Commands available:

``controller``
    Create a Controller and accompanying functional test
``restcontroller``
    Create a REST Controller and accompanying functional test
``shell``
    Open an interactive shell with the Pylons app loaded

Example usage::

    ~/sample$ paster controller account
    Creating /Users/ben/sample/sample/controllers/account.py
    Creating /Users/ben/sample/sample/tests/functional/test_account.py
    ~/sample$

.. admonition:: How it Works

    :command:`paster` is a command line script (from the PasteScript
    package) that allows the creation of context sensitive commands.
    :command:`paster` looks in the current directory for a
    ``.egg-info`` directory, then loads the ``paster_plugins.txt``
    file.

    Using setuptools entry points, :command:`paster` looks for
    functions registered with setuptools as
    :func:`paste.paster_command`. These are defined in the entry_points
    block in each packages :file:`setup.py` module.

    This same system is used when running :command:`paster create` to
    determine what templates are available when creating new projects.

"""
import os
import sys
import logging

import paste.fixture
import paste.registry
from paste.deploy import loadapp
from paste.script.command import Command, BadCommand
from paste.script.filemaker import FileOp
from tempita import paste_script_template_renderer

import pkg_resources
from paste.deploy.converters import asbool
from paste.script.appinstall import Installer

import pyblox
import pyblox.util as util

__all__ = ['ShellCommand']

def can_import(name):
    """Attempt to __import__ the specified package/module, returning
    True when succeeding, otherwise False"""
    try:
        __import__(name)
        return True
    except ImportError:
        return False


class PyBloxInstaller(Installer):
    use_cheetah = False
    config_file = 'config/deployment.ini_tmpl'

    def config_content(self, command, vars):
        """
        Called by ``self.write_config``, this returns the text content
        for the config file, given the provided variables.
        """
        modules = [line.strip()
                    for line in self.dist.get_metadata_lines('top_level.txt')
                    if line.strip() and not line.strip().startswith('#')]
        if not modules:
            print >> sys.stderr, 'No modules are listed in top_level.txt'
            print >> sys.stderr, 'Try running python setup.py egg_info to regenerate that file'
        for module in modules:
            if pkg_resources.resource_exists(module, self.config_file):
                return self.template_renderer(
                    pkg_resources.resource_string(module, self.config_file),
                    vars, filename=self.config_file)


class ShellCommand(Command):
    """Open an interactive shell with the Pylons app loaded

    The optional CONFIG_FILE argument specifies the config file to use for
    the interactive shell. CONFIG_FILE defaults to 'development.ini'.

    This allows you to test your mapper, models, and simulate web requests
    using ``paste.fixture``.

    Example::

        $ paster shell my-development.ini

    """
    summary = __doc__.splitlines()[0]
    usage = '\n' + __doc__

    min_args = 0
    max_args = 1
    group_name = 'pyblox'

    parser = Command.standard_parser(simulate=True)
    parser.add_option('-d', '--disable-ipython',
                      action='store_true',
                      dest='disable_ipython',
                      help="Don't use IPython if it is available")

    parser.add_option('-q',
                      action='count',
                      dest='quiet',
                      default=0,
                      help=("Do not load logging configuration from the "
                            "config file"))

    def command(self):
        """Main command to create a new shell"""
        self.verbose = 3
        if len(self.args) == 0:
            # Assume the .ini file is ./development.ini
            config_file = 'development.ini'
            if not os.path.isfile(config_file):
                raise BadCommand('%sError: CONFIG_FILE not found at: .%s%s\n'
                                 'Please specify a CONFIG_FILE' % \
                                 (self.parser.get_usage(), os.path.sep,
                                  config_file))
        else:
            config_file = self.args[0]

        config_name = 'config:%s' % config_file
        here_dir = os.getcwd()
        locs = dict(__name__="pyblox-admin")

        if not self.options.quiet:
            # Configure logging from the config file
            self.logging_file_config(config_file)

        # Load locals and populate with objects for use in shell
        sys.path.insert(0, here_dir)

        # Load the wsgi app first so that everything is initialized right
        wsgiapp = loadapp(config_name, relative_to=here_dir)
        test_app = paste.fixture.TestApp(wsgiapp)

        # Query the test app to setup the environment
        tresponse = test_app.get('/test')
        request_id = int(tresponse.body)

        # Disable restoration during test_app requests
        test_app.pre_request_hook = lambda self: \
            paste.registry.restorer.restoration_end()
        test_app.post_request_hook = lambda self: \
            paste.registry.restorer.restoration_begin(request_id)

        # Restore the state of the Pylons special objects
        # (StackedObjectProxies)
        paste.registry.restorer.restoration_begin(request_id)

        # Determine the package name from the pylons.config object
        pkg_name = pyblox.config['pyblox.package']

        # Start the rest of our imports now that the app is loaded
        model_module = pkg_name + '.model'
        helpers_module = pkg_name + '.lib.helpers'
        base_module = pkg_name + '.lib.base'

        if model_module and can_import(model_module):
            locs['model'] = sys.modules[model_module]

        if can_import(helpers_module):
            locs['h'] = sys.modules[helpers_module]

        exec ('from pyblox import app_globals, config, request, response, '
              'session, tmpl_context, url') in locs
        exec ('from pyblox.controllers.util import abort, forward') in locs
        locs.pop('__builtins__', None)

        # Import all objects from the base module
        __import__(base_module)

        base = sys.modules[base_module]
        base_public = [__name for __name in dir(base) if not \
                       __name.startswith('_') or __name == '_']
        locs.update((name, getattr(base, name)) for name in base_public)
        locs.update(dict(wsgiapp=wsgiapp, app=test_app))

        mapper = tresponse.config.get('routes.map')
        if mapper:
            locs['mapper'] = mapper

        banner = "  All objects from %s are available\n" % base_module
        banner += "  Additional Objects:\n"
        if mapper:
            banner += "  %-10s -  %s\n" % ('mapper', 'Routes mapper object')
        banner += "  %-10s -  %s\n" % ('wsgiapp',
            "This project's WSGI App instance")
        banner += "  %-10s -  %s\n" % ('app',
            'paste.fixture wrapped around wsgiapp')

        try:
            if self.options.disable_ipython:
                raise ImportError()

            # try to use IPython if possible
            try:
                # ipython >= 0.11
                from IPython.frontend.terminal.embed import InteractiveShellEmbed
                shell = InteractiveShellEmbed(banner2=banner)
            except ImportError:
                # ipython < 0.11
                from IPython.Shell import IPShellEmbed
                shell = IPShellEmbed(argv=self.args)
                shell.set_banner(shell.IP.BANNER + '\n\n' + banner)

            try:
                shell(local_ns=locs, global_ns={})
            finally:
                paste.registry.restorer.restoration_end()
        except ImportError:
            import code
            py_prefix = sys.platform.startswith('java') and 'J' or 'P'
            newbanner = "Pylons Interactive Shell\n%sython %s\n\n" % \
                (py_prefix, sys.version)
            banner = newbanner + banner
            shell = code.InteractiveConsole(locals=locs)
            try:
                import readline
            except ImportError:
                pass
            try:
                shell.interact(banner)
            finally:
                paste.registry.restorer.restoration_end()