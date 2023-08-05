import sys
import os

from setuptools import setup
from setuptools.command.test import test

import mkpassphrase

here_dir = os.path.abspath(os.path.dirname(__file__))


def read(*filenames):
    buf = []
    for filename in filenames:
        with open(os.path.join(here_dir, filename)) as f:
            buf.append(f.read())
    return '\n\n'.join(buf)


class PyTest(test):

    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


def remove_build_link(text):
    # pypi puts rel="nofollow" on the link surrounding the build image,
    # which causes the browser to not follow the image and to display a
    # broken image icon instead, so we filter the link and just show the image
    import re
    regex = '\s*:target: //travis-ci\.org/[^\n]*'
    return re.sub(regex, '', text, count=1)


setup(
    name=mkpassphrase.__name__,
    version=mkpassphrase.__version__,
    license='http://www.opensource.org/licenses/mit-license.php',
    url='https://github.com/eukaryote/mkpassphrase',
    description='Word-based passphrase generator',
    long_description=remove_build_link(read('README.rst', 'CHANGES.rst')),
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
)
