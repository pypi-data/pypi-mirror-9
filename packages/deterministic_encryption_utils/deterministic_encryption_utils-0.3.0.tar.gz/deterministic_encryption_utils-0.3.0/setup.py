from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='deterministic_encryption_utils',
    version='0.3.0',
    description='Common encryption utilities for the implementation of simple encryption/decryption views.',
    long_description=long_description,
    url='https://github.com/seiferma/deterministic_encryption_utils',
    author='Stephan Seifermann',
    author_email='seiferma@t-online.de',
    license='MIT',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only'
    ],
    keywords='encryption view decryption library',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['pycrypto']
)
