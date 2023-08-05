import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

PKG_NAME = 'bade'

class PyTest(TestCommand):
    'Hook into py.test to run the test suite'
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


def include(*dirs):
    'Generate explicit mapping of asset -> destination for setuptools'
    results = []
    for src_dir in dirs:
        for root, _, files in os.walk(src_dir):
            results.append((os.path.join(PKG_NAME, root),
                            map(lambda f: os.path.join(root, f), files)))
    print(results)
    return results


def readme():
    'Dump out the readme'
    with open('README.rst') as readme_:
        return readme_.read()

setup(
    name=PKG_NAME,
    version='0.1.5',
    description='Micro-blogging with rST',
    data_files=include('templates'),
    packages=find_packages(),
    long_description=readme(),
    url='http://bmcorser.github.com/bade',
    author='bmcorser',
    author_email='bmcorser@gmail.com',
    install_requires=[
        'click',
        'docutils',
        'mako',
        'sass-cli',
        'pyyaml',
        'pygments',
    ],
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    entry_points='''
        [console_scripts]
        bade=bade.cli:main
    '''
)
