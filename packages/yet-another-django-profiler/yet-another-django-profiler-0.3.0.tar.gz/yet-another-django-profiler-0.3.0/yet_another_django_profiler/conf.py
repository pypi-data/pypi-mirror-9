# encoding: utf-8
# Created by Jeremy Bowman on Fri Feb 21 11:15:41 EST 2014
# Copyright (c) 2014, 2015 Safari Books Online. All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE file for details.
"""
Custom Django settings for Yet Another Django Profiler middleware
"""

from __future__ import unicode_literals

import os
import re

from django.conf import settings as django_settings
from django.utils.functional import cached_property
from django.utils.importlib import import_module

DEFAULT_MODULE_PARENT_DIR_PATTERNS = [
    r'\.egg[/\\]',
    r'site-packages[/\\]',
    r'python\d+\.\d+[/\\]',
]


def path_to_module_name(path):
    """Get the fully qualified module name for the given absolute path by
    making intelligent guesses about the PYTHONPATH."""
    if path.endswith('.py'):
        path = path[:-3]
    cwd = os.getcwd()
    if path.startswith(cwd):
        path = path[len(cwd) + 1:]
    for pattern in settings.YADP_MODULE_PARENT_DIR_PATTERNS:
        match = True
        while match:
            match = re.search(pattern, path)
            if match:
                path = path[match.end():]
    path = path.replace('/', '.')
    path = path.replace('\\', '.')
    return path


class LazySettings(object):

    @property
    def YADP_ENABLED(self):
        return getattr(django_settings, 'YADP_ENABLED', django_settings.DEBUG)

    @property
    def YADP_FRACTION_PARAMETER(self):
        return getattr(django_settings, 'YADP_FRACTION_PARAMETER', 'fraction')

    @property
    def YADP_MAX_CALLS_PARAMETER(self):
        return getattr(django_settings, 'YADP_MAX_CALLS_PARAMETER', 'max_calls')

    @property
    def YADP_MODULE_PARENT_DIR_PATTERNS(self):
        return getattr(django_settings, 'YADP_MODULE_PARENT_DIR_PATTERNS',
                       DEFAULT_MODULE_PARENT_DIR_PATTERNS)

    @property
    def YADP_PATH_TO_MODULE_FUNCTION(self):
        return getattr(django_settings, 'YADP_PATH_TO_MODULE_FUNCTION',
                       'yet_another_django_profiler.conf.path_to_module_name')

    @property
    def YADP_PATTERN_PARAMETER(self):
        return getattr(django_settings, 'YADP_PATTERN_PARAMETER', 'pattern')

    @property
    def YADP_PROFILE_PARAMETER(self):
        return getattr(django_settings, 'YADP_PROFILE_PARAMETER', 'profile')

    @cached_property
    def path_to_module_function(self):
        """Resolve the function to use for converting paths to module names"""
        mod_name, function_name = self.YADP_PATH_TO_MODULE_FUNCTION.rsplit('.', 1)
        mod = import_module(mod_name)
        return getattr(mod, function_name)

settings = LazySettings()
