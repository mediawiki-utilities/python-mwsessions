from setuptools import setup

setup(
    name="mwsessions",
    version="0.0.1",  # Change in mwsessions/__init__.py
    author="Aaron Halfaker",
    author_email="aaron.halfaker@gmail.com",
    url="http://github.com/mediawiki-utilities/python-mwsessions",
    packages=["mwsessions"],
    license=open("LICENSE").read(),
    description="A set of utilities for group MediaWiki user actions into " +
                "sessions.",
    long_description=open("README.md").read(),
    install_requires=["mwtypes"]
)
