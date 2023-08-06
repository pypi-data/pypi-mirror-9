#!/usr/bin/env python
from setuptools import setup
from os import path

setup(
    name = 'bambu-oembed',
    version = '2.5.1',
    description = 'Embed resources like YouTube videos, tweets and Flickr images by entering their URL on a single line of text. Methodology inspired by WordPress',
    author = 'Steadman',
    author_email = 'mark@steadman.io',
    url = 'https://github.com/iamsteadman/bambu-oembed',
    long_description = open(path.join(path.dirname(__file__), 'README')).read(),
    install_requires = [
        'Django>=1.4',
        'requests>=2.0'
    ],
    packages = [
        'bambu_oembed',
        'bambu_oembed.migrations',
        'bambu_oembed.templatetags'
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django'
    ],
    package_data = {
        'bambu_oembed': [
            'static/oembed/*.js'
        ]
    }
)
