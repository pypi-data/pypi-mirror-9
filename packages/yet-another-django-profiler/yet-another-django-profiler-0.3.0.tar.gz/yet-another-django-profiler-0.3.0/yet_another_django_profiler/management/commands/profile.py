# encoding: utf-8
# Created by Jeremy Bowman on Fri Feb 21 11:16:36 EST 2014
# Copyright (c) 2014, 2015 Safari Books Online. All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE file for details.
"""
Yet Another Django Profiler "profile" management command
"""

from __future__ import unicode_literals

import atexit
import cProfile
from cStringIO import StringIO
import marshal
import mock
from optparse import make_option
import pstats
import subprocess
import sys
import tempfile

from django.conf import settings
from django.core.management import call_command, ManagementUtility
from django.core.management.base import BaseCommand

from yet_another_django_profiler.middleware import func_strip_path, which


class Command(BaseCommand):
    """
    Django management command for profiling other management commands.
    """
    args = 'other_command <argument argument ...>'
    help = 'Profile another Django management command'
    custom_options = (
        make_option(
            '-o',
            '--output',
            dest='path',
            help='Path to a file in which to store the profiling output (required if generating a call graph PDF, other results are output to the console by default)'
        ),
        make_option(
            '-s',
            '--sort',
            dest='sort',
            help='Statistic by which to sort the profiling data (default is to generate a call graph PDF instead)'
        ),
        make_option(
            '-f',
            '--fraction',
            dest='fraction',
            help='The fraction of total function calls to display (the default of .2 is omitted if max-calls or pattern are specified)'
        ),
        make_option(
            '-m',
            '--max-calls',
            dest='max_calls',
            help='The maximum number of function calls to display'
        ),
        make_option(
            '-p',
            '--pattern',
            dest='pattern',
            help='Regular expression filter for function display names'
        )
    )
    option_list = BaseCommand.option_list + custom_options

    def create_parser(self, prog_name, subcommand):
        """
        Override the base create_parser() method to ignore options of the
        command being profiled.
        """
        parser = super(Command, self).create_parser(prog_name, subcommand)
        parser.disable_interspersed_args()
        return parser

    def handle(self, *args, **options):
        """
        Run and profile the specified management command with the provided
        arguments.
        """
        if not len(args):
            self.print_help(sys.argv[0], 'profile')
            sys.exit(1)
        if not options['sort'] and not options['path']:
            self.stdout.write('Output file path is required for call graph generation')
            sys.exit(1)

        command_name = args[0]
        utility = ManagementUtility(sys.argv)
        command = utility.fetch_command(command_name)
        parser = command.create_parser(sys.argv[0], command_name)
        command_options, command_args = parser.parse_args(list(args[1:]))

        if command_name == 'test' and settings.TEST_RUNNER == 'django_nose.NoseTestSuiteRunner':
            # Ugly hack: make it so django-nose won't have nosetests choke on
            # our parameters
            BaseCommand.option_list += self.custom_options

        profiler = cProfile.Profile()
        atexit.register(output_results, profiler, options, self.stdout)
        profiler.runcall(call_command, command_name, *command_args, **command_options.__dict__)
        sys.exit(0)


def output_results(profiler, options, stdout):
    """Generate the profiler output in the desired format.  Implemented as a
    separate function so it can be run as an exit handler (because management
    commands often call exit() directly, bypassing the rest of the profile
    command's handle() method)."""
    profiler.create_stats()

    if not options['sort']:
        if not which('dot'):
            stdout.write('Could not find "dot" from Graphviz; please install Graphviz to enable call graph generation')
            return
        if not which('gprof2dot.py'):
            stdout.write('Could not find gprof2dot.py, which should have been installed by yet-another-django-profiler')
            return
        with tempfile.NamedTemporaryFile() as stats:
            stats.write(marshal.dumps(profiler.stats))
            stats.flush()
            cmd = ('gprof2dot.py -f pstats {} | dot -Tpdf'.format(stats.name))
            process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE)
            output = process.communicate()[0]
            return_code = process.poll()
            if return_code:
                stdout.write('gprof2dot/dot exited with {}'.format(return_code))
                return
            path = options['path']
            with open(path, 'wb') as pdf_file:
                pdf_file.write(output)
                stdout.write('Wrote call graph to {}'.format(path))
    else:
        sort = options['sort']
        if sort == 'file':
            # Work around bug on Python versions >= 2.7.4
            sort = 'fil'
        out = StringIO()
        stats = pstats.Stats(profiler, stream=out)
        with mock.patch('pstats.func_strip_path') as mock_func_strip_path:
            mock_func_strip_path.side_effect = func_strip_path
            stats.strip_dirs()
        restrictions = []
        if options['pattern']:
            restrictions.append(options['pattern'])
        if options['fraction']:
            restrictions.append(float(options['fraction']))
        elif options['max_calls']:
            restrictions.append(int(options['max_calls']))
        elif not options['pattern']:
            restrictions.append(.2)
        stats.sort_stats(sort).print_stats(*restrictions)
        if options['path']:
            path = options['path']
            with open(path, 'w') as text_file:
                text_file.write(out.getvalue())
                stdout.write('Wrote profiling statistics to {}'.format(path))
        else:
            stdout.write(out.getvalue())
