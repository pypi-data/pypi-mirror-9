#!/usr/bin/env python
from setuptools import setup, find_packages
import advanced_reports

setup(
    name="django-advanced-reports",
    version=advanced_reports.__version__,
    url='https://github.com/vikingco/django-advanced-reports',
    license='BSD',
    description="Advanced reports for Django",
    long_description=open('README.md', 'r').read(),
    author='Jef Geskens, VikingCo nv',
    packages=find_packages('.'),
    package_data = {'advanced_reports': [
                'static/*.js', 'static/*/*.js', 'static/*/*/*.js',
                'static/*.css', 'static/*/*.css', 'static/*/*/*.css',
                'static/*.png', 'static/*/*.png', 'static/*/*/*.png', 'static/*/*/*/*.png',
                'templates/*.html', 'templates/*/*.html', 'templates/*/*/*.html', 'templates/*/*/*/*.html',
                ],},
    zip_safe=False, # Don't create egg files, Django cannot find templates in egg files.
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Environment :: Web Environment',
        'Framework :: Django',
    ],
    install_requires=[
        'Django',
        'six',
        'django-widget-tweaks',
        'pygments',
    ]
)
