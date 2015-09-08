import os

from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def requirements(fname):
    for line in open(os.path.join(os.path.dirname(__file__), fname)):
        yield line.strip()


setup(
    name="mwsessions",
    version="0.0.2",  # Change in mwsessions/__init__.py
    author="Aaron Halfaker",
    author_email="aaron.halfaker@gmail.com",
    url="http://github.com/mediawiki-utilities/python-mwsessions",
    packages=find_packages(),
    entry_points = {
        'console_scripts': [
            'mwsessions=mwsessions.mwsessions:main'
        ],
    },
    license=read("LICENSE"),
    description="A set of utilities for group MediaWiki user actions into " +
                "sessions.",
    long_description=read("README.md"),
    install_requires=requirements("requirements.txt")
)
