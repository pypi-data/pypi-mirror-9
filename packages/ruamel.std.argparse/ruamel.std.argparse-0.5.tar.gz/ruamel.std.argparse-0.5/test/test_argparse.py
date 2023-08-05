# coding: utf-8
# Copyright Ruamel bvba 2007-2014

import pytest

try:
    from ruamel.std.argparse import argparse, CountAction, SmartFormatter
except ImportError:
    print("you have to install ruamel.std.argparse to run the tests")

from textwrap import dedent


def exit(self=None, status=None, message=None):
    pass


def test_argparse(capsys):
    desc = dedent("""\
    Please do not mess up this text!
    --------------------------------
       I have indented it
       exactly the way
       I want it
    """)
    help_verbose = "add some verbosity to the output"
    help_list = """\
    choose one:
      1) red
      2) green
      3) blue
    """
    help_one = """one
    line
    help
    """
    parser = argparse.ArgumentParser(
        description=desc,
        formatter_class=SmartFormatter,
    )
    parser.exit = exit
    parser.add_argument('--verbose', action='store_true',
                        help=help_verbose)
    parser.add_argument('--list', help='R|' + dedent(help_list))
    parser.add_argument('--oneline', action='store_true', help=help_one)
    parser.parse_args(['--help'])
    out, err = capsys.readouterr()
    full_help = dedent("""\
    usage: py.test [-h] [--verbose] [--list LIST] [--oneline]

    {0}
    optional arguments:
      -h, --help   show this help message and exit
      --verbose    {1}
      --list LIST  {2}
      --oneline    one line help
    """).format(
        desc, help_verbose,
        help_list.lstrip().replace('\n  ', '\n             ').rstrip(),
    )
    assert full_help == out


def test_argparse_default(capsys):
    desc = dedent("""\
    Please do not mess up this text!
    --------------------------------
       I have indented it
       exactly the way
       I want it
    """)
    help_verbose = "add some verbosity to the output"
    help_list = """\
    choose one:
      1) red
      2) green
      3) blue
    """
    help_one = """one
    line
    help
    """
    parser = argparse.ArgumentParser(
        description=desc,
        formatter_class=SmartFormatter,
    )
    parser.exit = exit
    # add  "D|" to the first option
    parser.add_argument('--verbose', action='store_true',
                        help='D|' + help_verbose)
    parser.add_argument('--list', help='R|' + dedent(help_list))
    parser.add_argument('--oneline', action='store_true', help=help_one)
    parser.parse_args(['--help'])
    out, err = capsys.readouterr()
    full_help = dedent("""\
    usage: py.test [-h] [--verbose] [--list LIST] [--oneline]

    {0}
    optional arguments:
      -h, --help   show this help message and exit
      --verbose    {1} (default: False)
      --list LIST  {2}
                    (default: None)
      --oneline    one line help (default: False)
    """).format(
        desc, help_verbose,
        help_list.lstrip().replace('\n  ', '\n             ').rstrip(),
    )
    assert full_help == out
