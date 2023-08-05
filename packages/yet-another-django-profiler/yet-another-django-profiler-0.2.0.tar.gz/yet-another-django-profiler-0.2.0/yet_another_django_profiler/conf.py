# encoding: utf-8
# Created by Jeremy Bowman on Fri Feb 21 11:15:41 EST 2014
# Copyright (c) 2014 Safari Books Online. All rights reserved.
"""
Custom Django settings for Yet Another Django Profiler middleware
"""

from django.conf import settings as django_settings


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
    def YADP_PATTERN_PARAMETER(self):
        return getattr(django_settings, 'YADP_PATTERN_PARAMETER', 'pattern')

    @property
    def YADP_PROFILE_PARAMETER(self):
        return getattr(django_settings, 'YADP_PROFILE_PARAMETER', 'profile')

settings = LazySettings()
