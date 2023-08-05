# -*- coding: utf-8 -*-
import os
from watson.console import command
from watson.console.decorators import arg
from watson.common.imports import load_definition_from_string
from watson.di import ContainerAware
from watson.dev.server import make_dev_server


class Dev(command.Base, ContainerAware):
    """Development related tasks.

    Example:

    .. code-block::

       ./console.py dev runserver

    Provides access to the following commands during development:
        - runserver
    """
    @arg('host', optional=True)
    @arg('port', optional=True)
    def runserver(self, host, port):
        """Runs the development server for the current application.

        Args:
            host: The host to bind to
            port: The port to run on
        """
        app_dir = os.environ['APP_DIR']
        app_module = os.environ['APP_MODULE']
        script_dir = os.environ['SCRIPT_DIR']
        public_dir = os.environ['PUBLIC_DIR']
        os.chdir(app_dir)
        app = load_definition_from_string('{0}.app.application'.format(
            app_module))
        kwargs = {
            'app': app,
            'script_dir': script_dir,
            'public_dir': public_dir,
        }
        if host:
            kwargs['host'] = host
        if port:
            kwargs['port'] = int(port)
        make_dev_server(**kwargs)
