# -*- coding: utf-8 -*-

from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-genericimports',
    version='0.1b4',
    author=u'Oscar Carballal Prego',
    author_email='oscar.carballal@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    url='http://github.com/clione/django-genericimports',
    license='BSD licence, see LICENSE file',
    description='Import any CSV or XLS file regardless of data types, headers or foreignkeys.',
    long_description=open('README.md').read(),
    zip_safe=False,
    install_requires=[
        "django >= 1.5.12",
        "openpyxl >= 2.1.4",
        "python-dateutil >= 1.5",
        "django-rq >= 0.7.0",
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ]
)
