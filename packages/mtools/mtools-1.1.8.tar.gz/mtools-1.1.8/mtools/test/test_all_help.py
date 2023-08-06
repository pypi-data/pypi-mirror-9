import sys
from nose.tools import *
from mtools.test import all_tools
from mtools.version import __version__
import time

@all_tools
def test_help(tool_cls):
    """ Check that all command line tools have a --help option that explains the usage.
        As per argparse default, this help text always starts with `usage:`.
    """
    tool = tool_cls()
   
    try:
        tool.run("--help")

    except SystemExit as e:
        if not hasattr(sys.stdout, "getvalue"):
            raise Exception('stdout not captured in test.')
        output = sys.stdout.getvalue().strip()
        assert output.startswith('usage:')


@all_tools
def test_version(tool_cls):
    """ Check that all command line tools have a --version option that returns the current version. """

    tool = tool_cls()
   
    try:
        tool.run("--version")

    except SystemExit as e:
        if not hasattr(sys.stdout, "getvalue"):
            raise Exception('stdout not captured in test.')

        # argparse's --version outputs to stderr, which can't be captured with nosetests.
        # therefore just checking that the scripts run and not output anything to stdout 
        output = sys.stdout.getvalue().strip()
        assert len(output) == 0
