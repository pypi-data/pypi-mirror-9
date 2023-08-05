Django Vkontakte Wall Statistic
===============================

[![PyPI version](https://badge.fury.io/py/django-vkontakte-wall-statistic.png)](http://badge.fury.io/py/django-vkontakte-wall-statistic) [![Build Status](https://travis-ci.org/ramusus/django-vkontakte-wall-statistic.png?branch=master)](https://travis-ci.org/ramusus/django-vkontakte-wall-statistic) [![Coverage Status](https://coveralls.io/repos/ramusus/django-vkontakte-wall-statistic/badge.png?branch=master)](https://coveralls.io/r/ramusus/django-vkontakte-wall-statistic)

Приложение позволяет взаимодействовать со статистикой сообщений Вконтакте через Вконтакте API и парсер используя стандартные модели Django

Установка
---------

    pip install django-vkontakte-wall-statistic

В `settings.py` необходимо добавить:

    INSTALLED_APPS = (
        ...
        'oauth_tokens',
        'taggit',
        'vkontakte_api',
        'vkontakte_users',
        'vkontakte_groups',
        'vkontakte_wall',
        'vkontakte_wall_statistic',
        'm2m_history',
    )

    # oauth-tokens settings
    OAUTH_TOKENS_HISTORY = True                                         # to keep in DB expired access tokens
    OAUTH_TOKENS_VKONTAKTE_CLIENT_ID = ''                               # application ID
    OAUTH_TOKENS_VKONTAKTE_CLIENT_SECRET = ''                           # application secret key
    OAUTH_TOKENS_VKONTAKTE_SCOPE = ['ads,wall,photos,friends,stats']    # application scopes
    OAUTH_TOKENS_VKONTAKTE_USERNAME = ''                                # user login
    OAUTH_TOKENS_VKONTAKTE_PASSWORD = ''                                # user password
    OAUTH_TOKENS_VKONTAKTE_PHONE_END = ''                               # last 4 digits of user mobile phone

Покрытие методов API
--------------------

* [stats.get](http://vk.com/dev/stats.getPostStats) – возвращает статистику рекламной записи сообщества;

Примеры использования
---------------------

### Получение статистики сообщения

    >>> from vkontakte_wall.models import Post
    >>> from datetime import date, timedelta
    >>> post = Post.objects.get(remote_id=...)
    >>> post.fetch_statistic(date_from=date.today()-timedelta(1), date_to=date.today())

Статистика, полученная через API доступна через менеджер

    >>> stat = post.statistics.all()[0]
    >>> stat.__dict__
    {'_state': <django.db.models.base.ModelState at 0x9b5e34c>,
     'date': datetime.date(2014, 2, 23),
     'fetched': datetime.datetime(2014, 2, 27, 22, 18, 26, 628260),
     'id': 200,
     'link_clicks': 0,
     'period': 1,
     'post_id': 229537,
     'reach': 1,
     'reach_age_18': 0,
     'reach_age_18_21': 0,
     'reach_age_21_24': 0,
     'reach_age_24_27': 0,
     'reach_age_27_30': 0,
     'reach_age_30_35': 0,
     'reach_age_35_45': 0,
     'reach_age_45': 0,
     'reach_females': 1,
     'reach_females_age_18': 0,
     'reach_females_age_18_21': 0,
     'reach_females_age_21_24': 0,
     'reach_females_age_24_27': 0,
     'reach_females_age_27_30': 0,
     'reach_females_age_30_35': 0,
     'reach_females_age_35_45': 0,
     'reach_females_age_45': 0,
     'reach_males': 0,
     'reach_males_age_18': 0,
     'reach_males_age_18_21': 0,
     'reach_males_age_21_24': 0,
     'reach_males_age_24_27': 0,
     'reach_males_age_27_30': 0,
     'reach_males_age_30_35': 0,
     'reach_males_age_35_45': 0,
     'reach_males_age_45': 0,
     'reach_subscribers': 0}
