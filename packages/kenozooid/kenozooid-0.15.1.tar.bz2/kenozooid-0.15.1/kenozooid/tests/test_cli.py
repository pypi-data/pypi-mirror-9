#
# Kenozooid - dive planning and analysis toolbox.
#
# Copyright (C) 2009-2014 by Artur Wroblewski <wrobell@pld-linux.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Test command line routines.
"""

from io import BytesIO
import argparse

from kenozooid.cli.logbook import _name_parse
from kenozooid.cli import add_uddf_input, add_commands, CLICommand
from kenozooid.component import _registry, inject

import unittest

class NameParseTestCase(unittest.TestCase):
    """
    Name parsing tests.
    """
    def test_name(self):
        """
        Test parsing name
        """
        f, m, l = _name_parse('Tom Cora')
        self.assertEquals('Tom', f)
        self.assertTrue(m is None)
        self.assertEquals('Cora', l)
            

    def test_name_middle(self):
        """
        Test parsing name with middle name
        """
        f, m, l = _name_parse('Thomas Henry Corra')
        self.assertEquals('Thomas', f)
        self.assertEquals('Henry', m)
        self.assertEquals('Corra', l)


    def test_name_last(self):
        """
        Test parsing name with lastname first
        """
        f, m, l = _name_parse('Corra, Thomas Henry')
        self.assertEquals('Thomas', f)
        self.assertEquals('Henry', m)
        self.assertEquals('Corra', l)


    def test_name_first(self):
        """
        Test parsing just first name
        """
        f, m, l = _name_parse('Tom')
        self.assertEquals('Tom', f)
        self.assertTrue(m is None)
        self.assertTrue(l is None)



class UDDFInputActionTestCase(unittest.TestCase):
    """
    Tests for parsing arguments being a list of UDDF input files.
    """
    def setUp(self):
        """
        Create argument parser for tests.
        """
        parser = self.parser = argparse.ArgumentParser()
        parser.__no_f_check__ = True
        add_uddf_input(parser)


    def test_single(self):
        """
        Test parsing arguments being a list of UDDF input files (single)
        """
        self.parser.add_argument('output')

        args = self.parser.parse_args(args=['f1', 'out'])
        self.assertEquals(([None], ['f1']), args.input)
        self.assertEquals('out', args.output)


    def test_multiple(self):
        """
        Test parsing arguments being a list of UDDF input files (multiple)
        """
        self.parser.add_argument('output')

        args = self.parser.parse_args(args=['f1', 'f2', 'out'])
        self.assertEquals(([None, None], ['f1', 'f2']), args.input)
        self.assertEquals('out', args.output)


    def test_opt_only(self):
        """
        Test parsing arguments being a list of UDDF input files (options only)
        """
        self.parser.add_argument('output')

        args = self.parser.parse_args(args=['-k', '2-3', 'f1', 'out'])
        self.assertEquals((['2-3'], ['f1']), args.input)
        self.assertEquals('out', args.output)

        args = self.parser.parse_args(args=['-k', '2-3', 'f1', '-k', '3-4', 'f2', 'out'])
        self.assertEquals((['2-3', '3-4'], ['f1', 'f2']), args.input)
        self.assertEquals('out', args.output)


    def test_opt_first(self):
        """
        Test parsing arguments being a list of UDDF input files (options first)
        """
        self.parser.add_argument('output')

        args = self.parser.parse_args(args=['-k', '2-3', 'f1', 'f2', 'out'])
        self.assertEquals((['2-3', None], ['f1', 'f2']), args.input)
        self.assertEquals('out', args.output)


    def test_opt_last(self):
        """
        Test parsing arguments being a list of UDDF input files (options last)
        """
        self.parser.add_argument('output')

        args = self.parser.parse_args(args=['f2', '-k', '2-3', 'f1', 'out'])
        self.assertEquals(([None, '2-3'], ['f2', 'f1']), args.input)
        self.assertEquals('out', args.output)



class CommandTestCase(unittest.TestCase):
    """
    CLI commands and subcommands parsing tests.
    """
    def tearDown(self):
        """
        Clear interface registry after each test.
        """
        _registry.clear()


    def test_simple_command(self):
        """
        Test CLI simple command parsing
        """
        @inject(CLICommand, name='test')
        class Test(object):
            description = 'test description'

            @classmethod
            def add_arguments(self, parser):
                pass

            def __call__(self, args):
                pass

        parser = argparse.ArgumentParser()
        add_commands(parser)

        args = parser.parse_args('test'.split())
        self.assertTrue(hasattr(args, 'cmd'))
        self.assertTrue(hasattr(args, 'subcmd'))
        self.assertTrue(hasattr(args, 'parser'))
        self.assertEquals('test', args.cmd)
        self.assertEquals('test', args.subcmd)


    def test_complex_command(self):
        """
        Test CLI command and subcommand parsing
        """
        @inject(CLICommand, name='test', master=True)
        class Test(object):
            description = 'test description'
            title = None

            @classmethod
            def add_arguments(self, parser):
                pass

            def __call__(self, args):
                pass


        @inject(CLICommand, name='test a')
        class TestA(object):
            description = 'test a description'
            title = None

            @classmethod
            def add_arguments(self, parser):
                pass

            def __call__(self, args):
                pass


        @inject(CLICommand, name='test b')
        class TestB(object):
            description = 'test b description'
            title = None

            @classmethod
            def add_arguments(self, parser):
                pass

            def __call__(self, args):
                pass

        parser = argparse.ArgumentParser()
        add_commands(parser)

        args = parser.parse_args('test'.split())
        self.assertTrue(hasattr(args, 'cmd'))
        self.assertTrue(hasattr(args, 'subcmd'))
        self.assertTrue(hasattr(args, 'parser'))
        self.assertEquals('test', args.cmd, args)
        self.assertIsNone(args.subcmd, args)

        args = parser.parse_args('test a'.split())
        self.assertTrue(hasattr(args, 'cmd'))
        self.assertTrue(hasattr(args, 'subcmd'))
        self.assertTrue(hasattr(args, 'parser'))
        self.assertEquals('test', args.cmd, args)
        self.assertEquals('a', args.subcmd, args)

        args = parser.parse_args('test b'.split())
        self.assertTrue(hasattr(args, 'cmd'))
        self.assertTrue(hasattr(args, 'subcmd'))
        self.assertTrue(hasattr(args, 'parser'))
        self.assertEquals('test', args.cmd, args)
        self.assertEquals('b', args.subcmd, args)


# vim: sw=4:et:ai
