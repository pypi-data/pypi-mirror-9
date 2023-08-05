from setuptools import setup, find_packages

VERSION = "1.0.0-beta.4"

LONG_DESCRIPTION = """
=================================
django-mobile-framework
=================================
Django mobile framework that contains the neccessary models required to develop
backends for mobile applications.
"""

setup(
    name='django-mobile-framework',
    version=VERSION,
    url='https://github.com/mstarinteractive/django-mobile-framework',
    download_url='https://github.com/mstarinteractive/django-mobile-framework/tarball/1.0.tar.gz',
    description='Contains models to help developers create mobile application backends',
    long_description=LONG_DESCRIPTION,
    author='Morningstar Enterprises Inc.',
    author_email='mstar@mstar.io',
    maintainer='Karl Castillo',
    maintainer_email='karl@karlworks.com',
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Site Management'
    ],
    keywords=['django','mobile','framework','utility'],
    packages=[
        'mobile_framework',
        'mobile_framework.core',
        'mobile_framework.device',
        'mobile_framework.tests',
        'mobile_framework.user',
        'mobile_framework.version',
    ],
    install_requires=[
        'django>=1.7',
        'django-oauth-toolkit',
        'django-cors-headers',
        'djangorestframework>=3',
        'psycopg2'
    ]
)
