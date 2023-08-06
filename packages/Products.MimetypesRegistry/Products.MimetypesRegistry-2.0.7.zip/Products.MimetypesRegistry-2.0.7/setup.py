from setuptools import find_packages
from setuptools import setup

version = '2.0.7'

setup(
    name='Products.MimetypesRegistry',
    version=version,
    description="MIME type handling for Zope",
    long_description=open("README.rst").read() + "\n" +
    open("CHANGES.rst").read(),
    classifiers=[
        "Framework :: Zope2",
        "Operating System :: OS Independent",
        "Framework :: Plone",
        "Framework :: Plone :: 5.0",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='Zope mimetype registry',
    author='Benjamin Saller',
    author_email='plone-developers@lists.sourceforge.net',
    url='http://pypi.python.org/pypi/Products.MimetypesRegistry',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['Products'],
    include_package_data=True,
    zip_safe=False,
    extras_require=dict(
        test=[
            'plone.app.testing',
        ]
    ),
    install_requires=[
        'setuptools',
        'zope.contenttype',
        'zope.interface',
        'Products.CMFCore',
        'Acquisition',
        'ZODB3',
        'Zope2',
    ],
)
