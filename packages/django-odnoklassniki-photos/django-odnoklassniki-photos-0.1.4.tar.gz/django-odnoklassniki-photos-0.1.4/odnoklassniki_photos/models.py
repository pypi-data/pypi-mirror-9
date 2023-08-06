# -*- coding: utf-8 -*-
from datetime import datetime

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.query import EmptyQuerySet
from django.utils import timezone
from django.utils.six import string_types
from m2m_history.fields import ManyToManyHistoryField
from odnoklassniki_api.decorators import atomic, fetch_all, fetch_by_chunks_of
from odnoklassniki_api.models import OdnoklassnikiManager, OdnoklassnikiPKModel, OdnoklassnikiTimelineManager
from odnoklassniki_users.models import User


class AlbumRemoteManager(OdnoklassnikiManager):
    fetch_album_limit = 100

    @fetch_all(pagination='pagingAnchor', has_more='hasMore')
    def get(self, *args, **kwargs):
        response = self.api_call(*args, **kwargs)

        if kwargs.get('count') and kwargs.get('all'):
            kwargs['count'] = self.__class__.fetch_photo_limit

        if kwargs.get('method') == 'get_one':
            response_data = [response.get('album')]
        else:
            response_data = response.pop('albums')

        return self.parse_response(response_data), response

    @atomic
    def fetch(self, group, **kwargs):
        """
        Req params:  ids | group | (group & album)
        Opt params: count - count of albums to fetch ( value <= fetch_album_limit )
        See: photos.getPhotos, photos.getInfo
        """
        from odnoklassniki_groups.models import Group

        if 'count' not in kwargs:
            kwargs['count'] = self.__class__.fetch_album_limit

        if not isinstance(group, Group):
            raise Exception('group parameter should be odnoklassniki_groups.models.Group object')

        kwargs['gid'] = group.pk
        kwargs['fields'] = self.get_request_fields('group_album', prefix=True)

        return super(AlbumRemoteManager, self).fetch(**kwargs)

    @atomic
    def fetch_group_specific(self, ids, *args, **kwargs):
        from odnoklassniki_groups.models import Group

        group = kwargs.pop('group', None)
        if not isinstance(group, Group):
            raise Exception(
                'This function needs group parameter (object of odnoklassniki_groups.models.Group) to get albums from')

        if not isinstance(ids, (list, tuple)):
            raise Exception('ids should be tuple or list of ints')

        kwargs['method'] = 'get_one'
        kwargs['gid'] = group.pk
        kwargs['fields'] = self.get_request_fields('group_album', prefix=True)

        result = EmptyQuerySet(model=Album)
        if kwargs.get('count'):
            ids = ids[:kwargs['count']]

        for id in ids:
            kwargs['aid'] = id
            result = super(AlbumRemoteManager, self).fetch(*args, **kwargs) | result

        return result


class Album(OdnoklassnikiPKModel):

    class Meta:
        verbose_name = u'Альбом фотографий Одноклассники'
        verbose_name_plural = u'Альбомы фотографий Одноклассники'

    methods_namespace = 'photos'

    remote_pk_field = 'aid'

    title = models.TextField()

    owner_name = models.TextField()

    owner_content_type = models.ForeignKey(ContentType, related_name='odnoklassniki_albums_owners')
    owner_id = models.BigIntegerField(db_index=True)
    owner = generic.GenericForeignKey('owner_content_type', 'owner_id')

    created = models.DateTimeField(null=True, db_index=True)
    updated = models.DateTimeField(null=True, db_index=True)

    photos_count = models.PositiveIntegerField(default=0)

    likes_count = models.PositiveIntegerField(default=0)
    last_like_date = models.DateTimeField(null=True)

    remote = AlbumRemoteManager(methods={
        'get': 'getAlbums',
        'get_one': 'getAlbumInfo',
    })

    @property
    def slug(self):
        return '%s/album/%s' % (self.owner.slug, self.id)

    def __unicode__(self):
        return self.title

    def parse(self, response):
        from odnoklassniki_groups.models import Group

        if response.get('author_name'):
            self.owner_name = response.pop('author_name')

        if response.get('author_type') not in ['GROUP', None]:
            raise NotImplementedError('Not implemented for author_type other than GROUP')

        if response.get('group_id'):
            self.owner_id = response.pop('group_id')
            self.owner = Group.objects.get(id=self.owner_id)

        if response.get('like_summary'):
            summary = response.pop('like_summary')
            self.likes_count = summary.get('count', 0)
            try:
                value = datetime.utcfromtimestamp(
                    int(summary['last_like_date_ms']) / 1000).replace(tzinfo=timezone.utc)
            except:
                value = None
            self.last_like_date = value

        return super(Album, self).parse(response)

    def fetch_photos(self, **kwargs):
        return Photo.remote.fetch(group=self.owner, album=self, **kwargs)


class PhotoRemoteManager(OdnoklassnikiTimelineManager):

    timeline_cut_fieldname = 'created'
    fetch_photo_limit = 100

    @fetch_all(has_more='hasMore')
    def get(self, **kwargs):
        if kwargs.get('count') and kwargs.get('all'):
            kwargs['count'] = self.fetch_photo_limit
        return super(PhotoRemoteManager, self).get(**kwargs), self.response

    def parse_response(self, response, extra_fields=None):
        response = response.pop('photos')
        return super(PhotoRemoteManager, self).parse_response(response, extra_fields)

    @atomic
    def fetch(self, **kwargs):
        """
        Params: group, album, [count]
        See: photos.getPhotos
        """
        from odnoklassniki_groups.models import Group

        group = kwargs.get('group')
        if not isinstance(group, Group):
            raise Exception('This function needs group parameter (object of odnoklassniki_groups.models.Group)')

        if 'album' in kwargs:
            return self._fetch_group_album(**kwargs)
        else:
            return self._fetch_all_for_group(**kwargs)

    @atomic
    @fetch_by_chunks_of(fetch_photo_limit)
    def fetch_group_specific(self, **kwargs):
        """
        Params: group,  ids
        Descr: Fetch list of photos
        See: photos.getInfo
        """
        from odnoklassniki_groups.models import Group

        group = kwargs.get('group')
        if not isinstance(group, Group):
            raise Exception('This function needs group parameter (object of odnoklassniki_groups.models.Group)')

        album = kwargs.get('album')
        if not isinstance(album, Album):
            raise Exception('album parameter should be odnoklassniki_photos.models.Album object')

        if not isinstance(kwargs['ids'], (tuple, list)):
            raise Exception('ids parameter should be int tuple or int list')

        kwargs['fields'] = Photo.remote.get_request_fields('group_photo', prefix=True)
        kwargs['method'] = 'get_specific'
        kwargs['photo_ids'] = ','.join(map(lambda i: str(i), kwargs['ids']))
        kwargs['gid'] = kwargs.pop('group').pk
        kwargs['aid'] = kwargs.pop('album').pk

        return super(PhotoRemoteManager, self).fetch(**kwargs)

    @atomic
    def _fetch_all_for_group(self, **kwargs):
        group = kwargs['group']
        albums = Album.remote.fetch(group)

        overall_result = EmptyQuerySet(model=Photo)
        last_result = EmptyQuerySet(model=Photo)
        overall_count = kwargs.get('count')
        for album in albums:
            if overall_count is not None and not kwargs.get('all'):
                overall_count -= len(last_result)
                kwargs['count'] = min(self.fetch_photo_limit, overall_count)
                if kwargs['count'] <= 0:
                    break
            else:
                kwargs['all'] = True

            kwargs['album'] = album
            last_result = self._fetch_group_album(**kwargs)
            overall_result = last_result | overall_result

        return overall_result

    @atomic
    def _fetch_group_album(self, **kwargs):
        kwargs_copy = dict(kwargs)
        album = kwargs_copy.pop('album')
        if not isinstance(album, Album):
            raise Exception('album parameter should be odnoklassniki_photos.models.Album object')

        group = kwargs_copy.pop('group')

        kwargs_copy['fields'] = Photo.remote.get_request_fields('group_photo', prefix=True)
        kwargs_copy['aid'] = album.pk
        kwargs_copy['gid'] = group.pk

        count = kwargs_copy.get('count')
        if count:
            if not kwargs_copy.get('all'):
                result = EmptyQuerySet(model=Photo)

                while count > 0:
                    kwargs_copy['count'] = min(self.fetch_photo_limit, count)
                    count -= kwargs_copy['count']
                    result = super(PhotoRemoteManager, self).fetch(**kwargs_copy) | result

                return result
            else:
                # set count to the highest available value to speed pagination
                kwargs_copy['count'] = self.fetch_photo_limit
                return super(PhotoRemoteManager, self).fetch(**kwargs_copy)
        else:
            # return all if count is not set
            kwargs_copy['all'] = True
            return super(PhotoRemoteManager, self).fetch(**kwargs_copy)


class Photo(OdnoklassnikiPKModel):

    class Meta:
        verbose_name = u'Фотография Одноклассники'
        verbose_name_plural = u'Фотографии Одноклассники'

    fetch_like_users_limit = 100

    methods_namespace = 'photos'
    remote_pk_field = 'id'

    album = models.ForeignKey(Album, related_name='photos')

    created = models.DateTimeField(null=True)

    actions_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    last_like_date = models.DateTimeField(null=True)
    like_users = ManyToManyHistoryField(User, related_name='like_photos')

    owner_content_type = models.ForeignKey(ContentType, related_name='odnoklassniki_photos_owners')
    owner_id = models.BigIntegerField(db_index=True)
    owner = generic.GenericForeignKey('owner_content_type', 'owner_id')

    owner_name = models.TextField()

    pic1024max = models.URLField(null=True)
    pic1024x768 = models.URLField(null=True)
    pic128max = models.URLField(null=True)
    pic128x128 = models.URLField(null=True)
    pic180min = models.URLField(null=True)
    pic190x190 = models.URLField(null=True)
    pic240min = models.URLField(null=True)
    pic320min = models.URLField(null=True)
    pic50x50 = models.URLField(null=True)
    pic640x480 = models.URLField(null=True)

    standard_height = models.PositiveIntegerField(default=0)
    standard_width = models.PositiveIntegerField(default=0)

    text = models.TextField()

    remote = PhotoRemoteManager(methods={
        'get': 'getPhotos',
        'get_specific': 'getInfo',
        'get_likes': 'getPhotoLikes',
    })

    def update_likes(self, instances, *args, **kwargs):
        users = User.objects.filter(pk__in=instances)
        self.like_users = users
        self.save()
        return users

    @atomic
    @fetch_all(return_all=update_likes, has_more=None)
    def fetch_likes(self, **kwargs):
        kwargs['photo_id'] = self.pk
        kwargs['gid'] = self.owner.pk

        if not kwargs.get('count'):
            kwargs['count'] = self.__class__.fetch_like_users_limit

        kwargs['fields'] = Photo.remote.get_request_fields('user', prefix=True)

        response = Photo.remote.api_call(method='get_likes', **kwargs)
        users = response.get('users')
        if users:
            users_ids = User.remote.get_or_create_from_resources_list(users).values_list('pk', flat=True)
        else:
            users_ids = EmptyQuerySet(model=User)

        return users_ids, response

    @property
    def slug(self):
        # Apparently there is no slug for a photo
        return '%s' % (self.album.slug, )

    def parse(self, response):
        from odnoklassniki_groups.models import Group

        self.owner_name = response.pop('author_name', u'')

        if response.get('author_type') not in ['GROUP', None]:
            raise NotImplementedError('Not implemented for author_type other than GROUP')

        if response.get('group_id'):
            self.owner_id = int(response.pop('group_id'))
            self.owner = Group.objects.get(id=self.owner_id)

        created = response.pop('created_ms', None)
        if created:
            response[u'created'] = created / 1000

        summary = response.pop('like_summary', None)
        if summary:
            self.likes_count = summary.get('count', 0)
            try:
                value = datetime.utcfromtimestamp(
                    int(summary['last_like_date_ms']) / 1000).replace(tzinfo=timezone.utc)
            except:
                value = None
            self.last_like_date = value

        if response.get('album_id'):
            self.album = Album.objects.get(id=int(response.get('album_id')))

        return super(Photo, self).parse(response)

    def save(self, *args, **kwargs):
        # if USE_TZ == False, we will get exception "TypeError: can't compare offset-naive and offset-aware datetimes"
        if self.album.updated and timezone.is_naive(self.album.updated):
            self.album.updated = self.album.updated.replace(tzinfo=self.created.tzinfo)

        if not self.album.updated or self.created > self.album.updated:
            self.album.updated = self.created
            self.album.save()

        self.actions_count = self.likes_count + self.comments_count
        return super(Photo, self).save(*args, **kwargs)
