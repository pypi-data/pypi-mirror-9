import os
from setuptools import setup, find_packages
# from tests import PyTest

setup(
    name='django-cratis',
    version='0.5.0',
    packages=find_packages(),

    url='',
    license='Simplified BSD License',
    author='Alex Rudakov',
    author_email='ribozz@gmail.com',
    description='Django-cratis is a way to group together django applications, so they form reusable features.',
    long_description='',
    install_requires=[
        'django>=1.4',
        'django-configurations',
        'dj-database-url',
        'PyYaml',
        'inject'
    ],

    entry_points={
        'console_scripts': [
            'cratis = cratis.cli:cratis_cmd',
            'cratis-init = cratis.cli:cratis_init_cmd',
        ],
    },
)

