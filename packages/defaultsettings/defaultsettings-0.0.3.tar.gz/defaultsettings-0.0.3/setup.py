# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print(
        "warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

with open('LICENSE') as f:
    license = f.read()


setup(
    name='defaultsettings',
    version='0.0.3',
    description='Handle settings with default in python',
    long_description=read_md('README.md'),
    #long_description=readme,
    author='oskarnyqvist',
    author_email='oskarnyqvist@gmail.com',
    url='https://github.com/oskarnyqvists/defaultsettings',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
)
