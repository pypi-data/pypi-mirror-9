import os
import sys
from setuptools import setup

version = '0.22'
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst')) as f:
    CHANGES = f.read()

requires = []
if sys.version_info[0] == 2 and sys.version_info[1] == 6:
    requires.append('weakrefset')

setup(
    name='GreenRocket',
    version=version,
    description='A simple and compact implementation '
                'of Observer design pattern',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords='signal observer publisher subscriber',
    author='Dmitry Vakhrushev',
    author_email='self@kr41.net',
    url='https://bitbucket.org/kr41/greenrocket',
    download_url='https://bitbucket.org/kr41/greenrocket/downloads',
    license='BSD',
    py_modules=['greenrocket'],
    install_requires=requires,
    zip_safe=True,
)
