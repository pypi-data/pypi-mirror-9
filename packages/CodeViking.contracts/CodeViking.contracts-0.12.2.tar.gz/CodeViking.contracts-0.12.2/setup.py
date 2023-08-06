import sys

from setuptools import setup
# noinspection PyPep8Naming
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='CodeViking.contracts',
    version='0.12.2',
    namespace_packages=['codeviking'],
    url='https://bitbucket.org/codeviking/python-codeviking.contracts/',
    author='Dan Bullok',
    author_email='opensource@codeviking.com',
    description='Function and method call contracts',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    platforms='any',
    packages=['codeviking.contracts'],
    license="MIT",
    tests_require=['pytest'],
    cmdclass={'test': PyTest}
)
