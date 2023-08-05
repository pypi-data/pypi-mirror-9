from django.conf import settings
from django.contrib.contenttypes import generic
from django.db import models
from m2m_history.fields import ManyToManyHistoryField
from odnoklassniki_api.decorators import atomic, fetch_all, opt_generator
from odnoklassniki_api.utils import get_improperly_configured_field


class UsersModelMixin(models.Model):

    class Meta:
        abstract = True

    if 'odnoklassniki_users' in settings.INSTALLED_APPS:
        from odnoklassniki_users.models import User
        users = ManyToManyHistoryField(User, versions=True)

        @atomic
        # @opt_generator
        def update_users(self, **kwargs):
            from odnoklassniki_users.models import User
            ids = self.__class__.remote.get_members_ids(group=self)
            first = self.users.versions.count() == 0

            self.users = User.remote.fetch(ids=ids)

            self.members_count = len(ids)
            self.save()

            if first:
                self.users.get_query_set_through().update(time_from=None)
                self.users.versions.update(added_count=0)

            return self.users.all()
    else:
        users = get_improperly_configured_field('odnoklassniki_users', True)
        update_users = get_improperly_configured_field('odnoklassniki_users')


class PhotosModelMixin(models.Model):

    class Meta:
        abstract = True

    if 'odnoklassniki_photos' in settings.INSTALLED_APPS:
        from odnoklassniki_photos.models import Album
        albums = generic.GenericRelation(Album, content_type_field='owner_content_type', object_id_field='owner_id')
        albums_count = models.PositiveIntegerField(null=True)

        def fetch_albums(self, **kwargs):
            from odnoklassniki_photos.models import Album
            return Album.remote.fetch(group=self, **kwargs)
    else:
        albums = get_improperly_configured_field('odnoklassniki_photos', True)
        albums_count = get_improperly_configured_field('odnoklassniki_photos', True)
        fetch_albums = get_improperly_configured_field('odnoklassniki_photos')


class DiscussionsModelMixin(models.Model):

    class Meta:
        abstract = True

    if 'odnoklassniki_discussions' in settings.INSTALLED_APPS:
        from odnoklassniki_discussions.models import Discussion
        discussions = generic.GenericRelation(
            Discussion, content_type_field='owner_content_type', object_id_field='owner_id')
        discussions_count = models.PositiveIntegerField(null=True)

        def fetch_discussions(self, **kwargs):
            from odnoklassniki_discussions.models import Discussion
            return Discussion.remote.fetch_group(group=self, **kwargs)
    else:
        discussions = get_improperly_configured_field('odnoklassniki_discussions', True)
        discussions_count = get_improperly_configured_field('odnoklassniki_discussions', True)
        fetch_discussions = get_improperly_configured_field('odnoklassniki_discussions')
