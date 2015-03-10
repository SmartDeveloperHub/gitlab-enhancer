__author__ = 'alejandrofcarrera'

import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="Drainer",
    version="0.0.1",
    author="Alejandro F. Carrera",
    author_email="alejandro.fernandez.carrera@centeropenmiddleware.com",
    description="A project for Service Drainer",
    license="BSD",
    keywords="inner-source drainer",
    url="http://packages.python.org/an_example_pypi_project",
    namespace_packages=['sdh-drainer'],
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    long_description=read('README'),
    install_requires=['pyapi-gitlab', 'flask', 'flask_negotiate'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)