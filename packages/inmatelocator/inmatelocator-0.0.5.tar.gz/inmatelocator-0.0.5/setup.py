import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="inmatelocator",
    version="0.0.5",
    author="Charlie DeTar",
    author_email="cfd@media.mit.edu",
    description=("Library for locating people incarcerated in the US "
                 "by querying official prison search tools"),
    long_description=read('README.md'),
    license="MPL",
    packages=['inmatelocator', 'inmatelocator.stateparsers'],
    include_package_data=True,
    install_requires=['requests', 'addresscleaner', 'lxml'],
    url="https://bitbucket.org/yourcelf/inmatelocator"
)
