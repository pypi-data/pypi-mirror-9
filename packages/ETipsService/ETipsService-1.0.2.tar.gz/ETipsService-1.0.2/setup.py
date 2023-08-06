# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='ETipsService',
    packages=find_packages(),
    version="1.0.2",
    description="service lib for ETips",
    author="Jayin Ton",
    author_email="tonjayin@gmail.com",
    url="https://github.com/Jayin/ETipsService",
    keywords=['ETips'],
    license='Apache License, Version 2.0',
    install_requires=['beautifulsoup4', 'requests'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent"
    ]

)
