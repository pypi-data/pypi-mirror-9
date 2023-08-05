# coding: utf-8
# Copyright Ruamel bvba 2007-2014


from __future__ import print_function

import sys
import pytest

try:
    from ruamel.std.argparse import ProgramBase, option, sub_parser, version
except ImportError:
    print("you have to install ruamel.std.argparse to run the tests")


class Program(ProgramBase):
    def __init__(self):
        # super(Program, self).__init__(
        #     formatter_class=SmartFormatter
        # )
        ProgramBase.__init__(self)

    def run(self):
        print('here', self._args.func)
        if self._args.func:
            return self._args.func()

    # you can put these options on __init__, but if Program is going
    # to be subclassed, there will be another __init__ scanned
    # in ProgramBase.__init__ than the one decorated here
    # defensive is to use a differently named option or the special _pb_init
    @option('--verbose', global_option=True, action='store_true')
    @option('--quiet', action='store_true')
    # @option('--version', action='version', version='version: 42')
    @version('version: 42')
    def _pb_init(self):
        pass

    @sub_parser(help="call mercurial")
    @option('--show', action='store_true')
    @option('--no-show', help='do not show', metavar='NSHO')
    @option('file-name', nargs='*')
    def hg(self):
        pass

    # have to define hg.sub_parser after creating sub_parser
    @hg.sub_parser(help='check something')
    @option('--extra')
    def check(self):
        pass

    @check.sub_parser(help='check something')
    def lablab(self):
        pass

    @check.sub_parser(help='check something')
    def k(self):
        print('doing k')

    @check.sub_parser(help='check something')
    def m(self):
        pass

    @sub_parser(help="call git")
    def git(self):
        print('doing git')

    @git.sub_parser('abc')
    @option('--extra')
    def just_some_name(self):
        print('doing just_some_name/abc')

    @git.sub_parser('hihi', help='helphelp')
    def hki(self):
        pass

    @hki.sub_parser('oops')
    def oops(self):
        print('doing oops')

    @sub_parser(help="call a")
    def a(self):
        pass

    @sub_parser(help="call b")
    def b(self):
        pass

    @sub_parser(help="call c")
    def c(self):
        pass

    @sub_parser(help="call d")
    def d(self):
        pass

    # on purpose not in "right" order
    @sub_parser(help="call f")
    def f(self):
        print('doing f')

    @sub_parser(help="call e")
    def e(self):
        pass

    # @sub_parser('svn')
    # def subversion(self):
    #     pass


class ParseHelpOutput:
    def __init__(self, capsys, error=False):
        self._capsys = capsys
        out, err = self._capsys.readouterr()
        o = err if error else out
        self(o)

    def __call__(self, out):
        print(out)
        print('+++++')
        self._chunks = {}
        chunk = None
        for line in out.splitlines():
            lsplit = line.split()
            chunk_name = None
            if lsplit and lsplit[0][-1] == ':':
                chunk_name = lsplit[0]
                line = line.split(':', 1)[1]
            if line and line[-1] == ':':
                chunk_name = line
            if chunk_name:
                chunk_name = chunk_name[:-1]
                chunk = self._chunks.setdefault(chunk_name, [])
            if chunk is None or not line.strip():
                continue
            chunk.append(line)
        print('chunks', self._chunks)
        if not self._chunks:
            print('stderr', err)

    def start(self, chunk, s, strip=True):
        """check if a stripped line in the chunk text starts with s"""
        for l in self._chunks[chunk]:
            if l.lstrip().startswith(s):
                return True
        return False

    def somewhere(self, chunk, s, strip=True):
        """check if s is somewhere in the chunk"""
        for l in self._chunks[chunk]:
            if s in l:
                return True
        return False


@pytest.fixture(scope='class')
def program():
    return Program()


class TestProgram:
    def test_help(self, capsys, program):
        with pytest.raises(SystemExit):
            program._parse_args('-h'.split())
        pho = ParseHelpOutput(capsys)
        assert pho.start('positional arguments', 'hg')
        if sys.version_info[:2] == (2, 6):
            # 2.6 argparse scrambles order
            assert pho.somewhere('usage', 'git,e,d,f')
        else:
            assert pho.somewhere('usage', 'c,d,f,e')
        assert pho.start('optional arguments', '--verbose')

    def test_help_sub_parser(self, capsys, program):
        with pytest.raises(SystemExit):
            program._parse_args('hg -h'.split())
        pho = ParseHelpOutput(capsys)
        assert pho.start('positional arguments', 'file-name')
        assert pho.start('optional arguments', '--verbose')
        assert not pho.start('optional arguments', '--extra')

    def test_sub_sub_parser(self, capsys, program):
        with pytest.raises(SystemExit):
            program._parse_args('hg check -h'.split())
        pho = ParseHelpOutput(capsys)
        # assert not pho.start('positional arguments', 'file-name')
        # assert not pho.start('positional arguments', 'hg')
        assert pho.start('optional arguments', '--extra')
        assert pho.start('optional arguments', '--verbose')

    def test_git_help_sub_parser(self, capsys, program):
        with pytest.raises(SystemExit):
            program._parse_args('git -h'.split())
        pho = ParseHelpOutput(capsys)
        assert pho.start('optional arguments', '--verbose')
        assert not pho.start('optional arguments', '--extra')

    def test_git_sub_sub_parser(self, capsys, program):
        with pytest.raises(SystemExit):
            program._parse_args('git abc -h'.split())
        pho = ParseHelpOutput(capsys)
        assert pho.start('optional arguments', '--extra')
        assert pho.start('optional arguments', '--verbose')

    def test_git_sub_sub_sub_parser(self, capsys, program):
        with pytest.raises(SystemExit):
            program._parse_args('git hihi oops -h'.split())
        pho = ParseHelpOutput(capsys)
        assert pho.start('usage', 'py.test git hihi oops')
        assert pho.start('optional arguments', '--verbose')

    def test_version(self, capsys, program):
        with pytest.raises(SystemExit):
            program._parse_args('--version'.split())
        pho = ParseHelpOutput(capsys, error=sys.version_info < (3, 4))
        assert pho.start('version', '42')

if __name__ == '__main__':
    p = Program()
    p._parse_args()
    p.run()
