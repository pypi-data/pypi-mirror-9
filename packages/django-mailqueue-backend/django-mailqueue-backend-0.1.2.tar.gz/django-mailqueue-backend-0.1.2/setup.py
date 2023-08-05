from re import search as re_search, M as re_M
from os import path as os_path
from codecs import open as codecs_open
from setuptools import setup, find_packages

def read(*parts):
    file_path = os_path.join(os_path.dirname(__file__), *parts)
    return codecs_open(file_path, encoding='utf-8').read()


def find_version(*parts):
    version_file = read(*parts)
    version_match = re_search(r"^__version__ = ['\"]([^'\"]*)['\"]",
        version_file, re_M)
    if version_match:
        return str(version_match.group(1))
    raise RuntimeError("Unable to find version string.")


description = long_description = "Simple Mail Queuing Backend for Django."
if os_path.exists('README.rst'):
    long_description = read('README.rst')

#mailq | tail -n +2 | grep -v '^ *(' | awk  'BEGIN { RS = "" } { if ($7 == "from@example.com" || $8 == "from@example.com") print $1 } ' | tr -d '*!'| postsuper -d -

setup(name='django-mailqueue-backend',
    version=find_version('mailqueue_backend', '__init__.py'),
    description=description,
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Communications :: Email",
        "Topic :: Utilities",
        "Framework :: Django",
    ],
    keywords='django mail queue smtp backend',
    maintainer='Dwaiter.com',
    maintainer_email='dev@dwaiter.com',
    url='https://bitbucket.org/dwaiter/django-mailqueue-backend',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['django>=1.4,<1.5,>=1.6', 'queue-front>=0.7.2']
)