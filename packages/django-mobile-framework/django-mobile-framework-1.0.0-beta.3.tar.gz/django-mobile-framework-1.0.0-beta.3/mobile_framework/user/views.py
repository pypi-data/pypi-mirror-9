import datetime
import uuid

from django.contrib.auth import get_user_model, authenticate, login, logout
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from oauth2_provider.models import AccessToken, get_application_model

from mobile_framework import (
    get_app_user_model, get_app_user_progression_model, get_device_model)
from mobile_framework.core.permissions import (
    IsSameDeviceOrReadOnly, IsSameUserOrReadOnly)
from mobile_framework.core.utils import Bool
from mobile_framework.user.serializers import (
    UserSerializer, AppUserSerializer, AppUserProgressionListSerializer)

User = get_user_model()
Application = get_application_model()
AppUser = get_app_user_model()
AppUserProgression =  get_app_user_progression_model()
Device = get_device_model()


class ListCreateUser(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RetrieveUpdateUser(generics.RetrieveUpdateAPIView):
    permission_classes = (IsSameUserOrReadOnly,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ListCreateAppUser(generics.ListCreateAPIView):
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializer


class RetrieveUpdateAppUser(generics.RetrieveUpdateAPIView):
    permission_classes = (IsSameUserOrReadOnly, IsSameDeviceOrReadOnly)
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializer


class LoginUser(APIView):

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
        ```
        {
            'pk': <the user's PK>,
            'name': <the user's name>,
            'short_name': <the user's short name>,
            'email': <the user's email>,
            ... other fields
        }
        ```
        """
        data = request.DATA
        try:
            user = authenticate(**data)
            if user:
                login(request, user)
                serializer = UserSerializer(user)
                return Response(serializer.data)
            else:
                return Response({'detail': 'Invalid Username or Password.'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'defailt': 'Uknown Exception.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            print(e)


class LoginMobileUser(APIView):

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
            device_uuid = request.META['HTTP_X_DEVICE']
            user = authenticate(**data)
            if user:
                login(request, user)
                now = timezone.now()
                try:
                    device = Device.objects.get(uuid=device_uuid)
                except Device.DoesNotExist:
                    return Response({'detail': 'Invalid Device.'}, status=status.HTTP_401_UNAUTHORIZED)
                try:
                    app = Application.objects.get(user=user)
                except Application.DoesNotExist:
                    return Response({'detail': 'Application Does not Exist.'}, status=status.HTTP_401_UNAUTHORIZED)

                tokens = AccessToken.objects.filter(user=user, application=app)
                token = None

                if device.uuid != user.app_user.device.uuid and not Bool(force):
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
        except KeyError as e:
            return Response({'detail': 'Missing Required Key: {}'.format(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'defailt': 'Uknown Exception.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            print(e)


class LogoutUser(APIView):

    def delete(self, request, *args, **kwargs):
        """ Logs out the user. """
        logout(request)
        return Response(status=status.HTTP_200_OK)


class CreateUserProgression(generics.CreateAPIView):
    queryset = AppUserProgression.objects.all()
    serializer_class = AppUserProgressionListSerializer
