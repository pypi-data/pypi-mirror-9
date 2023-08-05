# -*- coding: utf-8 -*-
"""`sphinx_drove_theme` lives on `Github`_.

.. _github: https://www.github.com/droveio/sphinx_drove_theme

"""
from setuptools import setup
from sphinx_drove_theme import __version__


setup(
    name='sphinx_drove_theme',
    version=__version__,
    url='https://github.com/droveio/sphinx_drove_theme/',
    license='MIT',
    author='Andrés J. Díaz',
    author_email='ajdiaz@connectical.com',
    description='drove.io theme for Sphinx, 2014 version.',
    long_description=open('README.rst').read(),
    zip_safe=False,
    packages=['sphinx_drove_theme'],
    package_data={'sphinx_drove_theme': [
        'theme.conf',
        '*.html',
        'static/css/*.css',
        'static/js/*.js',
        'static/font/*.*'
    ]},
    include_package_data=True,
    install_requires=open('requirements.txt').read().splitlines(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
    ],
)
