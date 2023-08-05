[![Build Status](https://travis-ci.org/mstarinteractive/django-mobile-framework.svg?branch=master)](https://travis-ci.org/mstarinteractive/django-mobile-framework) [![CocoaPods](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat)]() [![PyPI](https://img.shields.io/badge/pypi-1.0.0--beta-brightgreen.svg?style=flat)](https://pypi.python.org/pypi?name=django-mobile-framework&version=1.0.0-beta&:action=display)

Django Mobile Framework
=======================
The Django Mobile Framework is a Django module that gives developers the necessary components to create a server back-end for mobile applications.

Modules available to develop on:
- Device (used to store the different devices that used the API)
- Application Version (a list of application versions that is either known or unknown)
- User (a custom User model and an App User model to represent users that have used the app)

Features available:
- API to Create/Get/Update/Delete certain models.

Dependencies:
- [Django Rest Framework](http://www.django-rest-framework.org/)
- [Django Oauth Toolkit](https://django-oauth-toolkit.readthedocs.org/en/0.7.0/)
- [Django Cors Headers](https://github.com/ottoyiu/django-cors-headers/)
- [Django UUID Field](https://github.com/dcramer/django-uuidfield/)
- [Psycopg2](http://initd.org/psycopg/)

Installation and Setup
----------------------

Install via pip:
```
pip install django-mobile-framework
```

Install modules that aren't in PyPi yet:
```
pip install git+https://github.com/dcramer/django-uuidfield.git
```

Install the apps:
```
INSTALLED_APPS = (
   ...
   'ouath2_provider',
   'rest_framework',
   'corsheaders',
   
   'mobile_framework.core',
   'mobile_framework.version',
   'mobile_framework.device',
   'mobile_framework.user',
   ...
)
```

Add the Middlewares:
```
MIDDLEWARE_CLASSES = (
    ...
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    ...
)
```

Add the URLs:
```
url(r'^mf/', include('mobile_framework.urls', namespace='mobile_framework')),
```

Create Database:
```
$ createdb DB_NAME
$ psql DB_NAME
# CREATE USER username WITH PASSWORD 'password';
```
