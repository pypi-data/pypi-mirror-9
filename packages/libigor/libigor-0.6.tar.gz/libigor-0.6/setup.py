import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = "libigor",
    version = "0.6",
    author = "Mateusz 'novo' Klos",
    author_email = "novopl@gmail.com",
    license = "MIT",
    keywords = "webdev web framework jsobj serialize utility",
    url = "http://github.com/novopl/igor",
    packages=['igor'],
    description = ("Collection of general purpose python "
                   "libraries with focus on web development"),
    long_description=read('README.rst'),
    install_requires = [
        'six', 'python-dateutil'
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
    ],
)
