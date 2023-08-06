from setuptools import setup
import sys

from setuptools.command.test import test as TestCommand


__VERSION__ = '0.2.18'


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='flask_json_resource',
    version=__VERSION__,
    packages=['flask_json_resource', 'flask_json_resource.features'],
    package_data={
        'flask_json_resource': ['features/schemas/*.json']
    },
    long_description=open('./README.rst').read(),
    author='Ernst Odolphi',
    author_email='ernst.odolphi@gmail.com',
    install_requires=['flask', 'json_resource', 'flask-pymongo'],
    tests_require=['pytest>=2.6.0', 'pytest-bdd', 'requests'],
    cmdclass={'test': PyTest}
)




