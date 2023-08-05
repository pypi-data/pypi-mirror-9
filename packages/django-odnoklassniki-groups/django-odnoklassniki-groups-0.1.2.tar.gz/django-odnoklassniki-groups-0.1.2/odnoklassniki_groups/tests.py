# -*- coding: utf-8 -*-
import mock
import simplejson as json
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from odnoklassniki_users.tests import user_fetch_mock

from .factories import GroupFactory
from .models import Group

GROUP_ID = 47241470410797
GROUP_NAME = u'Кока-Кола'

GROUP_OPEN_ID = 53038939046008


class OdnoklassnikiGroupsTest(TestCase):

    def test_get_by_url(self):

        user = GroupFactory(id=GROUP_OPEN_ID)

        self.assertEqual(Group.objects.count(), 1)

        urls = (
            'http://ok.ru/apiok/',
            'http://ok.ru/apiok',
            'http://odnoklassniki.ru/apiok',
            'http://www.odnoklassniki.ru/apiok',
            'http://www.odnoklassniki.ru/group/53038939046008',
        )

        for url in urls:
            instance = Group.remote.get_by_url(url)
            self.assertEqual(instance.id, GROUP_OPEN_ID)

    def test_refresh_group(self):

        instance = Group.remote.fetch(ids=[GROUP_ID])[0]
        self.assertEqual(instance.name, GROUP_NAME)

        instance.name = 'temp'
        instance.save()
        self.assertEqual(instance.name, 'temp')

        instance.refresh()
        self.assertEqual(instance.name, GROUP_NAME)

    def test_fetch_groups(self):

        self.assertEqual(Group.objects.count(), 0)
        instance = Group.remote.fetch(ids=[GROUP_ID])[0]

        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(instance.id, GROUP_ID)
        self.assertEqual(instance.name, GROUP_NAME)

    def test_parse_group(self):

        response = u'''[{
                    "uid": "53923499278353",
                    "name": "Группа для тестирования нового сервиса",
                    "description": "Группа для тестирования нового сервиса",
                    "shortname": "newservicetesting",
                    "picAvatar": "http://groupava2.odnoklassniki.ru/getImage?photoId=476991575825&photoType=4",
                    "shop_visible_admin": false,
                    "shop_visible_public": false,
                    "members_count": 12463
                }]'''
        instance = Group()
        instance.parse(json.loads(response)[0])
        instance.save()

        self.assertEqual(instance.id, 53923499278353)
        self.assertEqual(instance.name, u'Группа для тестирования нового сервиса')
        self.assertEqual(instance.description, u'Группа для тестирования нового сервиса')
        self.assertEqual(instance.shortname, 'newservicetesting')
        self.assertEqual(
            instance.pic50x50, 'http://groupava2.odnoklassniki.ru/getImage?photoId=476991575825&photoType=4')
        self.assertEqual(instance.shop_visible_admin, False)
        self.assertEqual(instance.shop_visible_public, False)
        self.assertEqual(instance.members_count, 12463)

    def test_raise_users_exception(self):

        group = GroupFactory(id=GROUP_ID)
        if 'odnoklassniki_users' in settings.INSTALLED_APPS:
            group.users
        else:
            with self.assertRaises(ImproperlyConfigured):
                group.users

    def test_get_group_members_ids(self):

        group = GroupFactory(id=GROUP_OPEN_ID)
        ids = Group.remote.get_members_ids(group=group)

        self.assertGreater(len(ids), 18000)

    if 'odnoklassniki_users' in settings.INSTALLED_APPS:

        @mock.patch('odnoklassniki_api.models.OdnoklassnikiManager.fetch', side_effect=user_fetch_mock)
        def test_fetch_group_members(self, fetch):
            from odnoklassniki_users.models import User

            group = GroupFactory(id=GROUP_OPEN_ID)

            self.assertEqual(User.objects.count(), 0)
            self.assertEqual(group.users.versions.count(), 0)

            users = group.update_users()

            self.assertGreater(group.members_count, 18000)
            self.assertEqual(group.members_count, User.objects.count())
            self.assertEqual(group.members_count, users.count())
            self.assertEqual(group.members_count, group.users.count())

            self.assertEqual(group.users.versions.count(), 1)

            version = group.users.versions.all()[0]

            self.assertEqual(version.added_count, 0)
            self.assertEqual(version.removed_count, 0)
