#!/usr/bin/env python


from setuptools import setup


setup(
    name='BetterTablesExtension',
    version='0.0.1',
    author='Gregg Thomason',
    author_email='gregg@neurobashing.com',
    description='Python-Markdown extension to add additional table options',
    url='http://neurobashing.com/',
    py_modules=['better_tables'],
    install_requires=['Markdown>=2.0',],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup :: HTML'
    ]
)
