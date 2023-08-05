"""Setup file for handling the importconfig package."""
from setuptools import setup

import importconfig


setup(
    name=importconfig.__name__,
    description='JSON and YAML parsing with imports.',
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
