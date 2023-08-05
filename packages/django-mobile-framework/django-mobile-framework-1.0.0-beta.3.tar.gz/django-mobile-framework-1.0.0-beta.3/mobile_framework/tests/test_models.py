import uuid
from datetime import datetime
from django.test import TestCase
from uuidfield.fields import StringUUID
from mobile_framework.device.models import Device
from mobile_framework.version.models import Version, AppVersion
from mobile_framework.user.models import User, AppUser, AppUserProgression


class AppVersionTestCase(TestCase):

    def _create_app_version(self, version=Version('3.1.1'),
                            status=AppVersion.STATUS_UNKNOWN):
        return AppVersion.objects.create(version=version, status=status)

    def test_create_app_version(self):
        """ Test Creating a new AppVersion. """
        version = Version('3.1.1')
        status = AppVersion.STATUS_PUBLISHED
        app_version = self._create_app_version(version, status)
        self.assertEqual(int(app_version.version), int(version))
        self.assertEqual(app_version.__str__(), str(version))
        self.assertEqual(app_version.status, status)

    def test_update_app_version(self):
        """ Test Updating an existing AppVersion. """
        version = Version('3.1.1')
        version2 = Version('1.1.1')
        status = AppVersion.STATUS_DEVELOPMENT
        app_version = self._create_app_version(version)
        app_version.version = version2
        app_version.status = status
        app_version.save()
        app_version2 = AppVersion.objects.get(pk=app_version.pk)
        self.assertEqual(int(app_version2.version), int(version2))
        self.assertEqual(app_version2.__str__(), str(version2))
        self.assertEqual(app_version2.status, status)

    def test_delete_app_version(self):
        """ Test Deleting an existing AppVersion. """
        app_version = self._create_app_version()
        app_version_pk = app_version.pk
        app_version.delete()
        try:
            AppVersion.objects.get(pk=app_version_pk)
        except AppVersion.DoesNotExist:
            pass
        else:
            self.fail('AppVersion should not exist.')

    def test_get_app_version(self):
        """ Test Getting an existing AppVersion. """
        app_version = self._create_app_version()
        try:
            app_version2 = AppVersion.objects.get(pk=app_version.pk)
        except AppVersion.DoesNotExist:
            self.fail('AppVersion should exist.')
        self.assertEqual(app_version.pk, app_version2.pk)
        self.assertEqual(int(app_version.version), int(app_version2.version))


class DeviceTestCase(TestCase):

    def _create_device(self, 
        uuid=StringUUID('{667f98d2-0cb5-4923-b9f7-4e0f121733fb}'), device='iphone5,4',
        os='darwin', os_version='1.1.1', screen='100x100', alias='Whalias'):

        version = Version('1.1.1')
        app_version = AppVersion.objects.create(version=version)
        return Device.objects.create(
            uuid=uuid, device=device, os=os, alias=alias, os_version=os_version, 
            screen=screen, app_version=app_version)

    def test_create_device(self):
        """ Test Creating a new Device. """
        uuid = StringUUID('{667f98d2-0cb5-4923-b9f7-4e0f121733fb}')
        name = 'iphone5,4'
        os = 'darwin'
        os_version = '1.1.1'
        screen = '100x100'
        alias = 'Whalias'
        device = self._create_device(uuid, name, os, os_version, screen, alias)
        self.assertEqual(device.uuid, uuid)
        self.assertEqual(device.device, name)
        self.assertEqual(device.os, os)
        self.assertEqual(device.os_version, os_version)
        self.assertEqual(device.screen, screen)
        self.assertEqual(device.alias, alias)

    def test_update_device(self):
        """ Test Updating an existing Device. """
        name = 'android'
        os = 'ios'
        os_version = '1.2.4'
        screen = '300x300'
        alias = 'alias'
        device = self._create_device()
        device.device = name
        device.os = os
        device.os_version = os_version
        device.screen = screen
        device.alias = alias
        device.save()
        device2 = Device.objects.get(pk=device.pk)
        self.assertEqual(device2.device, name)
        self.assertEqual(device2.os, os)
        self.assertEqual(device2.os_version, os_version)
        self.assertEqual(device2.screen, screen)
        self.assertEqual(device2.alias, alias)

    def test_delete_device(self):
        """ Test Deleting am existing Device. """
        device = self._create_device()
        device_pk = device.pk
        device.delete()
        try:
            Device.objects.get(pk=device_pk)
        except Device.DoesNotExist:
            pass
        else:
            self.fail('Device should not exist.')

    def test_get_device(self):
        """ Test Getting an existing Device. """
        device = self._create_device()
        try:
            device2 = Device.objects.get(pk=device.pk)
        except Device.DoesNotExist:
            self.fail('Device should exist.')
        self.assertEqual(device.pk, device2.pk)


class UserTestCase(TestCase):

    def _create_user(self, username='test', password='test'):
        return User.objects.create_user(username=username, password=password)

    def test_create_user(self):
        """ Test Creating a new User. """
        username = 'test'
        password = 'test'
        user = self._create_user(username, password)
        self.assertEqual(user.username, username)
        self.assertEqual(user.__str__(), username)

    def test_update_user(self):
        """ Test Updating an existing User. """
        name = 'Long Name'
        short_name = 'Short'
        user = self._create_user()
        user.name = name
        user.short_name = short_name
        user.save()
        user2 = User.objects.get(pk=user.pk)
        self.assertEqual(user2.name, name)
        self.assertEqual(user2.short_name, short_name)

    def test_delete_user(self):
        """ Test Deleting an existing User. """
        user = self._create_user()
        user_pk = user.pk
        user.delete()
        try:
            User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            pass
        else:
            self.fail('User should not exist.')

    def test_get_user(self):
        """ Test Geting an existing User. """
        user = self._create_user()
        try:
            user2 = User.objects.get(pk=user.pk)
        except User.DoesNotExist:
            self.fail('User should exist.')
        self.assertEqual(user.pk, user2.pk)
        self.assertEqual(user.username, user2.username)

    def test_get_short_name_username(self):
        """ Test using the username as the short_name. """
        username = 'test'
        user = self._create_user(username=username)
        self.assertEqual(user.__str__(), username)

    def test_get_short_name_name(self):
        """ Test using the name as the short_name. """
        name = 'Long Name'
        user = self._create_user()
        user.name = name
        user.save()
        self.assertEqual(user.__str__(), name)

    def test_get_short_name_short_name(self):
        """ Test using the short name as the short_name. """
        short_name = 'Name'
        user = self._create_user()
        user.short_name = short_name
        user.save()
        self.assertEqual(user.__str__(), short_name)


class AppUserTestCase(TestCase):

    def _create_app_user(self):
        app_version = AppVersion.objects.create(version=Version('1.1.1'))
        device = Device.objects.create(
            uuid='5965e50f-6adf-46ab-a885-57b22df567f5', app_version=app_version,
            os='Darwin', device='iPhone5,4', os_version='1.1.1',
            screen='100x100')
        user = User.objects.create_user(username='test', password='test')
        return AppUser.objects.create(user=user, device=device)

    def test_create_app_user(self):
        """ Test Creating a new AppUser. """
        self._create_app_user()

    def test_delete_app_user(self):
        """ Test Deleting an existing AppUser. """
        app_user = self._create_app_user()
        app_user_pk = app_user.pk
        app_user.delete()
        try:
            AppUser.objects.get(pk=app_user_pk)
        except AppUser.DoesNotExist:
            pass
        else:
            self.fail('AppUser should not exist.')

    def test_get_appuser(self):
        """ Test Getting an existing AppUser. """
        app_user = self._create_app_user()
        try:
            app_user2 = AppUser.objects.get(pk=app_user.pk)
        except AppUser.DoesNotExist:
            self.fail('AppUser should exist.')
        self.assertEqual(app_user.pk, app_user2.pk)


class AppUserProgressionTestCase(TestCase):

    def _create_progression(self, module='test module', enter=datetime.now(),
                            session='12342455'):
        app_version = AppVersion.objects.create(version=Version('1.1.1'))
        device = Device.objects.create(
            uuid='5965e50f-6adf-46ab-a885-57b22df567f5', app_version=app_version,
            os='Darwin', device='iPhone5,4', os_version='1.1.1', screen='100x100')
        user = User.objects.create_user(username='test', password='test')
        app_user = AppUser.objects.create(user=user, device=device)
        return AppUserProgression.objects.create(
            app_user=app_user, device=device, module_name=module, 
            app_session_id=session, enter_timestamp=enter) 

    def test_create_progression(self):
        """ Test Creating a new AppUserProgression. """
        module = 'test module'
        enter = datetime.now()
        session = 12342455
        progression = self._create_progression(module, enter, session)
        self.assertEqual(progression.module_name, module)
        self.assertEqual(progression.enter_timestamp, enter)
        self.assertEqual(progression.app_session_id, session)

    def test_update_progression(self):
        """ Test Updating an existing AppUserProgression. """
        module = 'test module new'
        session = 1234324253535
        progression = self._create_progression()
        progression.module_name = module
        progression.app_session_id = session
        progression.save()
        progression2 = AppUserProgression.objects.get(pk=progression.pk)
        self.assertEqual(progression2.module_name, module)
        self.assertEqual(progression2.app_session_id, session)

    def test_delete_progression(self):
        """ Test Deleting an existing AppUserProgression. """
        progression = self._create_progression()
        progression_pk = progression.pk
        progression.delete()
        try:
            AppUserProgression.objects.get(pk=progression_pk)
        except AppUserProgression.DoesNotExist:
            pass
        else:
            self.fail('AppUserProgression should not exist.')

    def test_get_progression(self):
        """ Test Getting an existing AppUserProgression. """
        progression = self._create_progression()
        try:
            progression2 = AppUserProgression.objects.get(pk=progression.pk)
        except AppUserProgression.DoesNotExist:
            self.fail('AppUserProgression should exist.')
        self.assertEqual(progression.pk, progression2.pk)