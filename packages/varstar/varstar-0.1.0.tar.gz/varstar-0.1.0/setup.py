from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

INSTALL_REQUIRES = ['numpy', 'matplotlib', 'scipy']

setup(
    name='varstar',
    version='0.1.0',
    description='Utilities for analyzing variable star data',
    url='http://github.com/mwcraig/varstar',
    long_description=(open('README.rst').read()),
    license='BSD 3-clause',
    author='Matt Craig',
    author_email='mcraig@mnstate.edu',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    extras_require={
        'docs': ['numpydoc', 'sphinx-argparse', 'sphinx_rtd_theme', 'astropy-helpers'],
    },
    tests_require=['scipy', 'pytest>1.4', 'pytest-capturelog'] + INSTALL_REQUIRES,
    cmdclass={'test': PyTest},
    entry_points={
    },
    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: BSD License',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Intended Audience :: Science/Research',
                 'Topic :: Scientific/Engineering :: Astronomy'],
    )
