Django Odnoklassniki Users
==========================

[![PyPI version](https://badge.fury.io/py/django-odnoklassniki-users.png)](http://badge.fury.io/py/django-odnoklassniki-users) [![Build Status](https://travis-ci.org/ramusus/django-odnoklassniki-users.png?branch=master)](https://travis-ci.org/ramusus/django-odnoklassniki-users) [![Coverage Status](https://coveralls.io/repos/ramusus/django-odnoklassniki-users/badge.png?branch=master)](https://coveralls.io/r/ramusus/django-odnoklassniki-users)

Приложение позволяет взаимодействовать с профилями пользователей Вконтакте через Вконтакте API используя стандартные модели Django

Установка
---------

    pip install django-odnoklassniki-users

В `settings.py` необходимо добавить:

    INSTALLED_APPS = (
        ...
        'oauth_tokens',
        'taggit',
        'odnoklassniki_api',
        'odnoklassniki_users',
    )

    # oauth-tokens settings
    OAUTH_TOKENS_HISTORY = True                                             # to keep in DB expired access tokens
    OAUTH_TOKENS_ODNOKLASSNIKI_CLIENT_ID = 12345678                         # application id
    OAUTH_TOKENS_ODNOKLASSNIKI_CLIENT_PUBLIC = ''                           # application public key
    OAUTH_TOKENS_ODNOKLASSNIKI_CLIENT_SECRET = ''                           # application secret key
    OAUTH_TOKENS_ODNOKLASSNIKI_SCOPE = ['']                                 # application scopes
    OAUTH_TOKENS_ODNOKLASSNIKI_USERNAME = ''                                # user login
    OAUTH_TOKENS_ODNOKLASSNIKI_PASSWORD = ''                                # user password

Покрытие методов API
--------------------

* [users.getInfo](http://apiok.ru/wiki/display/api/users.getInfo) – возвращает большой массив информации, связанной с пользователем, для каждого переданного идентификатора пользователя;

Примеры использования
---------------------

### Получение пользователей по ID

    >>> from odnoklassniki_users.models import User
    >>> User.remote.fetch(ids=[561348705024,578592731938])
    [<User: Евгений Дуров>,
     <User: Михаил Коммуникатов>]