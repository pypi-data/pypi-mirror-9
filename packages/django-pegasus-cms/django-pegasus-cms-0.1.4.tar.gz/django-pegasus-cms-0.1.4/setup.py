# -*- coding: utf-8 -*-

import sys

from pip.req import parse_requirements
from setuptools import setup
from setuptools.command.test import test as TestCommand

import pegasus
import pip

try:
    parsed_reqs = list(parse_requirements('requirements.txt'))
except TypeError:
    parsed_reqs = parse_requirements('requirements.txt',
                                     session=pip.download.PipSession())

requirements = [str(ir.req) for ir in parsed_reqs]


class ToxCommand(TestCommand):
    user_options = [('tox-args=', 'a', 'Arguments to pass to tox.')]
    def initialize_options(self):
        super(ToxCommand, self).initialize_options()
        self.tox_args = None

    def finalize_options(self):
        super(ToxCommand, self).finalize_options()
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox
        import shlex
        if self.tox_args:
            errno = tox.cmdline(args=shlex.split(self.tox_args))
        else:
            errno = tox.cmdline()
        sys.exit(errno)

setup(
        name='django-pegasus-cms',
        version=pegasus.__version__,
        install_requires=requirements,
        tests_require=['tox'],
        cmdclass={'test': ToxCommand},
        packages=['pegasus'],
        include_package_data = True,
        package_data = {
            '': ['AUTHORS.md', 'LICENSE.md', 'README.md'],
        },
        url='https://github.com/celerityweb/django-pegasus-cms/',
        license='MIT - see LICENSE file',
        author='Matt Caldwell',
        author_email='matt.caldwell@gmail.com',
        description='tbd'
                    'tbd',
        long_description=open('README.md').read(),
)
