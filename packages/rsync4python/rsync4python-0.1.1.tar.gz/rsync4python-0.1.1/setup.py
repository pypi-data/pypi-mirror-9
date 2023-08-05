import glob
import os
from os import path
from setuptools import setup, find_packages, Extension
import sys

REQUIRES = ['cython']
DESCRIPTION = 'rsync access for python'

from Cython.Build import cythonize
from Cython.Distutils import build_ext

setup(
    name='rsync4python',
    version='0.1.1',
    description='rsync4python - {0}'.format(DESCRIPTION),
    license='Apache License 2.0',
    url='https://github.com/BenjamenMeyer/rsync4python',
    author='Rackspace',
    author_email='ben.meyer@rackspace.com',
    install_requires=REQUIRES,
    zip_safe=False,
    cmdclass = {'build_ext': build_ext },
    ext_modules=cythonize([Extension('rsync4python.rsync', ['rsync4python/rsync.pyx'], libraries=['rsync'])]),
    packages=find_packages(exclude=['tests',
                                    'rsync4python/tests*']),
    entry_points={
        'console_scripts': [
            'pyrdiff = rsync4python.shell:main',
        ]
    },
)
