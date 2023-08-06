import os
from setuptools import setup, find_packages
# from tests import PyTest

setup(
    name='django-cratis-suit',
    version='0.1.2',
    packages=find_packages(),

    url='',
    license='MIT License',
    author='Alex Rudakov',
    author_email='ribozz@gmail.com',
    description='Django-suit integration',
    long_description='',
    install_requires=[
        'django-suit',
        'cratis-base'

])

