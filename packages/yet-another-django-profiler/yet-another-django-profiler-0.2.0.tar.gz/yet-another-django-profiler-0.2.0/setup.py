# encoding: utf-8
# Created by Jeremy Bowman on Thu Feb 20 16:54:00 EST 2014
# Copyright (c) 2014 Safari Books Online. All rights reserved.
"""
yet-another-django-profiler setup script
"""

import os
from setuptools import setup

from yet_another_django_profiler import __version__

version = '.'.join(str(n) for n in __version__)

install_requires = [
    'Django',
]

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if on_rtd:
    from pip.download import PipSession
    from pip.index import PackageFinder
    from pip.req import parse_requirements
    session = PipSession()
    root_dir = os.path.abspath(os.path.dirname(__file__))
    requirements_path = os.path.join(root_dir, 'requirements', 'development.txt')
    finder = PackageFinder([], [], session=session)
    requirements = parse_requirements(requirements_path, finder, session=session)
    install_requires.extend([r.req for r in requirements])

setup(
    name='yet-another-django-profiler',
    version=version,
    author='Jeremy Bowman',
    author_email='jbowman@safaribooksonline.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
        'Topic :: Software Development',
    ],
    description='Django middleware for performance profiling directly from the browser',
    url='http://github.com/safarijv/yet-another-django-profiler',
    packages=[
        'yet_another_django_profiler',
    ],
    scripts=['gprof2dot.py'],
    zip_safe=True,
    install_requires=install_requires,
)
