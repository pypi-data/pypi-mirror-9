from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys
import browler


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name='browler',
    version=browler.__version__,
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    packages=['browler'],
    url='https://github.com/brady-vitrano/browler',
    install_requires=[
        'redis==2.10.3',
        'splinter==0.7.0'
    ],
    platforms=['any'],
    license='MIT',
    author='brady-vitrano',
    author_email='bjvitrano@gmail.com',
    description='Selenium Based Web Crawler',
    include_package_data=True,
    extras_require={
        'testing': ['pytest'],
    },
    #entry_points={
    #    'console_scripts': ['crawler=crawler.command_line:main'],
    #},
    zip_safe=False
)
