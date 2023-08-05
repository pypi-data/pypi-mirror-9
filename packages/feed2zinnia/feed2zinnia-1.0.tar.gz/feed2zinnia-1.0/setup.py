"""Setup script of feed2zinnia"""
from setuptools import setup
from setuptools import find_packages

import zinnia_feed

setup(
    name='feed2zinnia',
    version=zinnia_feed.__version__,

    description='Import your RSS or Atom feed into Zinnia',
    long_description=open('README.rst').read(),

    keywords='django, zinnia, feed, rss, atom',

    author=zinnia_feed.__author__,
    author_email=zinnia_feed.__email__,
    url=zinnia_feed.__url__,

    packages=find_packages(exclude=['demo_zinnia_feed']),
    classifiers=[
        'Framework :: Django',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries :: Python Modules'],

    license=zinnia_feed.__license__,
    include_package_data=True,
    zip_safe=False,
    install_requires=['feedparser>=5.1.3']
)
