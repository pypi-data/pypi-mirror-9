Django Odnoklassniki API
====================

[![PyPI version](https://badge.fury.io/py/django-odnoklassniki-api.png)](http://badge.fury.io/py/django-odnoklassniki-api) [![Build Status](https://travis-ci.org/ramusus/django-odnoklassniki-api.png?branch=master)](https://travis-ci.org/ramusus/django-odnoklassniki-api) [![Coverage Status](https://coveralls.io/repos/ramusus/django-odnoklassniki-api/badge.png?branch=master)](https://coveralls.io/r/ramusus/django-odnoklassniki-api) [![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/ramusus/django-odnoklassniki-api/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

Приложение позволяет взаимодействовать с объектами Одноклассники API используя стандартные модели Django

Установка
---------

    pip install django-odnoklassniki-api

В `settings.py` необходимо добавить:

    INSTALLED_APPS = (
        ...
        'oauth_tokens',
        'taggit',
        'odnoklassniki_api',
    )

    # oauth-tokens settings
    OAUTH_TOKENS_HISTORY = True                                             # to keep in DB expired access tokens
    OAUTH_TOKENS_ODNOKLASSNIKI_CLIENT_PUBLIC = ''                           # application public key
    OAUTH_TOKENS_ODNOKLASSNIKI_CLIENT_SECRET = ''                           # application secret key
    OAUTH_TOKENS_ODNOKLASSNIKI_SCOPE = ['']                                 # application scopes
    OAUTH_TOKENS_ODNOKLASSNIKI_USERNAME = ''                                # user login
    OAUTH_TOKENS_ODNOKLASSNIKI_PASSWORD = ''                                # user password

Покрытие методов API
--------------------

* [resolveScreenName](http://vk.com/dev/resolveScreenName) – определяет тип объекта (пользователь, группа, приложение) и его идентификатор по короткому имени screen_name;

Примеры использования
---------------------

### Запрос API

    >>> from odnoklassniki_api.api import api_call
    >>> api_call('url.getInfo', url='http://www.odnoklassniki.ru/apiok')
    {u'objectId': 53038939046008L, u'type': u'GROUP'}
