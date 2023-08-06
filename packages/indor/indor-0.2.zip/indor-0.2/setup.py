# coding=utf-8
from setuptools import setup

VERSION = '0.2'

setup(
    name='indor',
    version=VERSION,
    install_requires=[
        "requests",
        "pyparsing",
        'mock',
        'nose',
        'nose-cov',
        'junit-xml',
        'termcolor'
    ],
    package_dir={'indor': 'indor/src'},
    packages=['indor'],
    package_data={'indor': ['logo.txt']},
    url='https://github.com/nokia-wroclaw/innovativeproject-resttest',
    license='',
    author='Sławomir Domagała, Damian Mirecki, Tomasz Wlisłocki, Bartosz Zięba',
    author_email='',
    description='Tool for running rest-api tests written in plain language.',
    entry_points={
        'console_scripts': [
            'indor = indor.__main__:main',
        ]
    }
)

