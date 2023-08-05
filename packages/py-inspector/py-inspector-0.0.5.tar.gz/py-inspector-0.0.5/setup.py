# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='py-inspector',
    version='0.0.5',
    url='https://github.com/maethorin/py-inspector',
    license='MIT',
    description='Possibilita a criação de testes para PEP8 e PyLint que serão executados com nose',
    author=u'Márcio Duarte',
    author_email='maethorin@gmail.com',
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet",
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['pep8', 'pylint', 'nose'],
)
