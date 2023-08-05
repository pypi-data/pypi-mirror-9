import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

import siren_client

here = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()


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
    name='siren-client',
    version=siren_client.__version__,
    description='Client for a Siren based Hypermedia API',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: Apache Software License",
    ],
    author='Will Wheatley',
    author_email='will.wheatley@lonelyplanet.com.au',
    url='https://github.com/lonelyplanet/siren-client-python',
    keywords='siren hypermedia json',
    license='Apache 2.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=[],
    extras_require={
        'testing': ['pytest', 'mock', 'requests', 'simplejson'],
    },
    tests_require=['pytest', 'mock', 'requests', 'simplejson'],
    cmdclass={'test': PyTest},
)
