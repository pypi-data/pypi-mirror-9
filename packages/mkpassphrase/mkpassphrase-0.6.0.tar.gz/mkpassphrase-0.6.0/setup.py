import sys

from setuptools import setup
from setuptools.command.test import test

import mkpassphrase


class PyTest(test):

    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

kw = {}
if sys.version_info >= (3,):
    kw['use_2to3'] = True

setup(
    name=mkpassphrase.__name__,
    version=mkpassphrase.__version__,
    license='http://www.opensource.org/licenses/mit-license.php',
    url='https://github.com/eukaryote/mkpassphrase',
    description='Word-based passphrase generator',
    long_description=(
        'A commandline script and an associated package for'
        ' generating natural-language passphrases by sampling from a large'
        ' dictionary file containing one word per line, yielding a passphrase'
        ' like "Snack cachets Duds Corey".'),
    keywords='passphrase password',
    author='Calvin Smith',
    author_email='sapientdust+mkpassphrase@gmail.com',
    packages=[mkpassphrase.__name__],
    platforms='any',
    cmdclass={'test': PyTest},
    tests_require=['pytest'],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            '{name} = {name}.main:main'.format(name=mkpassphrase.__name__),
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Development Status :: 4 - Beta',
        'Topic :: Security',
        'Topic :: Utilities'
    ],
    **kw
)
