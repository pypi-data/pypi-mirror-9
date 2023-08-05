# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

b2w = __import__('b2w', {}, {}, [''])

def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read()

setup(
    name = "python-bonmarketplace-b2w",
    version = b2w.__version__,
    author = "Gabriel Galiaso",
    author_email = "gabriel@poteinterativo.com.br",
    description = (u"Cliente Python para integração com Bon Marketplace B2W (Shoptime, Lojas Americanas, Submarino e Soubarato)"),
    long_description = read('README.rst'),
    classifiers = [
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    license = b2w.__license__,
    keywords = ["b2w", "submarino", "americanas", "shoptime", "soubarato", "lojas", "marketplace", "ecommerce", "e-commerce", "virtual"],
    url = "https://github.com/gabrielgaliaso/python-bonmarketplace-b2w",
    packages = find_packages(),
    include_package_data = False,
    zip_safe = False,
    install_requires = ['requests']
)