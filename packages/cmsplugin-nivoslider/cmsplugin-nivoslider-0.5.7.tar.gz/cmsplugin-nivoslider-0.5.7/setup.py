# -*- coding:utf-8 -*-

from setuptools import setup, find_packages
from cmsplugin_nivoslider import version_string

authors = open('AUTHORS').read()

setup(
    name='cmsplugin-nivoslider',
    version=version_string,
    author=", ".join(authors.split("\n")),
    author_email='bcabezas@apsl.net',
    packages=find_packages(),
    license='MIT',
    description="Simple Nivo Slider plugin for django-cms",
    long_description=open('README.rst').read(),
    install_requires=['django-cms', 'django-filer'],
    url='https://bitbucket.org/bercab/cmsplugin-nivoslider',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    include_package_data=True,
    zip_safe=False,
)
