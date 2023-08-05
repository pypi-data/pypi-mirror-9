"""Setup file for handling the importconfig package."""
from setuptools import setup

import importconfig

description, long_description = importconfig.__doc__.split('\n\n', 1)

setup(
    name=importconfig.__name__,
    description=description,
    long_description=long_description,
    license='MIT',
    url=importconfig.__url__,
    author=importconfig.__author__,
    author_email=importconfig.__email__,
    packages=[
        'importconfig',
    ],
    version=importconfig.__version__,
    install_requires=[
        'PyYaml'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
    ],
)
