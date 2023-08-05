"""Setup script of zinnia-twitter"""
from setuptools import setup
from setuptools import find_packages

import zinnia_twitter

setup(
    name='zinnia-twitter',
    version=zinnia_twitter.__version__,

    description='Twitter plugin for django-blog-zinnia',
    long_description=open('README.rst').read(),

    keywords='django, zinnia, twitter',

    author=zinnia_twitter.__author__,
    author_email=zinnia_twitter.__email__,
    url=zinnia_twitter.__url__,

    packages=find_packages(exclude=['demo_zinnia_twitter']),
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

    license=zinnia_twitter.__license__,
    include_package_data=True,
    zip_safe=False,
    install_requires=['tweepy']
)
