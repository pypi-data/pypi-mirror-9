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
GROUP1_ID = 51745210433673


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

        @mock.patch('odnoklassniki_users.models.UserRemoteManager.fetch', side_effect=user_fetch_mock)
        def test_group_add_members_ids_not_users(self, fetch):
            '''
            Without vkontakte_users in apps fetching group members doesn't trigger fetching users
            :param fetch:
            :return:
            '''
            apps = list(settings.INSTALLED_APPS)
            del apps[apps.index('odnoklassniki_users')]

            from odnoklassniki_users.models import User
            User.remote.fetch(ids=range(0, 500))

            group = GroupFactory(id=GROUP1_ID)
            with self.settings(**dict(INSTALLED_APPS=apps)):
                group.users = range(0, 1000)

            self.assertEqual(group.users.count(), 500)
            self.assertEqual(group.users.get_queryset().count(), 500)
            self.assertEqual(group.users.get_queryset_through().count(), 1000)
            self.assertItemsEqual(group.users.all(), User.objects.all())
            self.assertItemsEqual(group.users.get_queryset(only_pk=True), range(0, 1000))

        @mock.patch('odnoklassniki_users.models.UserRemoteManager.fetch', side_effect=user_fetch_mock)
        def test_fetch_group_members(self, fetch):
            from odnoklassniki_users.models import User

            group = GroupFactory(id=GROUP1_ID)

            self.assertEqual(User.objects.count(), 0)
            self.assertEqual(group.users.versions.count(), 0)

            with self.settings(**dict(ODNOKLASSNIKI_USERS_FETCH_USERS_ASYNC=False)):
                group.update_users()

            self.assertGreater(group.members_count, 4000)
            self.assertEqual(group.members_count, User.objects.count())
            self.assertEqual(group.members_count, group.users.count())

            self.assertEqual(group.users.versions.count(), 1)

            version = group.users.versions.all()[0]

            self.assertEqual(version.added_count, 0)
            self.assertEqual(version.removed_count, 0)

        @mock.patch('odnoklassniki_groups.models.GroupRemoteManager.get_members_ids')
        def test_group_members_changes(self, get_members_ids):

            apps = list(settings.INSTALLED_APPS)
            del apps[apps.index('odnoklassniki_users')]
            with self.settings(**dict(INSTALLED_APPS=apps)):

                group = GroupFactory(id=GROUP1_ID)

                def membership(id):
                    return group.users.get_queryset_through().get(user_id=id)

                def memberships(id):
                    return group.users.get_queryset_through().filter(user_id=id).order_by('id')

                def id90_state1():
                    self.assertEqual(membership(90).time_from, None)
                    self.assertEqual(membership(90).time_to, None)

                def id90_state2():
                    versions = group.users.versions.all()
                    self.assertEqual(membership(90).time_from, None)
                    self.assertEqual(membership(90).time_to, versions[1].time)

                def id90_state3():
                    versions = group.users.versions.all()
                    self.assertEqual(memberships(90)[0].time_from, None)
                    self.assertEqual(memberships(90)[0].time_to, versions[1].time)
                    self.assertEqual(memberships(90)[1].time_from, versions[2].time)
                    self.assertEqual(memberships(90)[1].time_to, None)

                def id90_state4():
                    versions = group.users.versions.all()
                    self.assertEqual(memberships(90)[0].time_from, None)
                    self.assertEqual(memberships(90)[0].time_to, versions[1].time)
                    self.assertEqual(memberships(90)[1].time_from, versions[2].time)
                    self.assertEqual(memberships(90)[1].time_to, None)

                def id90_state4_corrected():
                    versions = group.users.versions.all()
                    self.assertEqual(memberships(90)[0].time_from, None)
                    self.assertEqual(memberships(90)[0].time_to, versions[1].time)
                    self.assertEqual(memberships(90)[1].time_from, versions[3].time)
                    self.assertEqual(memberships(90)[1].time_to, None)

                def id0_state1():
                    self.assertEqual(memberships(0).count(), 0)

                def id0_state2():
                    versions = group.users.versions.all()
                    self.assertEqual(membership(0).time_from, versions[1].time)
                    self.assertEqual(membership(0).time_to, None)

                def id0_state3():
                    versions = group.users.versions.all()
                    self.assertEqual(membership(0).time_from, versions[1].time)
                    self.assertEqual(membership(0).time_to, versions[2].time)

                def id0_state3_corrected():
                    versions = group.users.versions.all()
                    self.assertEqual(membership(0).time_from, versions[1].time)
                    self.assertEqual(membership(0).time_to, versions[3].time)

                def id20_state1():
                    self.assertEqual(memberships(20).count(), 0)

                def id20_state2():
                    versions = group.users.versions.all()
                    self.assertEqual(membership(20).time_from, versions[1].time)
                    self.assertEqual(membership(20).time_to, None)

                def id20_state3():
                    versions = group.users.versions.all()
                    self.assertEqual(membership(20).time_from, versions[1].time)
                    self.assertEqual(membership(20).time_to, versions[2].time)

                def id20_state4():
                    versions = group.users.versions.all()
                    self.assertEqual(memberships(20)[0].time_from, versions[1].time)
                    self.assertEqual(memberships(20)[0].time_to, versions[2].time)
                    self.assertEqual(memberships(20)[1].time_from, versions[3].time)
                    self.assertEqual(memberships(20)[1].time_to, None)

                def id40_state1():
                    self.assertEqual(membership(40).time_from, None)
                    self.assertEqual(membership(40).time_to, None)

                def id40_state3():
                    self.assertEqual(membership(40).time_from, None)
                    self.assertEqual(membership(40).time_to, None)

                def id105_state1():
                    self.assertEqual(memberships(105).count(), 0)

                def id105_state3():
                    versions = group.users.versions.all()
                    self.assertEqual(membership(105).time_from, versions[2].time)
                    self.assertEqual(membership(105).time_to, None)

                def id105_state4():
                    versions = group.users.versions.all()
                    self.assertEqual(membership(105).time_from, versions[2].time)
                    self.assertEqual(membership(105).time_to, versions[3].time)

                get_members_ids.side_effect = lambda group: map(str, range(30, 100))
                group.update_users(check_count=False)
                self.assertEqual(group.users.get_queryset_through().count(), 70)
                id0_state1()
                id20_state1()
                id40_state1()
                id90_state1()
                id105_state1()

                get_members_ids.side_effect = lambda group: map(str, range(0, 50))
                group.update_users(check_count=False)
                self.assertEqual(group.users.get_queryset_through().count(), 100)
                id0_state2()
                id20_state2()
                id40_state1()
                id90_state2()
                id105_state1()

                get_members_ids.side_effect = lambda group: map(str, range(30, 110))
                group.update_users(check_count=False)
                self.assertEqual(group.users.get_queryset_through().count(), 160)
                id0_state3()
                id20_state3()
                id40_state3()
                id90_state3()
                id105_state3()

                get_members_ids.side_effect = lambda group: map(str, range(15, 100))
                group.update_users(check_count=False)
                self.assertEqual(group.users.get_queryset_through().count(), 175)
                id0_state3()
                id20_state4()
                id40_state3()
                id90_state4()
                id105_state4()

                return

                # hide migration3
                migration3 = GroupMigration.objects.get(id=migration3.id)
                migration3.hide()
                self.assertEqual(group.users.get_queryset_through().count(), 150)
                id0_state3_corrected()
                id20_state2()
                id40_state1()
                id90_state4_corrected()
                id105_state1()

                # hide migration4 -> back to state2
                migration4 = GroupMigration.objects.get(id=migration4.id)
                migration4.hide()
                self.assertEqual(group.users.get_queryset_through().count(), 100)
                id0_state2()
                id20_state2()
                id40_state1()
                id90_state2()
                id105_state1()

                # hide migration2 -> back to state1
                migration2 = GroupMigration.objects.get(id=migration2.id)
                migration2.hide()
                self.assertEqual(group.users.get_queryset_through().count(), 70)
                id0_state1()
                id20_state1()
                id40_state1()
                id90_state1()
                id105_state1()
