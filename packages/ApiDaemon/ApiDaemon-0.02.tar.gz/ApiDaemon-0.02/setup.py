import os
import sys

py_version = sys.version_info[:2]
if py_version < (3, 4):
    raise RuntimeError('ApiDaemon requires Python 3.4 or later')

from setuptools import setup
here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except:
    README = """ Some readme must be here """
    CHANGES = ''

CLASSIFIERS = [
    'Natural Language :: English',
    'Operating System :: POSIX',
    "Programming Language :: Python :: 3.4",
]

dist = setup(
    name='ApiDaemon',
    version='0.02',
    license='MIT-license',
    url='https://github.com/tsyganov-ivan/ApiDaemon',
    description="Daemon for wraps any external APIs",
    long_description=README + '\n\n' + CHANGES,
    classifiers=CLASSIFIERS,
    author="Ivan Tsyganov",
    author_email="tsyganov.ivan@gmail.com",
    packages=['ApiDaemon'],
    install_requires=[
        'requests',
        'AsyncVk==1.0-alpha',
        'Click'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'apidaemon = ApiDaemon.runner:main'
        ],
    },
)
