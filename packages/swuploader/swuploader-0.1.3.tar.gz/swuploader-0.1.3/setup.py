#!/usr/bin/env python

from setuptools import setup

from swuploader import __version__

setup(
    name='swuploader',
    version=__version__,
    author='Brett Langdon',
    author_email='brett@blangdon.com',
    py_modules=[
        'swuploader',
    ],
    install_requires=[
        'shapeways==1.0.0',
        'docopt==0.6.2',
    ],
    scripts=[
        './bin/swuploader',
    ],
    setup_requires=[],
    description='Easy to use bulk model uploader for Shapeways.com API',
    url='http://github.com/brettlangdon/swuploader',
)
