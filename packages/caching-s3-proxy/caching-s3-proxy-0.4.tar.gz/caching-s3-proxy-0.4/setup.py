import codecs
import glob
import os
from setuptools import setup


setup(
    name='caching-s3-proxy',
    version='0.4',
    description=('provides an unauthenticated plain HTTP frontend for'
                 ' public and private S3 buckets, and caches on the'
                 ' filesystem using an LRU cache'),
    author='Rob Helmer',
    author_email='rhelmer@rhelmer.org',
    license='MPL',
    url='https://github.com/rhelmer/caching-s3-proxy',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        ],
    packages=['proxy'],
    keywords=['caching', 'lru', 's3', 'proxy', 'unauthenticated'],
    install_requires=['boto>=2.36.0', 'wsgiref>=0.1.2', 'ordereddict>=1.1.2'],
    entry_points={
        'console_scripts': [
            'caching-s3-proxy = proxy.run:main'
            ],
        },
    test_suite='nose.collector',
    zip_safe=False,
),
