#!/usr/bin/env python
from django_trap import __version__, __description__, __license__

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

setup(
    name='django-trap',
    version=__version__,
    description=__description__,
    long_description=open('./README.rst', 'r').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    keywords='django admin honeypot trap',
    maintainer='Mark Vasilkov',
    maintainer_email='mvasilkov@gmail.com',
    url='https://github.com/mvasilkov/django-trap',
    download_url=('https://github.com/mvasilkov/django-trap/tarball/v%s' %
                  __version__),
    license=__license__,
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
)
