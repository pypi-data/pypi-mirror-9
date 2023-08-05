# coding: utf-8
from setuptools import setup, Command
import unittest


class RunTests(Command):
    """New setup.py command to run all tests for the package.
    """
    description = "run all tests for the package"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        tests = unittest.TestLoader().discover('test')
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(tests)

setup(
    name='urllib2_prior_auth',
    version="0.2.0",
    license="BSD",
    description='Module resolving http://bugs.python.org/issue19494',
    author=u'Matěj Cepl',
    author_email='mcepl@cepl.eu',
    url='https://gitlab.com/mcepl/urllib2_prior_auth',
    py_modules=['urllib2_prior_auth'],
    keywords=['urllib2', 'authorization', 'unittest'],
    cmdclass={
        'test': RunTests,
    },
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
    ]
)
