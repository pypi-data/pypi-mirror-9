import json
from datetime import datetime
from django.contrib.sessions.middleware import SessionMiddleware
from uuidfield.fields import StringUUID
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from mobile_framework.device.views import CreateDevice, RetrieveUpdateDevice
from mobile_framework.user.models import AppUser
from mobile_framework.version.models import Version
from mobile_framework.user.views import (
    ListCreateUser, RetrieveUpdateUser, LoginUser, LoginMobileUser,
    LogoutUser, CreateUserProgression)


class NeedSessionMixin(object):

    def _add_session_to_request(self, request):
        """Annotate a request object with a session"""
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()


class NeedDeviceMixin(object):
    device_id = '37f7ebd9-9d08-4c0e-8f3e-51350a24488c'

    def _create_device(self, device=None):
        self.device_id = self.device_id if not device else device
        data = {
            'app_version': {
                'version': '3.1.1',
                'app_store_build': '1234567'
            },
            'uuid': self.device_id,
            'device': 'iPhone5,4',
            'os': 'Darwin',
            'os_version': '1.1.1',
            'screen': '100x100'
        }
        view = CreateDevice.as_view()
        request = self.factory.post('/api/devices/', json.dumps(data),
                                    content_type='application/json')
        response = view(request)


class NeedUserMixin(NeedDeviceMixin):

    def _create_user(self):
        data = {
            'user': {
                'username': 'test',
                'password1': 'test',
                'password2': 'test',
                'email': 'test@test.com',
                'name': 'test',
                'short_name': 'test'
            },
            'device': self.device_id
        }
        self._create_device()
        view = ListCreateUser.as_view()
        request = self.factory.post('/api/users/', json.dumps(data),
                                    content_type='application/json')
        response = view(request)
        return response.data['pk']


class CreateDeviceTestCase(APITestCase):
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = CreateDevice.as_view()

    def test_create_device(self):
        """ Test Creating a new device. """
        data = {
            'app_version': {
                'version': '3.1.1',
                'app_store_build': '1234567'
            },
            'uuid': '37f7ebd9-9d08-4c0e-8f3e-51350a24488c',
            'device': 'iPhone5,4',
            'os': 'Darwin',
            'os_version': '1.1.1',
            'screen': '100x100'
        }
        request = self.factory.post('/api/devices/', json.dumps(data),
                                    content_type='application/json')
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('uuid' in response.data.keys())

    def test_create_device_error(self):
        """ Test Creating a new device with invalid data. """
        data = {
            'app': {
                'version': '3.1.1',
                'app_store_build': '1234567'
            },
            'device': {
                'device': 'iPhone5,4',
                'os': 'Darwin',
                'os_version': '1.1.1',
                'screen': '100x100'
            }
        }
        request = self.factory.post('/api/devices/', json.dumps(data),
                                    content_type='application/json')
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RetrieveUpdateDeviceTestCase(NeedDeviceMixin, APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = RetrieveUpdateDevice.as_view()

    def test_retrieve_device(self):
        """ Test Retrieving an existing device. """
        self._create_device()
        request = self.factory.get('/api/devices/{}'.format(self.device_id))
        response = self.view(request, uuid=self.device_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['uuid'], str(StringUUID(self.device_id)))

    def test_retrieve_device_404(self):
        """ Test Retrieving a device that does not exist. """
        uuid = 'c353267d-f12f-4e8c-9e59-68010b35c121'
        request = self.factory.get('/api/devices/{}'.format(uuid))
        request = self.view(request, uuid=uuid)
        self.assertEqual(request.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_device(self):
        """ Test Updating an existing device. """
        self._create_device()
        data = {
            'app_version': {
                'version': '7.7.7',
                'app_store_build': 'aaaaaaa'
            },
            'uuid': self.device_id,
            'device': 'iPhone',
            'os': 'Darwin 2',
            'os_version': '2.2.2',
            'screen': '500x500'
        }
        request = self.factory.put('/api/device/{}'.format(self.device_id), 
                                   json.dumps(data),
                                   content_type='application/json')
        response = self.view(request, uuid=self.device_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['device'], data['device'])
        self.assertEqual(response.data['os'], data['os'])
        self.assertEqual(response.data['os_version'], data['os_version'])
        self.assertEqual(response.data['screen'], data['screen'])
        self.assertEqual(int(response.data['app_version']['version']), int(Version(data['app_version']['version'])))
        self.assertEqual(response.data['app_version']['app_store_build'], data['app_version']['app_store_build'])


class ListCreateUserTestCase(NeedDeviceMixin, APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ListCreateUser.as_view()

    def _create_user(self, data=None):
        if data is None:
            data = {
                'user': {
                    'username': 'test',
                    'password1': 'test',
                    'password2': 'test',
                    'email': 'test@test.com',
                    'name': 'test',
                    'short_name': 'test'
                },
                'device': self.device_id
            }
        self._create_device()
        request = self.factory.post('/api/users/', json.dumps(data),
                                    content_type='application/json')
        request.META['HTTP_X_DEVICE'] = self.device_id
        response = self.view(request)
        return response.status_code, response.data

    def test_create_user(self):
        """ Test Creating a new User. """
        status_code, data = self._create_user()
        self.assertEqual(status_code, status.HTTP_201_CREATED)
        self.assertTrue('pk' in data.keys())

    def test_create_user_error(self):
        """ Test Creating a User with invalid data. """
        data = {
            'user': {
                'password': 'test',
                'email': 'test@test.com',
                'name': 'test',
                'short_name': 'test'
            },
            'device': self.device_id,
        }
        status_code, data = self._create_user(data)
        self.assertEqual(status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_user(self):
        """ Test Listing all the Users. """
        self._create_user()
        request = self.factory.get('/api/users/')
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        self.assertEqual(len(response.data), 1)


class RetrieveUpdateUserTestCase(NeedUserMixin, NeedSessionMixin, APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = RetrieveUpdateUser.as_view()

    def test_update_user(self):
        """ Test Updating an existing User. """
        app_user_pk = self._create_user()
        app_user = AppUser.objects.get(pk=app_user_pk)
        data = {
            'user': {
                'email': 'test2@test.com',
                'name': 'test2',
                'short_name': 'test2'
            }
        }
        request = self.factory.put(
            '/api/users/{}'.format(app_user_pk), json.dumps(data),
            content_type='application/json')
        force_authenticate(request, user=app_user.user)
        request.META['HTTP_X_DEVICE'] = self.device_id
        #request.user = app_user.user
        #self._add_session_to_request(request)
        response = self.view(request, pk=app_user_pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pk'], app_user_pk)
        self.assertEqual(response.data['email'], data['user']['email'])
        self.assertEqual(response.data['name'], data['user']['name'])
        self.assertEqual(response.data['short_name'], data['user']['short_name'])

    def test_update_user_error(self):
        """ Test Updating an existing User with invalid data. """
        app_user_pk = self._create_user()
        app_user = AppUser.objects.get(pk=app_user_pk)
        data = {
            'user': {
                'email': 'test2',
            }
        }
        request = self.factory.put(
            '/api/users/{}'.format(app_user_pk), json.dumps(data),
            content_type='application/json')
        force_authenticate(request, user=app_user.user)
        request.META['HTTP_X_DEVICE'] = self.device_id
        #request.user = app_user.user
        #self._add_session_to_request(request)
        response = self.view(request, pk=app_user_pk)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user(self):
        """ Test Getting an existing User. """
        app_user_pk = self._create_user()
        request = self.factory.get('/api/users/{}'.format(app_user_pk))
        response = self.view(request, pk=app_user_pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pk'], app_user_pk)

    def test_get_user_404(self):
        """ Test Getting a User that doesn't exist. """
        app_user_pk = 9999
        request = self.factory.get('/api/users/{}'.format(app_user_pk))
        response = self.view(request, pk=app_user_pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LoginUserTestCase(NeedSessionMixin, NeedUserMixin, APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = LoginUser.as_view()
        self._create_user()

    def test_login(self):
        """ Test Logging in an existing User. """
        data = {
            'username': 'test',
            'password': 'test'
        }
        request = self.factory.post('/api/authenticate/', json.dumps(data),
                                    content_type='application/json')
        self._add_session_to_request(request)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_invalid(self):
        """ Test Logging in using invalid credentials. """
        data = {
            'username': 'test1',
            'password': 'test1'
        }
        request = self.factory.post('/api/authenticate/', json.dumps(data),
                                    content_type='application/json')
        self._add_session_to_request(request)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LoginMobileUserTestCase(NeedUserMixin, NeedSessionMixin, APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = LoginMobileUser.as_view()
        self._create_user()

    def test_login(self):
        """ Test Logging in an existing User. """
        data = {
            'username': 'test',
            'password': 'test'
        }
        request = self.factory.post('/api/authenticate/', json.dumps(data),
                                    content_type='application/json')
        request.META['HTTP_X_DEVICE'] = self.device_id
        self._add_session_to_request(request)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_invalid(self):
        """ Test Logging in using invalid credentials. """
        data = {
            'username': 'test1',
            'password': 'test1'
        }
        request = self.factory.post('/api/authenticate/', json.dumps(data),
                                    content_type='application/json')
        request.META['HTTP_X_DEVICE'] = self.device_id
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_login_without_device(self):
        """ Test Logging in without specifying a device. """
        data = {
            'username': 'test',
            'password': 'test'
        }
        request = self.factory.post('/api/authenticate/', json.dumps(data),
                                    content_type='application/json')
        self._add_session_to_request(request)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_different_device(self):
        """ Test Logging in from a different device. """
        device_id = 'ccd72550-ffbb-4dd5-82e1-37f1742ea5d5'
        self._create_device(device_id)
        data = {
            'username': 'test',
            'password': 'test'
        }
        request = self.factory.post('/api/authenticate/', json.dumps(data),
                                    content_type='application/json')
        request.META['HTTP_X_DEVICE'] = device_id
        self._add_session_to_request(request)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_login_different_device_force(self):
        """ Test Logging in from a different device but force the login. """
        device_id = 'ccd72550-ffbb-4dd5-82e1-37f1742ea5d5'
        self._create_device(device_id)
        data = {
            'username': 'test',
            'password': 'test'
        }
        request = self.factory.post('/api/authenticate/?force=1', 
                                    json.dumps(data), 
                                    content_type='application/json')
        request.META['HTTP_X_DEVICE'] = device_id
        self._add_session_to_request(request)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CreateUserProgressionTestCase(NeedUserMixin, APITestCase):
    now = datetime.now().strftime("%b %d, %Y %H:%M:%S")

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = CreateUserProgression.as_view()

    def test_create_progression(self):
        """ Test Creating a new User Progression. """
        app_user_pk = self._create_user()
        data = {
            'device': self.device_id,
            'app_user': app_user_pk,
            'module_name': 'Test Module',
            'enter_timestamp': self.now,
            'app_session_id': 1234234234
        }
        request = self.factory.post('/api/progressions/', json.dumps(data),
                                    content_type='application/json')
        response = self.view(request)
        self.assertTrue(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_progression_error(self):
        """ Test Creating a new User Progression with invalid data. """
        app_user_pk = self._create_user()
        data = {
            'app_user': app_user_pk,
            'module_name': 'Test Module',
            'enter_timestamp': self.now,
            'app_session_id': 1234234234
        }
        request = self.factory.post('/api/progressions/', json.dumps(data),
                                    content_type='application/json')
        response = self.view(request)
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)