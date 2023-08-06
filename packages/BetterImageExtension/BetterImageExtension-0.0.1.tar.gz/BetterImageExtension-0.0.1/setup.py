#!/usr/bin/env python


from setuptools import setup


setup(
    name='BetterImageExtension',
    version='0.0.1',
    author='Gregg Thomason',
    author_email='gregg@neurobashing.com',
    description='Python-Markdown extension to add additional image syntax eg print and web sizes from a single image',
    url='http://neurobashing.com/',
    py_modules=['better_image'],
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
