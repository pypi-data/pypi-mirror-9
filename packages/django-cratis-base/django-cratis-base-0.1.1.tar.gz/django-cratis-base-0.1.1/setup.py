import os
from setuptools import setup, find_packages
# from tests import PyTest

setup(
    name='django-cratis-base',
    version='0.1.1',
    packages=find_packages(),

    url='',
    license='MIT License',
    author='Alex Rudakov',
    author_email='ribozz@gmail.com',
    description='Django-cratis is a way to group together django applications, so they form reusable features.',
    long_description='',
    install_requires=[
        'django-cratis>=0.5.0',
    ]
)

