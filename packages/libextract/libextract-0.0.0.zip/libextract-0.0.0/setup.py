import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = []

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


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='libextract',
    version='0.0.0',
    url='https://github.com/libextract/libextract',
    license='MIT',
    description='A ridiculously simple HT/XML article-text extractor',
    packages=['libextract'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'chardet>=2.3.0',
        'lxml>=3.4.0',
    ],
    keywords='extract extraction main article text html data-extraction data\
              content-extraction content unsupervised classification',
    author='Rodrigo Palacios, Eeo Jun',
    author_email='rodrigopala91@gmail.com, packwolf58@gmail.com',
    scripts=[],
    package_data={},
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
)
