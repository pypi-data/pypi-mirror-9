__author__ = 'nickmab'

from setuptools import setup, find_packages

setup(
    name='nickmab.async_util',
    version='0.0.2',
    license='MIT',
    author='Nick Mabbutt',
    author_email='nickmab@gmail.com',
    description='My first package (be nice please!). Convenience objects for working with long-running calcs and web requests.',
    url='https://github.com/nickmab/async_util',
    keywords='json thread async',
    packages=find_packages(),
    namespace_packages=['nickmab'],
    install_requires=[
        'beautifulsoup4>=4.3.2',
        'threadpool>=1.2.7',
    ],
)
