# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-mailtestfield',
    version='1.0.1',
    author=u'Jon Combe',
    author_email='pypi@joncombe.net',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/naremit/django-mailtestfield',
    license='BSD licence, see LICENCE file',
    description='Drop-in replacement for Django\'s forms.EmailField. Uses ' \
        'http://mailtest.in to validate email addresses. Caches results.',
    long_description='Drop-in replacement for Django\'s forms.EmailField. Uses ' \
        'http://mailtest.in to validate email addresses. Caches results.',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    zip_safe=False,
)
