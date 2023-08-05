# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '0.1.4'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.rst')
    + '\n' +
    read('CHANGES.rst'))

setup(
    name='ps.zope.i18nfield',
    version=version,
    description="A zope.schema field for inline translations.",
    long_description=long_description,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Zope3",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Zope",
    ],
    keywords='zope zope3 schema i18n z3c.form',
    author='Propertyshelf, Inc.',
    author_email='development@propertyshelf.com',
    url='https://github.com/propertyshelf/ps.zope.i18nfield',
    download_url='http://pypi.python.org/pypi/ps.zope.i18nfield',
    license='GPL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['ps', 'ps.zope'],
    zip_safe=False,
    include_package_data=True,
    extras_require=dict(
        test=[
            'unittest2',
            'z3c.form [test]',
            'zc.buildout',
            'zope.browserpage',
            'zope.publisher',
            'zope.testing',
            'zope.traversing',
        ],
    ),
    install_requires=[
        'setuptools',
        'ZODB3',
        'z3c.indexer',
        'zope.globalrequest',
        'zope.i18n',
        'zope.interface',
        'zope.schema',
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
