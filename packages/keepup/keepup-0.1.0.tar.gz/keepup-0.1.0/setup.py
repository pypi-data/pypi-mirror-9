import os
import sys
from setuptools import setup

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

if sys.version_info[:2] < (3,):
    sys.exit('keepup requires Python 3 or higher.')

setup(
    name='keepup',
    version='0.1.0',
    description='Keep a defined set of tasks running',
    long_description=read('README.rst'),
    url='https://github.com/parryjacob/keepup',
    license='MIT',
    author='Jacob Parry',
    author_email='jacob@jacobparry.ca',
    scripts=['keepup'],
    include_package_data=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Console :: Curses',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: System :: Systems Administration',
    ],
    install_requires=['npyscreen',]
)