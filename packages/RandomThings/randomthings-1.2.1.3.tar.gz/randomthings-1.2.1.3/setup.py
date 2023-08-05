#from distutils.core import setup
from setuptools import setup,find_packages
from setuptools.command.test import test as TestCommand
import sys

class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        errno = tox.cmdline(args=shlex.split(self.tox_args))
        sys.exit(errno)

setup(
    name='randomthings',
    version='1.2.1.3',
    description='Generate Random Things',
    author='kajigga',
    author_email='kajigga@gmail.com',
    url='https://bitbucket.org/kajigga/py_randomthings',
    packages=find_packages(),
    #packages=['random_things','random_things.random_sources'],
    #package_dir={'random_things':'random_things'},
    package_data={'random_things':['names_csv/*.csv']},
    #test_suite='tests',
    #tests_require=['tox'],
    #cmdclass = {'test': Tox},
)
