# -*- coding: utf-8 -*-
import factory
from datetime import datetime
from odnoklassniki_groups.factories import GroupFactory
from .models import Photo, Album


class AlbumFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Album

    id = factory.Sequence(lambda n: n)
    created = datetime.now()

    owner = factory.SubFactory(GroupFactory)


class PhotoFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Photo

    id = factory.Sequence(lambda n: n)
    created = datetime.now()
    last_like_date = datetime.now()

    owner = factory.SubFactory(GroupFactory)
    album = factory.SubFactory(AlbumFactory)

    #like_users = ManyToManyHistoryField(User, related_name='like_photos')

