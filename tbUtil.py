"""
utility management for timebandit
"""

from argparse import ArgumentParser
import AppManager
from tb_Settings import *

class tbParser(object):
    """
    management class for adding command line arguments and features
    """
    def __init__(self, *args, **kwargs):
        self.args = args[0][1:]
        self.parser = self._build_parser()

    def _build_parser(self):
        """
        build/return a global argument parser for timebandit
        """
        parser = ArgumentParser()

        parser.add_argument(
            'command',
            type=str,
            action='store',
            help=(
                "initialize a timebandit shell for headless use"
            ),
        )

        parser.add_argument(
            '-a', action='append_const',
            dest='flags',
            const='a',
            help=(
                "demo flag"
            ),
        )

        return parser

    def parse(self):
        p = self.parser.parse_args()
        return p.command, p.flags

def AppExec(command, flags):
    """
    finds an installed App and executes its method
    """
    if command in INSTALLED_APPS:
        whichapp = getattr(AppManager, command)
        if callable(whichapp):
            print "%s is callable" % (command)
            whichapp(flags)
        else:
            print "oops"
