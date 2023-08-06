# coding: utf-8
import os.path
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

import dbsync


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

extra_requirements = []
if sys.version_info < (3, 2):
    extra_requirements.append('futures')

here = os.path.dirname(__file__)
readme_path = os.path.join(here, 'README.md')
readme = open(readme_path).read()

setup(
    name='DBSync',
    version=dbsync.release,
    description='Sync database to hadoop',
    long_description=readme,
    author='Bangtao Zhou',
    author_email='zhoubangtao@163.com',
    url='http://github.com/zhoubangtao/dbsync',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ],
    keywords='sync hive hadoop mysql mongodb',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    install_requires=['setuptools >= 0.7', 'six >= 1.4.0', 'pytz', 'tzlocal', ''] + extra_requirements,
    tests_require=['pytest >= 2.5.1'],
    cmdclass={'test': PyTest},
    zip_safe=False,
    scripts=[],
    entry_points={
    }
)
