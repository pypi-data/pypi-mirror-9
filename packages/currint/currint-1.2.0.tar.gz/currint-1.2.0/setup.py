from setuptools import setup, find_packages
from currint import __version__

setup(
    name='currint',
    version=__version__,
    description='Integer-based, fixed precision currency calculation',
    packages=find_packages(),
    author='Andrew Godwin',
    author_email='andrew@aeracode.org',
)

