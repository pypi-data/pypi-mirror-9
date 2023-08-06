Django Odnoklassniki Photos
===========================

[![PyPI version](https://badge.fury.io/py/django-odnoklassniki-photos.png)](http://badge.fury.io/py/django-odnoklassniki-photos) [![Build Status](https://travis-ci.org/ramusus/django-odnoklassniki-photos.png?branch=master)](https://travis-ci.org/ramusus/django-odnoklassniki-photos) [![Coverage Status](https://coveralls.io/repos/ramusus/django-odnoklassniki-photos/badge.png?branch=master)](https://coveralls.io/r/ramusus/django-odnoklassniki-photos)

Приложение позволяет взаимодействовать с фотографиями и альбомами фотографий соц. сети Одноклассники, их статистикой и пользователями групп через OK API используя стандартные модели Django

Установка
---------

    pip install django-odnoklassniki-photos

В `settings.py` необходимо добавить:

    INSTALLED_APPS = (
        ...
        'oauth_tokens',
        'taggit',
        'odnoklassniki_api',
        'odnoklassniki_groups',
        'odnoklassniki_users',
        'odnoklassniki_photos',
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

* [photo.getAlbums](http://apiok.ru/wiki/display/api/photo.getAlbums) – получение списка альбомов группы;
* [photo.getAlbumInfo](http://apiok.ru/wiki/display/api/photo.getAlbumInfo) – получение информации по конкретному альбому;
* [photo.getAlbumLikes](http://apiok.ru/wiki/display/api/photo.getAlbumLikes) – получение списка пользователей поставивших "Класс" конкретному альбому;
* [photo.getInfo](http://apiok.ru/wiki/display/api/photo.getInfo) – получение информации по конкретной фотке;
* [photo.getPhotos](http://apiok.ru/wiki/display/api/photo.getPhotos) – получение списка фотографий альбома группы;
* [photo.getPhotoLikes](http://apiok.ru/wiki/display/api/photo.getPhotoLikes) – получение списка пользователей поставивших "Класс" конкретной фотке;

Примеры использования
---------------------

Все примеры использоания можно найти в тестах (test.py). Ниже краткий перечень

### Получение альбомов группы

    >>> from odnoklassniki_photos.models import Album
    >>> from odnoklassniki_groups.models import Group
    >>> group = Group.remote.fetch(ids=[50415375614101])[0]
    >>> Album.remote.fetch_group_specific(group=group, ids=[51836162801813, 51751246299285])
    [<Album: Album object>, <Album: Album object>]
    >>> Album.remote.fetch(group=group, all=True)
    [<Album: Album object>, <Album: Album object>, <Album: Album object>, ... ]

### Получение фотографий группы

    >>> from odnoklassniki_groups.models import Group
    >>> from odnoklassniki_photos.models import Album, Photo
    >>> group = Group.remote.fetch(ids=[50415375614101])[0]
    >>> album = Album.remote.fetch_group_specific(group=group, ids=[51836162801813])[0]
    >>> Photo.remote.fetch(group=group, album=album, all=True)
    [<Photo: Photo object>, <Photo: Photo object>, <Photo: Photo object>, ... ]

### Получение лайков фотографиии

Для этого необходимо установить дополнительно приложения:
[`django-odnoklassniki-users`](http://github.com/ramusus/django-odnoklassniki-users/) и добавить его в `INSTALLED_APPS`
[`django-m2m-history`](http://github.com/ramusus/django-m2m-history/)

    >>> from odnoklassniki_groups.models import Group
    >>> from odnoklassniki_photos.models import Album, Photo
    >>> group = Group.remote.fetch(ids=[44257342587000])[0]
    >>> album = Album.remote.fetch_group_specific(group=group, ids=[53047339778168])[0]
    >>> photo = Photo.remote.fetch_group_specific(group=group, album=album, ids=[545406014072])[0]
    >>> users = photo.fetch_likes()
    >>> users.count()
    146
