__author__ = 'alejandrofcarrera'

import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="sdh-drainer",
    version="0.0.6",
    author="Alejandro F. Carrera",
    author_email="alejandro.fernandez.carrera@centeropenmiddleware.com",
    description="A project for Drainer Service",
    license="BSD",
    keywords="inner-source drainer",
    url="https://bitbucket.org/smartdeveloperhub/sdh-drainer",
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    long_description=read('README.md'),
    install_requires=['pyapi-gitlab', 'flask', 'flask_negotiate', 'python-dateutil', 'redis'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)