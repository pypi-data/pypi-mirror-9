import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "capuchin",
    version = "0.0.4",
    author = "Justin Wilson",
    author_email = "justinwilson1@gmail.com",
    description = ("Simple wrapper around tornado that uses "
        "environment variables for host, port, endpoint prefix. "
        "Also uses the py-hancock library for the ability to sign "
        "endpoints. Endpoints for `time`, `ping`, and `status` are "
        "automatically added as well."),
    license = "Simplified BSD",
    url = "http://pypi.python.org/pypi/capuchin",
    packages=['capuchin',],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ],
    install_requires=[
        "tornado >= 4.0.0",
    	"requests >= 2.3.0",
    ],
)

