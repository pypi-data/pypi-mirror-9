import json
from datetime import datetime
from django.contrib.sessions.middleware import SessionMiddleware
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from mobile_framework.device.views import CreateDevice, RetrieveUpdateDevice
from mobile_framework.user.models import AppUser
from mobile_framework.user.views import (
    ListCreateUser, RetrieveUpdateUser, AuthenticateUser, CreateUserProgression)


class NeedSessionMixin(object):

    def _add_session_to_request(self, request):
        """Annotate a request object with a session"""
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()


class CreateDeviceTestCase(APITestCase):
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = CreateDevice.as_view()

    def test_create_device(self):
        """ Test Creating a new device. """
        data = {
            'app': {
                'version': '3.1.1',
                'app_store_build': '1234567'
            },
            'device': {
                'uuid': '37f7ebd9-9d08-4c0e-8f3e-51350a24488c',
                'device': 'iPhone5,4',
                'os': 'Darwin',
                'os_version': '1.1.1',
                'screen': '100x100'
            }
        }
        request = self.factory.post('/api/devices/', json.dumps(data),
                                    content_type='application/json')
        response = self.view(request)
        response.render()
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('id' in content)

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
        response.render()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RetrieveUpdateDeviceTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = RetrieveUpdateDevice.as_view()

    def _create_device(self):
        data = {
            'app': {
                'version': '3.1.1',
                'app_store_build': '1234567'
            },
            'device': {
                'uuid': '37f7ebd9-9d08-4c0e-8f3e-51350a24488c',
                'device': 'iPhone5,4',
                'os': 'Darwin',
                'os_version': '1.1.1',
                'screen': '100x100'
            }
        }
        view = CreateDevice.as_view()
        request = self.factory.post('/api/devices/', json.dumps(data),
                                    content_type='application/json')
        response = view(request)
        response.render()
        content = json.loads(response.content)
        return content['uuid']

    def test_retrieve_device(self):
        """ Test Retrieving an existing device. """
        uuid = self._create_device()
        request = self.factory.get('/api/devices/{}'.format(uuid))
        response = self.view(request, uuid=uuid)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertEqual(content['uuid'], uuid)

    def test_retrieve_device_404(self):
        """ Test Retrieving a device that does not exist. """
        uuid = 'c353267d-f12f-4e8c-9e59-68010b35c121'
        request = self.factory.get('/api/devices/{}'.format(uuid))
        request = self.view(request, uuid=uuid)
        self.assertEqual(request.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_device(self):
        """ Test Updating an existing device. """
        uuid = self._create_device()
        data = {
            'app': {
                'version': '7.7.7',
                'app_store_build': 'aaaaaaa'
            },
            'device': {
                'uuid': uuid,
                'device': 'iPhone',
                'os': 'Darwin 2',
                'os_version': '2.2.2',
                'screen': '500x500'
            }
        }
        request = self.factory.put('/api/device/{}'.format(uuid), 
                                   json.dumps(data),
                                   content_type='application/json')
        response = self.view(request, uuid=uuid)
        response.render()
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['build'], data['app']['app_store_build'])
        self.assertEqual(content['device'], data['device']['device'])
        self.assertEqual(content['os'], data['device']['os'])
        self.assertEqual(content['os_version'], data['device']['os_version'])
        self.assertEqual(content['screen'], data['device']['screen'])


class ListCreateUserTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ListCreateUser.as_view()

    def _create_device(self):
        data = {
            'app': {
                'version': '3.1.1',
                'app_store_build': '1234567'
            },
            'device': {
                'uuid': '37f7ebd9-9d08-4c0e-8f3e-51350a24488c',
                'device': 'iPhone5,4',
                'os': 'Darwin',
                'os_version': '1.1.1',
                'screen': '100x100'
            }
        }
        view = CreateDevice.as_view()
        request = self.factory.post('/api/devices/', json.dumps(data),
                                    content_type='application/json')
        response = view(request)
        response.render()
        content = json.loads(response.content)
        return content['uuid']

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
                }
            }
        device_id = self._create_device()
        request = self.factory.post('/api/users/', json.dumps(data),
                                    content_type='application/json')
        request.META['HTTP_X_DEVICE'] = device_id
        response = self.view(request)
        response.render()
        content = json.loads(response.content)
        return response.status_code, content

    def test_create_user(self):
        """ Test Creating a new User. """
        status_code, content = self._create_user()
        self.assertEqual(status_code, status.HTTP_201_CREATED)
        self.assertTrue('id' in content)

    def test_create_user_error(self):
        """ Test Creating a User with invalid data. """
        data = {
            'user': {
                'password': 'test',
                'email': 'test@test.com',
                'name': 'test',
                'short_name': 'test'
            }
        }
        status_code, content = self._create_user(data)
        self.assertEqual(status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_user(self):
        """ Test Listing all the Users. """
        self._create_user()
        request = self.factory.get('/api/users/')
        response = self.view(request)
        response.render()
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(content, list))
        self.assertEqual(len(content), 1)


class RetrieveUpdateUserTestCase(NeedSessionMixin, APITestCase):
    device_id = '37f7ebd9-9d08-4c0e-8f3e-51350a24488c'

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = RetrieveUpdateUser.as_view()

    def _create_device(self):
        data = {
            'app': {
                'version': '3.1.1',
                'app_store_build': '1234567'
            },
            'device': {
                'uuid': self.device_id,
                'device': 'iPhone5,4',
                'os': 'Darwin',
                'os_version': '1.1.1',
                'screen': '100x100'
            }
        }
        view = CreateDevice.as_view()
        request = self.factory.post('/api/devices/', json.dumps(data),
                                    content_type='application/json')
        response = view(request)
        response.render()
        content = json.loads(response.content)
        return content['uuid']

    def _create_user(self):
        data = {
            'user': {
                'username': 'test',
                'password1': 'test',
                'password2': 'test',
                'email': 'test@test.com',
                'name': 'test',
                'short_name': 'test'
            }
        }
        device_id = self._create_device()
        view = ListCreateUser.as_view()
        request = self.factory.post('/api/users/', json.dumps(data),
                                    content_type='application/json')
        request.META['HTTP_X_DEVICE'] = device_id
        response = view(request)
        response.render()
        content = json.loads(response.content)
        return content['id']

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
        response = self.view(request, pk=app_user_pk)
        response.render()
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['id'], app_user_pk)
        self.assertEqual(content['email'], data['user']['email'])
        self.assertEqual(content['name'], data['user']['name'])
        self.assertEqual(content['short_name'], data['user']['short_name'])

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
        request.META['HTTP_X_DEVICE'] = self.device_id
        request.user = app_user.user
        self._add_session_to_request(request)
        response = self.view(request, pk=app_user_pk)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user(self):
        """ Test Getting an existing User. """
        app_user_pk = self._create_user()
        request = self.factory.get('/api/users/{}'.format(app_user_pk))
        response = self.view(request, pk=app_user_pk)
        response.render()
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['id'], app_user_pk)

    def test_get_user_404(self):
        """ Test Getting a User that doesn't exist. """
        app_user_pk = 9999
        request = self.factory.get('/api/users/{}'.format(app_user_pk))
        response = self.view(request, pk=app_user_pk)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AuthenticateUserTestCase(NeedSessionMixin, APITestCase):
    device_id = '332b7783-ad29-48e5-a9bc-d466d40d2022'

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = AuthenticateUser.as_view()
        self._create_user()

    def _create_device(self, device_id='332b7783-ad29-48e5-a9bc-d466d40d2022'):
        data = {
            'app': {
                'version': '3.1.1',
                'app_store_build': '1234567'
            },
            'device': {
                'uuid': device_id,
                'device': 'iPhone5,4',
                'os': 'Darwin',
                'os_version': '1.1.1',
                'screen': '100x100'
            }
        }
        view = CreateDevice.as_view()
        request = self.factory.post('/api/devices/', json.dumps(data),
                                    content_type='application/json')
        response = view(request)
        response.render()
        content = json.loads(response.content)
        return content['uuid']

    def _create_user(self):
        data = {
            'user': {
                'username': 'test',
                'password1': 'test',
                'password2': 'test',
                'email': 'test@test.com',
                'name': 'test',
                'short_name': 'test'
            }
        }
        device_id = self._create_device()
        view = ListCreateUser.as_view()
        request = self.factory.post('/api/users/', json.dumps(data),
                                    content_type='application/json')
        request.META['HTTP_X_DEVICE'] = device_id
        response = view(request)
    
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

        self._add_session_to_request(request)
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


class CreateUserProgressionTestCase(APITestCase):
    device_id = '37f7ebd9-9d08-4c0e-8f3e-51350a24488c'
    now = datetime.now().strftime("%b %d, %Y %H:%M:%S")

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = CreateUserProgression.as_view()

    def _create_device(self):
        data = {
            'app': {
                'version': '3.1.1',
                'app_store_build': '1234567'
            },
            'device': {
                'uuid': self.device_id,
                'device': 'iPhone5,4',
                'os': 'Darwin',
                'os_version': '1.1.1',
                'screen': '100x100'
            }
        }
        view = CreateDevice.as_view()
        request = self.factory.post('/api/devices/', json.dumps(data),
                                    content_type='application/json')
        response = view(request)
        response.render()
        content = json.loads(response.content)
        return content['uuid']

    def _create_user(self):
        data = {
            'user': {
                'username': 'test',
                'password1': 'test',
                'password2': 'test',
                'email': 'test@test.com',
                'name': 'test',
                'short_name': 'test'
            }
        }
        device_id = self._create_device()
        view = ListCreateUser.as_view()
        request = self.factory.post('/api/users/', json.dumps(data),
                                    content_type='application/json')
        request.META['HTTP_X_DEVICE'] = device_id
        response = view(request)
        response.render()
        content = json.loads(response.content)
        return content['id']

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