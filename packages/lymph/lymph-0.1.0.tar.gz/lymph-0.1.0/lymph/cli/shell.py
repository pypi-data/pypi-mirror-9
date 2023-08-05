# -*- coding: utf-8 -*-
import logging

from lymph.client import Client
from lymph.cli.base import Command


logger = logging.getLogger(__name__)


class ShellCommand(Command):
    """
    Usage: lymph shell [options]

    Description:
        Opens a Python shell.

    {COMMON_OPTIONS}
    """

    short_description = 'Open an interactive Python shell.'

    def run(self, **kwargs):
        client = Client.from_config(self.config, **kwargs)
        imported_objects = {'client': client, 'config': self.config}

        try:
            import IPython
        except ImportError:
            IPython = None

        if IPython:
            IPython.start_ipython(
                argv=[],
                user_ns=imported_objects,
                banner1='Welcome to the lymph shell'
            )
        else:
            import code
            code.interact(local=imported_objects)

