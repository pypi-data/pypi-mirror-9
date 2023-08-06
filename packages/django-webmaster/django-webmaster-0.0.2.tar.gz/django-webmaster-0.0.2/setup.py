# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-webmaster',
    version='0.0.2',
    author=u'Jon Combe',
    author_email='pypi@joncombe.net',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/joncombe/django-webmaster',
    license='BSD licence, see LICENCE file',
    description='A very basic tool to keep track of your domain names and ' \
        'servers.',
    long_description='Picture the scene: you own and/or manage multiple ' \
        'domain names, purchased from a number of different registrars. You ' \
        'use a few different DNS and web hosting providers and have multiple ' \
        'servers dotted around the globe. Keeping track of all that is a ' \
        'pain. If a server, or any other link in the above chain goes down, ' \
        'how can you quickly find what is hosted where? How many of your ' \
        'clients are affected? You can create a complex spreadsheet and ' \
        'employ various filters to do all that for you, but this is ' \
        'hopefully a little less painful.',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: System :: Systems Administration',
    ],
    zip_safe=False,
)
