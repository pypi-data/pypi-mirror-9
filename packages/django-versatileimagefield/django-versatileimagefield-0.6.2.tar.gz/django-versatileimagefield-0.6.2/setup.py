# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-versatileimagefield',
    packages=find_packages(),
    version='0.6.2',
    author=u'Jonathan Ellenberger',
    author_email='jonathan_ellenberger@wgbh.org',
    url='http://github.com/WGBH/django-versatileimagefield/',
    license='MIT License, see LICENSE',
    description="A drop-in replacement for django's ImageField that provides "
                "a flexible, intuitive and easily-extensible interface for "
                "quickly creating new images from the one assigned to your "
                "field.",
    long_description=open('README.rst').read(),
    zip_safe=False,
    install_requires=['Pillow>=2.4.0'],
    package_data={
        'versatileimagefield': [
            'static/versatileimagefield/css/*.css',
            'static/versatileimagefield/js/*.js',
        ]
    },
    classifiers=[
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Multimedia :: Graphics :: Presentation'
    ]
)
