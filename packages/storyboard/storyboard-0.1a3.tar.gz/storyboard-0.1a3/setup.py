#!/usr/bin/env python3
"""Setup script for PyPI."""

import os
from setuptools import setup

here = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(here, 'README.rst'), 'r') as f:
    long_description = f.read()

# read version from version.py and save in __version__
with open(os.path.join(here, 'storyboard', 'version.py')) as f:
    exec(f.read())

setup(
    name='storyboard',
    version=__version__,
    description='Customizable video storyboard generator with metadata report',
    long_description=long_description,
    url='https://github.com/zmwangx/storyboard',
    author='Zhiming Wang',
    author_email='zmwangx@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Multimedia :: Video',
    ],
    keywords='video storyboard metadata thumbnail ffmpeg',
    packages=['storyboard'],
    install_requires=[
        'Pillow>=2.7',
    ],
    package_data={
        'storyboard': [
            'SourceCodePro-Regular.otf',
        ]
    },
    entry_points={
        'console_scripts': [
            'storyboard=storyboard.storyboard:main',
            'metadata=storyboard.metadata:main',
        ]
    },
)
