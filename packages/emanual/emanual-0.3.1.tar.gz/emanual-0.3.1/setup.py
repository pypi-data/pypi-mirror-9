#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages
import emanual

with open('README.md') as f:
    long_description = f.read()


setup(
    name='emanual',
    version=emanual.__version__,
    description=emanual.__doc__.strip(),
    long_description=long_description,
    url='https://github.com/EManual/EManual-CLI',
    author=emanual.__author__,
    author_email='tonjayin@gmail.name',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'path.py'
    ],
    entry_points={
        'console_scripts' : [
            'emanual=emanual.cli:main',
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='emanual cli',
)



