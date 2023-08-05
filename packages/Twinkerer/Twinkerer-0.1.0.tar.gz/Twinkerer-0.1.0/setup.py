# -*- coding:utf8 -*-
"""setup script
"""
import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(base_dir)

requires = [
    'Tinkerer',
    'twitter',
    'python-dateutil',
    'pytz',
]
test_requires = [
    'pytest',
]

classifiers = [
    'Programming Language :: Python',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

entry_points = {
    'console_scripts': [
        'twinker = twinkerer.cmd:main',
    ],
}


with open(os.path.join(base_dir, 'README.rst')) as f:
    readme = f.read()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        import pytest
        pytest.main(self.test_args)


setup(
    name='Twinkerer',
    version='0.1.0',
    description="tinkerer small extension to use twitter api.",
    long_description=readme,
    author='attakei',
    author_email='attakei@gmail.com',
    license='MIT License',
    url='https://github.com/attakei/twinkerer',
    classifiers=classifiers,

    install_requires=requires,
    tests_require=test_requires,

    test_suite='tests',

    packages=find_packages(),
    entry_points=entry_points,

    cmdclass = {'test': PyTest},
)
