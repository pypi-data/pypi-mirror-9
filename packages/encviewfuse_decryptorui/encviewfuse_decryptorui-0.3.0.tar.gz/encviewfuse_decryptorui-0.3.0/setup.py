from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='encviewfuse_decryptorui',
    version='0.3.0',
    description='A UI for decrypting directories and files encrypted with encviewfuse_decryptorui.',
    long_description=long_description,
    url='https://github.com/seiferma/encviewfuse_decryptorui',
    author='Stephan Seifermann',
    author_email='seiferma@t-online.de',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Security :: Cryptography',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only'
    ],
    keywords='decryption ui',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['hurry.filesize', 'deterministic_encryption_utils'],
    entry_points={
        'console_scripts': [
            'encviewfuse_decryptionui=encviewfuse_decryptorui.decryptorui.DecryptionUI:main'
        ],
    },
)
