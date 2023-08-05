import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "easyab",
    version = "0.1.3",
    author = "easyab",
    author_email = "easyab@bainainfo.com",
    description = "An A/B Testing framework",
    long_description = read("README.txt"),
    license = "BSD",
    keywords = "a/b testing",
    packages = ['easyab'],
)
