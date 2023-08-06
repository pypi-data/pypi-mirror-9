# coding:utf-8

from setuptools import setup, find_packages

long_description = """\
DB client.

See detail @ http://github.com/tomokinakamaru/sqlew.

Copyright (c) 2015, Tomoki Nakamaru.

License: MIT
"""

setup(
    author='Tomoki Nakamaru',
    author_email='tomoki.nakamaru@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Database :: Front-Ends",
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    description='db client',
    license='MIT',
    long_description=long_description,
    name='sqlew',
    packages=find_packages(),
    platforms='any',
    url='http://github.com/tomokinakamaru/sqlew',
    version='0.3.1'
)
