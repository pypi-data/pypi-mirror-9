# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

b2w = __import__('b2w', {}, {}, [''])

def read(f):
    f = open(os.path.join(os.path.dirname(__file__), f))
    read = f.read()
    f.close()
    return read

setup(
    name="python-bonmarketplace-b2w",
    version=b2w.__version__,
    description=(u"Cliente Python para integração com Bon Marketplace B2W (Shoptime, Lojas Americanas, Submarino e Soubarato)"),
    long_description=read('README.rst'),
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=["b2w", "submarino", "americanas", "shoptime", "soubarato", "lojas", "marketplace", "ecommerce", "e-commerce", "virtual"],
    author=b2w.__author__,
    author_email="gabriel@poteinterativo.com.br",
    url="https://github.com/gabrielgaliaso/python-bonmarketplace-b2w",
    license=b2w.__license__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['requests']
)