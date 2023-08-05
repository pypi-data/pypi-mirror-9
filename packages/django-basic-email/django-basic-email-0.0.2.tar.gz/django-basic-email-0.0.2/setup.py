# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from pkg_resources import require, DistributionNotFound
import basic_email
import os
package_name = 'django-basic-email'


def local_open(fname):
    return open(os.path.join(os.path.dirname(__file__), fname))

requirements = local_open('requirements/external_apps.txt')
test_requirements = local_open('requirements/test_apps.txt')

# Build the list of dependency to install
required_to_install = []
for dist in requirements.readlines():
    dist = dist.strip()
    try:
        require(dist)
    except DistributionNotFound:
        required_to_install.append(dist)

test_required_to_install = []
for dist in test_requirements.readlines():
    dist = dist.strip()
    try:
        require(dist)
    except DistributionNotFound:
        test_required_to_install.append(dist)

data_dirs = []

url_schema = 'http://pypi.python.org/packages/source/d/%s/%s-%s.tar.gz'
download_url = url_schema % (package_name, package_name,
                             basic_email.__version__)


setup(
    name=package_name,
    test_suite='example_project.test_runner.main',
    version=basic_email.__version__,
    description=basic_email.__doc__,
    author=basic_email.__author__,
    author_email=basic_email.__contact__,
    url=basic_email.__homepage__,
    license=basic_email.__license__,
    long_description=local_open('README.rst').read(),
    download_url=download_url,
    install_requires=required_to_install,
    tests_require=test_required_to_install,
    packages=find_packages(exclude=['example', 'example.*']),
    # very important for the binary distribution to include the templates.
    package_data={'basic_cms': data_dirs},
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: JavaScript',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
)
