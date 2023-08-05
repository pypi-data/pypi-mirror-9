import glob
import os
from os import path
from setuptools import setup, find_packages, Extension
import sys

REQUIRES = []
DESCRIPTION = 'rsync access for python'

# Note: In order to ship this you have to run the following
#       commands in order:
#
# 1. build the C files
#       python setup.py build_ext --inplace
# 2. build the distributable
#       python setup.py sdist
#       python setup.py bdist
# 3. upload the files
#       twine upload dist/...
#    or
#       python setup.py sdist upload
#       python setup.py bdist upload
#
precompiled_extensions = [
    Extension('rsync4python.rsync',
              sources=['rsync4python/rsync.c'],
              libraries=['rsync'])
]

extensions = None

try:
    from Cython.Build import cythonize
    from Cython.Distutils import build_ext

    cython_extensions = [
        Extension('rsync4python.rsync',
                  ['rsync4python/rsync.pyx'],
                  libraries=['rsync'])
    ]
    extensions = cythonize(cython_extensions)

except ImportError:
    extensions = precompiled_extensions


setup(
    name='rsync4python',
    version='0.2',
    description='rsync4python - {0}'.format(DESCRIPTION),
    license='Apache License 2.0',
    url='https://github.com/BenjamenMeyer/rsync4python',
    author='Rackspace',
    author_email='ben.meyer@rackspace.com',
    install_requires=REQUIRES,
    zip_safe=False,
    ext_modules=extensions,
    packages=find_packages(exclude=['tests',
                                    'rsync4python/tests*']),
    entry_points={
        'console_scripts': [
            'pyrdiff = rsync4python.shell:main',
        ]
    },
)
