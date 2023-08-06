# -*- coding: utf-8 -*-
from datetime import datetime, date

from django.test import TestCase
from django.utils import timezone
from odnoklassniki_api.api import OdnoklassnikiError
from odnoklassniki_groups.factories import GroupFactory
from odnoklassniki_users.factories import UserFactory
from odnoklassniki_users.models import User
import simplejson as json

from .factories import AlbumFactory, PhotoFactory
from .models import Album, Photo

# ria news
GROUP_ID = 50415375614101
# sakura blossom
ALBUM1_ID = 51836162801813
# ISS return
ALBUM2_ID = 51751246299285
# Day in History
ALBUM_BIG_ID = 51324428026005
# Day: 23rd of January
PHOTO_ID = 544442732181

# cocacola
GROUP_SMALL_ID = 53129767747696
# Ваши фотографии с Coca-Cola
ALBUM_BIG2_ID = 53169390747760
# some photos from album above
PHOTO1_ID = 585084794224
PHOTO2_ID = 584955983472

# Haag discussion
DISCUSSION_ID = 62575868474773


class OdnoklassnikiPhotosTest(TestCase):

    def test_album_fetch(self):
        group = GroupFactory(id=GROUP_ID)

        self.assertEqual(Album.objects.count(), 0)

        albums = Album.remote.fetch(group=group, all=True)
        self.assertTrue(len(albums) > 360)
        self.assertEqual(Album.objects.count(), len(albums))

        albums2 = Album.remote.fetch_group_specific(group=group, ids=[ALBUM1_ID, ALBUM2_ID])
        self.assertEqual(len(albums2), 2)
        self.assertTrue(set(albums2).issubset(set(albums)))
        for album in albums2:
            self.assertEqual(album, albums.filter(id=album.id)[0])
            self.assertEqual(album.owner, group)
            self.assertTrue(album.likes_count > 0)
            self.assertTrue(album.last_like_date is not None)
            self.assertTrue(album.created is not None)
            self.assertTrue(len(album.owner_name) > 0)
            self.assertTrue(len(album.title) > 0)

        # test count is working
        albums_part = Album.remote.fetch(group=group, count=40)
        self.assertTrue(albums_part.count() < 40)
        self.assertTrue(albums_part.count() > 0)

        # test if count is more than max
        self.assertRaises(OdnoklassnikiError, Album.remote.fetch, group=group,
                          count=Album.remote.__class__.fetch_album_limit + 20)

        # test fetch with default count
        albums_part2 = Album.remote.fetch(group=group)
        self.assertTrue(albums_part2.count() < Album.remote.__class__.fetch_album_limit)

        # test all entities returned, not 90
        albums_all = Album.remote.fetch(group=group, count=90, all=True)
        self.assertTrue(albums_all.count() > 360)

        # no group provided
        self.assertRaises(Exception, Album.remote.fetch, all=True)
        # group should be Group object
        self.assertRaises(Exception, Album.remote.fetch, group=11)
        self.assertRaises(Exception, Album.remote.fetch, group='')

    def test_album_fetch_specific(self):
        group = GroupFactory(id=GROUP_ID)

        # test count is working with ids
        album1 = Album.remote.fetch_group_specific(group=group, count=1, ids=[ALBUM1_ID, ALBUM2_ID])
        self.assertEqual(album1.count(), 1)

        # test can fetch one album with specific id
        album1 = Album.remote.fetch_group_specific(group=group, ids=[ALBUM1_ID])
        self.assertEqual(album1.count(), 1)

        # "all" attr is not applicable here
        albums_not_all = Album.remote.fetch_group_specific(group=group, ids=[ALBUM1_ID, ALBUM2_ID], all=True)
        self.assertEqual(albums_not_all.count(), 2)

        # group should be Group object
        self.assertRaises(Exception, Album.remote.fetch_group_specific, group=11)
        self.assertRaises(Exception, Album.remote.fetch_group_specific, group=group, ids=11)

    def test_album_fetch_photos(self):

        self.assertEqual(Album.objects.count(), 0)
        self.assertEqual(Photo.objects.count(), 0)

        group = GroupFactory(id=GROUP_ID)
        album = AlbumFactory(id=ALBUM_BIG_ID, owner=group)
        photos = album.fetch_photos(count=50)
        self.assertEqual(photos.count(), 50)
        self.assertEqual(photos.count(), Photo.objects.count())

        Photo.objects.all().delete()

        photos = album.fetch_photos(all=True)
        self.assertGreater(photos.count(), 300)
        self.assertEqual(photos.count(), Photo.objects.count())

        album = Album.objects.get(pk=album.pk)
        self.assertNotEqual(album.updated, None)

    def test_album_fetch_photos_after_before(self):

        group = GroupFactory(id=GROUP_ID)
        album = AlbumFactory(id=ALBUM_BIG_ID, owner=group)

        # test `after` argument
        after = datetime(2013, 9, 13, 5, 20, 25).replace(tzinfo=timezone.utc)
        photos_after = album.fetch_photos(all=True, after=after)
        self.assertLess(photos_after.count(), 50)
        self.assertEqual(photos_after.count(), 41)
        self.assertEqual(photos_after.filter(created__lt=after).count(), 0)

        # # test `before` argument
        # before = datetime(2013, 9, 28, 5, 16, 54).replace(tzinfo=timezone.utc)
        # photos_before = album.fetch_photos(all=True, after=after, before=before)
        # self.assertLess(photos_before.count(), photos_after.count())
        # self.assertEqual(photos_before.count(), 10)
        # self.assertEqual(photos_before.filter(created__gt=before).count(), 0)

    def test_album_parse(self):
        response = '''{"albums":
            [{"photos_count": 335,
              "created": "2012-09-22",
              "title": "\u0414\u0435\u043d\u044c \u0432 \u0438\u0441\u0442\u043e\u0440\u0438\u0438",
              "author_name": "\u0420\u0418\u0410 \u041d\u043e\u0432\u043e\u0441\u0442\u0438",
              "like_count": 8555,
              "attrs": {"flags": "l"},
              "liked_it": false,
              "like_summary": {"count": 8555, "like_possible": true, "self": false, "like_id": "nhIyoINYykF3rWr8_88J9A", "unlike_possible": true, "last_like_date_ms": 1399567588656},
              "aid": "51324428026005",
              "group_id": "50415375614101",
              "author_type": "GROUP"
            }]}
            '''
        instance = Album()
        group = GroupFactory(id=GROUP_ID)
        instance.parse(json.loads(response)['albums'][0])
        instance.save()

        self.assertEqual(instance.id, 51324428026005)
        self.assertEqual(instance.owner_name, u'\u0420\u0418\u0410 \u041d\u043e\u0432\u043e\u0441\u0442\u0438')
        self.assertEqual(instance.last_like_date, datetime(2014, 5, 8, 16, 46, 28, tzinfo=timezone.utc))
        self.assertEqual(instance.owner, group)
        self.assertIsInstance(instance.created, datetime)

    def test_group_fetch_albums(self):
        group = GroupFactory(id=GROUP_ID)

        albums = group.fetch_albums(all=True)

        self.assertTrue(len(albums) > 360)
        self.assertEqual(Album.objects.count(), len(albums))

    def test_photo_fetch(self):
        group_big = GroupFactory(id=GROUP_ID)
        album = AlbumFactory(id=ALBUM_BIG_ID, owner=group_big)
        group_small = GroupFactory(id=GROUP_SMALL_ID)
        album2 = AlbumFactory(id=ALBUM_BIG2_ID, owner=group_small)

        self.assertEqual(Album.objects.count(), 2)

        # group should be Group object
        self.assertRaises(Exception, Photo.remote.fetch, group=11)
        self.assertRaises(Exception, Photo.remote.fetch, group='')

        # get all
        photos_all = Photo.remote.fetch(group=group_small, all=True)
        self.assertTrue(len(photos_all) > 0)
        self.assertEqual(Photo.objects.count(), len(photos_all))

        Photo.objects.all().delete()
        self.assertEqual(Photo.objects.count(), 0)

        # get all photos of an album
        photos_album_all = Photo.remote.fetch(group=group_big, album=album, all=True)
        self.assertTrue(len(photos_album_all) > 0)
        self.assertEqual(Photo.objects.count(), len(photos_album_all))

        Photo.objects.all().delete()

        # "all" overrides count
        photos_album_all2 = Photo.remote.fetch(group=group_big, album=album, count=230, all=True)
        self.assertEqual(len(photos_album_all2), len(photos_album_all))
        self.assertEqual(Photo.objects.count(), len(photos_album_all2))

        Photo.objects.all().delete()

        # get no more than count photos of a group
        photos_group_part = Photo.remote.fetch(group=group_small, count=110)
        self.assertEqual(len(photos_group_part), 110)
        self.assertEqual(Photo.objects.count(), len(photos_group_part))

        Photo.objects.all().delete()

        # "count" == limit
        photos = Photo.remote.fetch(group=group_small, count=Photo.remote.__class__.fetch_photo_limit)
        self.assertEqual(len(photos), Photo.remote.__class__.fetch_photo_limit)

        Photo.objects.all().delete()

        # "count" < limit
        photos = Photo.remote.fetch(group=group_small, count=50)
        self.assertEqual(len(photos), 50)

        Photo.objects.all().delete()

        # test fetch group photos with no count specified == all photos
        photos_all3 = Photo.remote.fetch(group=group_small)
        self.assertEqual(photos_all3.count(), len(photos_all))

        Photo.objects.all().delete()

        # test fetch album photos with default count
        photos_album_all3 = Photo.remote.fetch(group=group_small, album=album2, all=True)
        album_count = len(photos_album_all3)

        Photo.objects.all().delete()

        photos_album_all4 = Photo.remote.fetch(group=group_small, album=album2)
        self.assertEqual(photos_album_all4.count(), album_count)

        Photo.objects.all().delete()

        # get no more than count photos of a group
        photos_group_album_part = Photo.remote.fetch(group=group_small, album=album2, count=110)
        self.assertTrue(len(photos_group_album_part) > 0)
        self.assertEqual(Photo.objects.count(), len(photos_group_album_part))

        Photo.objects.all().delete()

        # "count" == limit
        photos = Photo.remote.fetch(group=group_small, album=album2, count=100)
        self.assertEqual(len(photos), 100)  # strange, but sometimes here 99

        Photo.objects.all().delete()

        # "count" < limit
        photos = Photo.remote.fetch(group=group_small, album=album2, count=50)
        self.assertEqual(len(photos), 50)

        Photo.objects.all().delete()

        # album should be Album object
        self.assertRaises(Exception, Photo.remote.fetch, group=group_small, album=11)
        self.assertRaises(Exception, Photo.remote.fetch, group=group_small, album='')

        # no group provided
        self.assertRaises(Exception, Album.remote.fetch, all=True)

    def test_photo_fetch_group_specific(self):
        group = GroupFactory(id=GROUP_SMALL_ID)
        album = AlbumFactory(id=ALBUM_BIG2_ID, owner=group)

        self.assertEqual(Album.objects.count(), 1)

        # group should be Group object
        self.assertRaises(Exception, Photo.remote.fetch_group_specific, group=11)
        self.assertRaises(Exception, Photo.remote.fetch_group_specific, group='')

        # "album" argument should present
        self.assertRaises(Exception, Photo.remote.fetch_group_specific, group=group, ids=[PHOTO1_ID, PHOTO2_ID])

        # "album" should be Album object
        self.assertRaises(Exception, Photo.remote.fetch_group_specific,
                          group=group, album=11, ids=[PHOTO1_ID, PHOTO2_ID])

        # "ids" argument should present
        self.assertRaises(Exception, Photo.remote.fetch_group_specific, group=group)
        # "ids" should be list or tuple
        self.assertRaises(Exception, Photo.remote.fetch_group_specific, group=group, ids=111)

        photos = Photo.remote.fetch_group_specific(group=group, album=album, ids=[PHOTO1_ID, PHOTO2_ID])

        self.assertEqual(len(photos), 2)
        self.assertEqual(Photo.objects.count(), len(photos))

    def test_photo_fetch_likes(self, *kwargs):
        group = GroupFactory(id=GROUP_ID)
        album = AlbumFactory(id=ALBUM_BIG_ID, owner=group)

        photo = Photo.remote.fetch_group_specific(group=group, album=album, ids=[PHOTO_ID])[0]

        self.assertEqual(photo.like_users.count(), 0)

        users = photo.fetch_likes(count=50)

        self.assertEqual(50, len(users))
        self.assertEqual(50, User.objects.count())

        users = photo.fetch_likes(all=True)

        self.assertGreater(users.count(), User.remote.__class__.fetch_users_limit)
        # TODO: because API returns 146 users instead of all 147 -- 1 less. Forced to do this kind of checks
        self.assertEqual(users.count(), photo.likes_count - 1)

        self.assertEqual(users.count(), User.objects.count())
        self.assertEqual(users.count(), photo.like_users.count())

    def test_photo_parse(self):
        response = '''{"photos":
            [{"album_id": "51324428026005",
             "standard_height": 768,
             "created_ms": 1390456312257,
             "author_name": "\u0420\u0418\u0410 \u041d\u043e\u0432\u043e\u0441\u0442\u0438",
             "like_count": 147,
             "attrs": {"flags": "l,s"},
             "pic180min": "http://itd2.mycdn.me/getImage?photoId=544442732181&photoType=13&viewToken=zTBy6mruu-TknmDenjXlwg",
             "like_summary": {"count": 147, "like_possible": true, "self": false, "like_id": "7QQmgWn6-sgl9skZmB4Rsg07GJziF49kdwtS94a7c3s", "unlike_possible": true, "last_like_date_ms": 1397655462641},
             "id": "544442732181",
             "pic50x50": "http://groupava1.mycdn.me/getImage?photoId=544442732181&photoType=4&viewToken=zTBy6mruu-TknmDenjXlwg",
             "standard_width": 768,
             "text": "\u0415\u0441\u043b\u0438 \u0432\u044b \u0434\u0430\u0432\u043d\u043e \u043d\u0435 \u043f\u0438\u0441\u0430\u043b\u0438 \u043a\u043e\u043c\u0443-\u043d\u0438\u0431\u0443\u0434\u044c \u0440\u0443\u043a\u043e\u043f\u0438\u0441\u043d\u044b\u0435 \u043f\u043e\u0441\u043b\u0430\u043d\u0438\u044f \u2014 \u0441\u0435\u0433\u043e\u0434\u043d\u044f \u0435\u0441\u0442\u044c \u043f\u043e\u0432\u043e\u0434: \u0432 \u043c\u0438\u0440\u0435 \u043e\u0442\u043c\u0435\u0447\u0430\u044e\u0442 \u0414\u0435\u043d\u044c \u0440\u0443\u0447\u043d\u043e\u0433\u043e \u043f\u0438\u0441\u044c\u043c\u0430 \u0438\u043b\u0438, \u043f\u0440\u043e\u0449\u0435 \u0433\u043e\u0432\u043e\u0440\u044f, \u043f\u043e\u0447\u0435\u0440\u043a\u0430, \u043a\u043e\u0442\u043e\u0440\u044b\u0439 \u0443 \u043a\u0430\u0436\u0434\u043e\u0433\u043e \u0447\u0435\u043b\u043e\u0432\u0435\u043a\u0430 \u0443\u043d\u0438\u043a\u0430\u043b\u0435\u043d.",
             "discussion_summary": {"discussion_type": "GROUP_PHOTO", "comments_count": 4, "discussion_id": "544442732181"},
             "author_type": "GROUP",
             "pic640x480": "http://dg52.mycdn.me/getImage?photoId=544442732181&photoType=0&viewToken=zTBy6mruu-TknmDenjXlwg",
             "pic1024max": "http://dg52.mycdn.me/getImage?photoId=544442732181&photoType=3&viewToken=zTBy6mruu-TknmDenjXlwg",
             "liked_it": false,
             "pic320min": "http://itd2.mycdn.me/getImage?photoId=544442732181&photoType=15&viewToken=zTBy6mruu-TknmDenjXlwg",
             "pic1024x768": "http://dg52.mycdn.me/getImage?photoId=544442732181&photoType=3&viewToken=zTBy6mruu-TknmDenjXlwg",
             "pic128x128": "http://itd2.mycdn.me/getImage?photoId=544442732181&photoType=23&viewToken=zTBy6mruu-TknmDenjXlwg",
             "pic240min": "http://itd2.mycdn.me/getImage?photoId=544442732181&photoType=14&viewToken=zTBy6mruu-TknmDenjXlwg",
             "comments_count": 4,
             "pic128max": "http://dg52.mycdn.me/getImage?photoId=544442732181&photoType=2&viewToken=zTBy6mruu-TknmDenjXlwg",
             "group_id": "50415375614101"}]}
            '''
        instance = Photo()
        group = GroupFactory(id=GROUP_ID)
        album = AlbumFactory(id=ALBUM_BIG_ID, owner=group)
        instance.parse(json.loads(response)['photos'][0])
        instance.save()

        self.assertEqual(instance.id, 544442732181)
        self.assertEqual(instance.created, datetime(2014, 1, 23, 5, 51, 52, tzinfo=timezone.utc))
        self.assertEqual(instance.owner_name, u'\u0420\u0418\u0410 \u041d\u043e\u0432\u043e\u0441\u0442\u0438')
        self.assertEqual(instance.likes_count, 147)
        self.assertEqual(instance.comments_count, 4)
        self.assertEqual(instance.last_like_date, datetime(2014, 4, 16, 13, 37, 42, tzinfo=timezone.utc))
        self.assertEqual(
            instance.pic1024max, u'http://dg52.mycdn.me/getImage?photoId=544442732181&photoType=3&viewToken=zTBy6mruu-TknmDenjXlwg')
        self.assertEqual(
            instance.pic1024x768, u'http://dg52.mycdn.me/getImage?photoId=544442732181&photoType=3&viewToken=zTBy6mruu-TknmDenjXlwg')
        self.assertEqual(
            instance.pic128max, u'http://dg52.mycdn.me/getImage?photoId=544442732181&photoType=2&viewToken=zTBy6mruu-TknmDenjXlwg')
        self.assertEqual(
            instance.pic128x128, u'http://itd2.mycdn.me/getImage?photoId=544442732181&photoType=23&viewToken=zTBy6mruu-TknmDenjXlwg')
        self.assertEqual(
            instance.pic180min, u'http://itd2.mycdn.me/getImage?photoId=544442732181&photoType=13&viewToken=zTBy6mruu-TknmDenjXlwg')
        self.assertEqual(
            instance.pic240min, u'http://itd2.mycdn.me/getImage?photoId=544442732181&photoType=14&viewToken=zTBy6mruu-TknmDenjXlwg')
        self.assertEqual(
            instance.pic50x50, u'http://groupava1.mycdn.me/getImage?photoId=544442732181&photoType=4&viewToken=zTBy6mruu-TknmDenjXlwg')
        self.assertEqual(
            instance.pic640x480, u'http://dg52.mycdn.me/getImage?photoId=544442732181&photoType=0&viewToken=zTBy6mruu-TknmDenjXlwg')
        self.assertEqual(instance.standard_height, 768)
        self.assertEqual(instance.standard_width, 768)
        self.assertEqual(
            instance.text, u'\u0415\u0441\u043b\u0438 \u0432\u044b \u0434\u0430\u0432\u043d\u043e \u043d\u0435 \u043f\u0438\u0441\u0430\u043b\u0438 \u043a\u043e\u043c\u0443-\u043d\u0438\u0431\u0443\u0434\u044c \u0440\u0443\u043a\u043e\u043f\u0438\u0441\u043d\u044b\u0435 \u043f\u043e\u0441\u043b\u0430\u043d\u0438\u044f \u2014 \u0441\u0435\u0433\u043e\u0434\u043d\u044f \u0435\u0441\u0442\u044c \u043f\u043e\u0432\u043e\u0434: \u0432 \u043c\u0438\u0440\u0435 \u043e\u0442\u043c\u0435\u0447\u0430\u044e\u0442 \u0414\u0435\u043d\u044c \u0440\u0443\u0447\u043d\u043e\u0433\u043e \u043f\u0438\u0441\u044c\u043c\u0430 \u0438\u043b\u0438, \u043f\u0440\u043e\u0449\u0435 \u0433\u043e\u0432\u043e\u0440\u044f, \u043f\u043e\u0447\u0435\u0440\u043a\u0430, \u043a\u043e\u0442\u043e\u0440\u044b\u0439 \u0443 \u043a\u0430\u0436\u0434\u043e\u0433\u043e \u0447\u0435\u043b\u043e\u0432\u0435\u043a\u0430 \u0443\u043d\u0438\u043a\u0430\u043b\u0435\u043d.')
        self.assertEqual(instance.owner, group)
        self.assertEqual(instance.album, album)
