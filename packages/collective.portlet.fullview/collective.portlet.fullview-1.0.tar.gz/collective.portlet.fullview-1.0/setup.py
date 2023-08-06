from setuptools import setup
from setuptools import find_packages

version = '1.0'

name = "collective.portlet.fullview"
namespace = ['collective', 'collective.portlet', ]
baseurl = "http://github.com/collective"

setup(
    name=name,
    version=version,
    description="Displays a content item as full view",
    long_description="{0}{1}".format(
        open("README.rst").read(),
        open("CHANGES.rst").read(),
    ),
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
    ],
    keywords='plone portlet',
    author='Johannes Raggam',
    author_email='johannes@raggam.co.at',
    url='%s/%s' % (baseurl, name),
    license='GPL',
    namespace_packages=namespace,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Products.CMFPlone',
    ],
)
