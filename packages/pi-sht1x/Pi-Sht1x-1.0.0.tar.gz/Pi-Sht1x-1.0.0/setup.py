__author__ = 'Doug Rohm'
import re
import ast
from os import path
from setuptools import setup


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('pi_sht1x/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(f.read().decode('utf-8')).group(1)))

classifiers = ['Development Status :: 5 - Production/Stable',
               'Operating System :: POSIX :: Linux',
               'License :: OSI Approved :: MIT License',
               'Intended Audience :: Developers',
               'Programming Language :: Python :: 3',
               'Topic :: Software Development',
               'Topic :: Utilities']

setup(
    name='Pi-Sht1x',
    version=version,
    url='https://bitbucket.org/drohm/pi-sht1x',
    license='MIT',
    author=__author__,
    author_email='pypi@drohm.sent.com',
    description='Python library for the Sensirion SHT1x series of temperature & humidity sensors for the Raspberry Pi.',
    long_description=long_description,
    include_package_data=True,
    packages=['pi_sht1x', 'examples'],
    install_requires=[
        'RPi.GPIO>=0.5.11',
    ],
    classifiers=classifiers,
)
