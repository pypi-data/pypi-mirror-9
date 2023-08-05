# encoding: utf-8
# Created by Jeremy Bowman on Fri Feb 21 11:16:36 EST 2014
# Copyright (c) 2014 Safari Books Online. All rights reserved.
"""
Yet Another Django Profiler middleware implementation
"""

import cProfile
from cStringIO import StringIO
import marshal
import os
import pstats
import subprocess
import tempfile

from django.core.exceptions import MiddlewareNotUsed

from .conf import settings


def text_response(response, content):
    """Return a plain text message as the response content."""
    response.content = content
    response['Content-type'] = 'text/plain'
    return response


def which(program):
    """Return the path of the named program in the PATH, or None if no such
    executable program can be found  Used to make sure that required binaries
    are in place before attempting to call them."""

    def is_exe(file_path):
        return os.path.isfile(file_path) and os.access(file_path, os.X_OK)

    program_path, _name = os.path.split(program)
    if program_path:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


class ProfilerMiddleware(object):
    """
    Code profiling middleware which can display either a call graph PDF or
    a table of called functions ordered by the desired statistic.  For the call
    graph, just append "?profile" to the URL.  For the graph generation to
    work, install Graphviz from http://www.graphviz.org/Download.php

    For a statistics table, use the statistic you want to sort by as the
    parameter (such as "?profile=time").  Sorting options include:

    * calls (call count)
    * cumulative (cumulative time)
    * file (file name)
    * module (file name)
    * pcalls (primitive call count)
    * line (line number)
    * name (function name)
    * nfl (name/file/line)
    * stdname (standard name)
    * time (internal time)

    Additional parameters can be added when generating a statistics table:

    * fraction - The fraction of total function calls to display (the default of .2 is omitted if lines or filter are specified)
    * max_calls - The maximum number of function calls to display
    * pattern - Regular expression filter for function display names

    To get these instructions in the app if you forget the usage options, use
    "?profile=help" in the URL.

    Inspiration:

    * https://gist.github.com/kesor/1229681
    * https://bitbucket.org/brodie/geordi
    """

    def __init__(self):
        if not settings.YADP_ENABLED:
            # Disable the middleware completely when YADP_ENABLED = False
            raise MiddlewareNotUsed()
        self.profiler = None

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if settings.YADP_ENABLED and (settings.YADP_PROFILE_PARAMETER in request.REQUEST):
            self.profiler = cProfile.Profile()
            args = (request,) + callback_args
            return self.profiler.runcall(callback, *args, **callback_kwargs)

    def process_response(self, request, response):
        if settings.YADP_ENABLED and settings.YADP_PROFILE_PARAMETER in request.REQUEST:
            self.profiler.create_stats()
            mode = request.REQUEST[settings.YADP_PROFILE_PARAMETER]
            if not mode:
                if not which('dot'):
                    return text_response(response, 'Could not find "dot" from Graphviz; please install Graphviz to enable call graph generation')
                if not which('gprof2dot.py'):
                    return text_response(response, 'Could not find gprof2dot.py, which should have been installed by yet-another-django-profiler')
                with tempfile.NamedTemporaryFile() as stats:
                    stats.write(marshal.dumps(self.profiler.stats))
                    stats.flush()
                    cmd = ('gprof2dot.py -f pstats {} | dot -Tpdf'.format(stats.name))
                    process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE)
                    output = process.communicate()[0]
                    return_code = process.poll()
                    if return_code:
                        raise Exception('gprof2dot/dot exited with {}'.format(return_code))
                response.content = output
                response['Content-Type'] = 'application/pdf'
                return response
            elif mode == 'help':
                return text_response(response, ProfilerMiddleware.__doc__)
            else:
                out = StringIO()
                stats = pstats.Stats(self.profiler, stream=out)
                restrictions = []
                if settings.YADP_PATTERN_PARAMETER in request.REQUEST:
                    restrictions.append(request.REQUEST[settings.YADP_PATTERN_PARAMETER])
                if settings.YADP_FRACTION_PARAMETER in request.REQUEST:
                    restrictions.append(float(request.REQUEST[settings.YADP_FRACTION_PARAMETER]))
                elif settings.YADP_MAX_CALLS_PARAMETER in request.REQUEST:
                    restrictions.append(int(request.REQUEST[settings.YADP_MAX_CALLS_PARAMETER]))
                elif settings.YADP_PATTERN_PARAMETER not in request.REQUEST:
                    restrictions.append(.2)
                stats.sort_stats(mode).print_stats(*restrictions)
                return text_response(response, out.getvalue())
        return response
