import datetime
import uuid

from django.contrib.auth import get_user_model, authenticate, login, logout
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from oauth2_provider.models import AccessToken, get_application_model

from mobile_framework import get_app_user_model, get_app_user_progression_model, get_device_model
from mobile_framework.core.permissions import IsSameDeviceOrReadOnly, IsSameUserOrReadOnly
from mobile_framework.core.utils import Bool
from mobile_framework.user.serializers import (
    CreateAppUserSerializer, AppUserSerializer, AppUserProgressionSerializer
)

User = get_user_model()
Application = get_application_model()
AppUser = get_app_user_model()
AppUserProgression =  get_app_user_progression_model()
Device = get_device_model()


class ListCreateUser(generics.ListCreateAPIView):
    queryset = AppUser.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateAppUserSerializer
        return AppUserSerializer

    def post(self, request, *args, **kwargs):
        """
        Creates the User.

        Accepts:
            - json
            - formdata
            - multipart
        Request Structure:
        ```
        {
            'user': {
                'username': <the user's username>, # Required
                'password': <the user's password>, # Required
                'name': <the user's name>,
                'short_name': <the user's short name>,
                'email': <the user's email>
            },
            'app_user': {
                ...fields for the App User
            }
        }
        ```

        Return:
            - 400 : Invalid Request
            - 201 : Create successful
        Response Structure:
        ```
        {
            'id': <the new app user's UUID> 
        }
        ```
        """
        serializer = self.get_serializer_class()
        data = request.DATA
        try:

            app_user_data = data.get('app_user', {})
            app_user_data['device'] = request.META['HTTP_X_DEVICE']
            app_user_serializer = serializer(data=app_user_data, user_data=data['user'])

            if app_user_serializer.is_valid():
                app_user_serializer.save()
                return Response(app_user_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(app_user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return Response({'detail': 'KeyError: {}'.format(e)})
        except Exception as e:
            print(e)
            return Response({'detail': e}, status=status.HTTP_400_BAD_REQUEST)


class RetrieveUpdateUser(generics.RetrieveUpdateAPIView):
    permission_classes = (IsSameUserOrReadOnly, IsSameDeviceOrReadOnly)
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializer

    def put(self, request, *args, **kwargs):
        """
        Updates the User data. The user to be updated must be a valid Mobile App User.

        Accepts:
            - json
            - formdata
            - multipart
        Request Structure:
        ```
        {
            'user': {
                'password': <the user's password>,
                'name': <the user's name>,
                'short_name': <the user's short name>,
                'email': <the user's email>
            },
            'app_user': {
                ...fields for the App User
            }
        }
        ```

        Return:
            - 400 : Invalid Request
            - 200 : Update successful
        Response Structure:
        ```
        {
            'uuid': <the app user's UUID>,
            'name': <the user's name>,
            'short_name': <the user's short name>,
            'email': <the user's email>,
            ... other fields
        }
        ```
        """
        app_user = self.get_object()
        data = request.DATA
        try:
            app_user_data = data.get('app_user', {})
            app_user_serializer = self.serializer_class(app_user, data=app_user_data, user_data=data['user'])

            if app_user_serializer.is_valid():
                app_user_serializer.save()
                return Response(app_user_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(app_user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return Response({'detail': 'KeyError: {}'.format(e)})
        except Exception as e:
            print(e)


class AuthenticateUser(APIView):

    def post(self, request, *args, **kwargs):
        """
        Logs in the User. Creates a new token for the User if the access token is expired.

        Querystring:
        force=<number> - Ignore the current device check (0=false, 1=true)

        Accepts:
            - json
            - formdata
            - multipart
        Request Structure:
        ```
        {
            'username': <the user's username>,
            'password': <the user's password>
        }
        ```

        Return:
            - 400 : Invalid Request
            - 200 : Login successful
            - 202 : Accepted (Credentials were correct, but was currently logged in another device)
        Response Structure:
        ```
        {
            'uuid': <the app user's UUID>,
            'name': <the user's name>,
            'short_name': <the user's short name>,
            'email': <the user's email>,
            ... other fields
        }
        ```
        """
        data = request.DATA
        force = request.GET.get('force', 0)
        try:
            device_uuid = request.META.get('HTTP_X_DEVICE', None)
            user = authenticate(**data)
            if user:
                login(request, user)
                now = timezone.now()
                try:
                    device = Device.objects.get(uuid=device_uuid)
                except Device.DoesNotExist:
                    return Response({'detail': 'Login Failed.'}, status=status.HTTP_401_UNAUTHORIZED)
                try:
                    app = Application.objects.get(user=user)
                except Application.DoesNotExist:
                    return Response({'detail': 'Login Failed.'}, status=status.HTTP_401_UNAUTHORIZED)

                tokens = AccessToken.objects.filter(user=user, application=app)
                token = None

                if device != user.app_user.device and not Bool(force):
                    e = 'Currently logged in another device. Woud you like to continue?'
                    return Response({'detail': e}, status=status.HTTP_202_ACCEPTED)
                if tokens.exists():
                    token = tokens.latest('expires')
                if not token or token.is_expired():
                    token = AccessToken.objects.create(
                        user=user,
                        application=app,
                        expires=now + datetime.timedelta(days=365),
                        token=uuid.uuid1().hex
                    )

                user.app_user.device = device
                user.app_user.save()
                serializer = AppUserSerializer(user.app_user)
                retval = {
                    'token': token.token,
                    'expires_in': token.expires,
                    'user': serializer.data,
                    'notes': None
                }
                return Response(retval)
            else:
                return Response({'detail': 'Login Failed. Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)   
        except Exception as e:
            print(e)

    def delete(self, request, *args, **kwargs):
        """ Logs out the user. """
        logout(request)
        return Response(status=status.HTTP_200_OK)


class CreateUserProgression(APIView):

    def post(self, request, *args, **kwargs):
        """
        Creates the User Progression while using the App.

        Accepts:
            - json
            - formdata
            - multipart
        Request Structure:
        ```
        [
            {
                'device': <the device's UUID>,
                'app_user': <the user's UUID>,
                'module_name': <the class of the module>,
                'enter_timestamp': <the timestamp when the User entered the module>,
                'app_session_id': <the session id for User (created by the device)>
            }
        ]
        ```

        Return:
            - 400 : Invalid Request
            - 204 : Created the progressions successfully
        Response Structure:
        ```
        No Content
        ```
        """
        data = request.DATA
        serializer = AppUserProgressionSerializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)