from setuptools import setup, find_packages

name = 'cconfig'
version = '0.1.0'

setup(
    name=name,
    version=version,
    author='Steven Armstrong',
    author_email='steven-%s@armstrong.cc' % name,
    url='http://github.com/asteven/%s/' % name,
    description='cconfig implementation for python',
    packages=find_packages(),
)
