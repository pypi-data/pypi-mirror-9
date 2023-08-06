#!/usr/bin/env python
#  -*- coding: utf-8 -*-


from setuptools import setup

import choosealicense


try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    with open('README.md') as f:
        long_description = f.read()


setup(
    name='choosealicense-cli',
    version=choosealicense.__version__,
    description='Bring http://choosealicense.com to your terminal',
    long_description=long_description,
    url='http://github.com/lord63/choosealicense-cli',
    author='lord63',
    author_email='lord63.j@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='license generate cli choosealicense',
    packages=['choosealicense'],
    install_requires=[
        'click>=4.0',
        'requests>=2.6.0'
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'license=choosealicense.main:cli']
    }
)
