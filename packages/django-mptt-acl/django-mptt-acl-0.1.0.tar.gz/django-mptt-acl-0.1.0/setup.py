# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name="django-mptt-acl",
    install_requires=[
        'django-mptt==0.6.1',
        'django-bitfield==1.7.1',
    ],
    packages=['django_mptt_acl', ],
    dependency_links=['git+https://github.com/Eksmo/django-bitfield.git#egg=django_bitfield-1.7.1'],
    author=u"rclick s.r.o.",
    author_email='info@rclick.cz',
    zip_safe=True,
    include_package_data=True,
    clasifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Framework :: Django",
        "Topic :: Security",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    description="",
    version="0.1.0"
)
