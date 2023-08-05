import os
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...

setup(
    name="pyslave",
    version="0.0.1",
    author="Steven Huf",
    author_email="huffy7412@gmail.com",
    description="Send random functions through celery, without having to define the @task.",
    keywords="celery",
    url="http://packages.python.org/pyslave",
    packages=['pyslave'],
    install_requires=[
        "celery",
        "dill",
    ],
    long_description=open(os.path.join(os.path.dirname(__file__), "README")).read(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "License :: Public Domain",
    ],
)
