from os.path import join, dirname

from setuptools import setup, find_packages

from version import get_version

setup(
    name='libarchive-c',
    version=get_version(),
    description='Python interface to libarchive',
    author='Changaco',
    author_email='changaco@changaco.oy.lc',
    url='https://github.com/Changaco/python-libarchive-c',
    license='LGPLv2+',
    packages=find_packages(exclude=['tests']),
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    keywords='archive libarchive 7z tar bz2 zip gz',
)
