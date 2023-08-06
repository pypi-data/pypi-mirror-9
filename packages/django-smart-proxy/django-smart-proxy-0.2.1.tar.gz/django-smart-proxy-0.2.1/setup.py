# -*- coding: utf-8 -*-

import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

import smart_proxy

requirements = [
    'requests>=2',
]

if sys.version_info[:2] == (2, 6):
    requirements.append('Django>=1.4,<1.7')
elif sys.version_info[:2] == (2, 7):
    requirements.append('Django>=1.4,<1.7')
elif sys.version_info[0] == 3:
    requirements.append('Django>=1.7')

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
        name='django-smart-proxy',
        version=smart_proxy.__version__,
        install_requires=requirements,
        tests_require=['tox'],
        cmdclass={'test': ToxCommand},
        packages=['smart_proxy'],
        include_package_data = True,
        package_data = {
            '': ['AUTHORS.md', 'LICENSE.md', 'README.md'],
        },
        url='https://github.com/celerityweb/django-smart-proxy/',
        license='MIT - see LICENSE file',
        author='Matt Caldwell',
        author_email='matt.caldwell@gmail.com',
        description='The django-smart-proxy app allows you to configure '
                    'plug-and-play reverse proxy solutions for social networks '
                    'and other complex integration points with your website.',
        long_description=open('README.md').read(),
)
