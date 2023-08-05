import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "hancock",
    version = "1.0.0",
    author = "Justin Wilson",
    author_email = "justinwilson1@gmail.com",
    description = ("HTTP request signing library."
    	"Provides private key URL signing for secure HTTP requests."),
    license = "Simplified BSD",
    url = "http://pypi.python.org/pypi/hancock",
    packages=['hancock',],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ],
    install_requires=[
    	"requests >= 2.3.0",
        "simplejson >= 3.6.5",
    ],
)

