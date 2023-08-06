import sys, os
import setuptools

version = '0.3.1'

setuptools.setup(
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
    extras_require={
        'better date conversion': ["python-dateutil"]
    },
    include_package_data=True,
    zip_safe=False
)
