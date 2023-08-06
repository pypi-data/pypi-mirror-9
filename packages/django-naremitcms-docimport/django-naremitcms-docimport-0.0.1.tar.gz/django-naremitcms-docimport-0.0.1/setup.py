# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-naremitcms-docimport',
    version='0.0.1',
    author=u'Jon Combe',
    author_email='jon@naremit.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    url='http://naremitcms.com',
    license='BSD licence, see LICENCE file',
    description='A static text file import tool for NaremitCMS',
    long_description='A static text file import tool for NaremitCMS',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    zip_safe=False,
)
