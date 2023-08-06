from setuptools import setup
from setuptools import find_packages

version = '1.0'
description = open("README.rst").read() + "\n" + open("CHANGES.rst").read()

setup(
    name='collective.simpleintranetworkflow',
    version=version,
    description="Simple Intranet/Extranet workflow.",
    long_description=description,
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
    ],
    keywords='plone workflow',
    author='Johannes Raggam',
    author_email='raggam-nl@adm.at',
    url='https://github.com/collective/collective.simpleintranetworkflow',
    license='GPL',
    packages=find_packages(),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Products.CMFPlone',
    ],
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """
)
