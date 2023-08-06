from setuptools import setup, find_packages
import sys, os

version = '0.3'

setup(
    name='python-whois',
    version=version,
    description="Whois querying and parsing of domain registration information.",
    long_description='',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP'
    ],
    keywords='whois, python',
    author='Richard Penman',
    author_email='richard@webscraping.com',
    url='https://bitbucket.org/richardpenman/pywhois',
    license='MIT',
    packages=['whois'],
    package_dir={'whois':'whois'},
    package_data={
        'whois': ['data/*.txt']
    },
    extras_require={
        'better date conversion': ["python-dateutil"]
    },
    include_package_data=True,
    zip_safe=False,
)
