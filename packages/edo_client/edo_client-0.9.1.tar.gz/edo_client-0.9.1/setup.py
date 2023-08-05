from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
requires = ['py-oauth2>=0.0.10', 'requests==1.2.0'],

kw = dict(
    name = 'edo_client',
    version = '0.9.1',
    description = 'SDK for easydo.cn',
    long_description=README,
    author = 'Chen Weihong',
    author_email = 'whchen1080@gmail.com',
    url = 'https://github.com/everydo/python-sdk',
    download_url = 'https://github.com/everydo/python-sdk',
    packages = find_packages(),
    install_requires=requires,
    tests_require=requires,
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ])

setup(**kw)
