#!/usr/bin/env python
import os

from setuptools import setup, find_packages


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='floraconcierge-client',
    version=__import__('floraconcierge').get_version(),
    author='Alexandr Shurigin',
    author_email='alexandr.shurigin@gmail.com',
    description='FloraExpress API python client library. www.floraexpress.ru',
    license='BSD',
    keywords='floraconcierge floraexpress ecommerce api adapter client',
    url='http://www.floraexpress.ru/',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    test_suite='tests',
    long_description=read("README.rst"),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Customer Service',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Legal Industry',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Natural Language :: Russian',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: PHP',
        'Topic :: Database :: Front-Ends',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Embedded Systems'
    ], install_requires=['pytz', 'ordered_set']
)