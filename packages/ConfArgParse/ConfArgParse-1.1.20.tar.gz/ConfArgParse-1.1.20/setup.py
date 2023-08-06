from __future__ import print_function
from setuptools import setup

try:
   import confargparse
   docs = confargparse.__doc__
   print (docs, file=open("README.txt", "w"))
except:
   docs = file("README.txt").read()
   
setup(name="ConfArgParse",
    version="1.1.20",
    install_requires=["hgtools"],
    description="An integrated argument/configuration file parser that follows the syntax of argparser",
    long_description=docs,
    author="S. Joshua Swamidass",
    url="https://bitbucket.org/swamidass/confargparse/",
    author_email="swamidass@gmail.com",
    classifiers=["Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "License :: Free for non-commercial use",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        ],
    py_modules=['confargparse']
)
