from setuptools import setup, find_packages

requires = ['py-oauth2>=0.0.10', 'requests==1.2.0'],

kw = dict(
    name = 'edo_client',
    version = '0.0.3',
    description = 'Everydo OAuth 2 API Python SDK',
    long_description = "Everydo OAuth 2 API Python SDK",
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
