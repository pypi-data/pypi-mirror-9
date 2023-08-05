from django.db import models
from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.compat import OrderedDict
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty, SkipField

from oauth2_provider.models import get_application_model

from mobile_framework import (get_app_user_model, get_app_user_progression_model, 
                              get_device_model)

User = get_user_model()
Application = get_application_model()
Device = get_device_model()
AppUser = get_app_user_model()
AppUserProgression = get_app_user_progression_model()


class CreateUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    short_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ('username', 'name', 'short_name', 'email')

    def validate(self, attrs):
        password1 = self.initial_data.get('password1', None)
        password2 = self.initial_data.get('password2', None)

        if password1 and password2:
            if password1 == password2:
                attrs['password'] = password2
            else:
                raise ValidationError('Passwords did not match.')
        else:
            raise ValidationError('Password is required.')
        return attrs

    def create(self, validated_data):
        ModelClass = self.Meta.model
        password = validated_data.pop('password', None)
        obj = ModelClass(username=validated_data['username'])
        obj.name = validated_data.get('name', None)
        obj.short_name = validated_data.get('name', None)
        obj.email = validated_data.get('email', None)
        obj.set_password(password)
        obj.save()

        # Create new application
        data = {
            'name': '%s App' % obj.username,
            'user': obj,
            'client_type': 'confidential',
            'authorization_grant_type': 'client-credentials'
        }
        Application.objects.get_or_create(**data)

        return obj

    def update(self, instance, validated_data):
        raise Exception('Cannot update user in the CreateUserSerializer. Use UserSerializer.')


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)
    name = serializers.CharField(required=False)
    short_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'name', 'short_name', 'email', 'password')

    def validate(self, attrs):
        password1 = self.initial_data.get('password1', None)
        password2 = self.initial_data.get('password2', None)

        if password1 and password2:
            if password1 == password2:
                attrs['password'] = password2
            else:
                raise ValidationError('Passwords did not match.')
        return attrs

    def create(self, validated_data):
        raise Exception('Cannot create user in the UserSerializer. Use CreateUserSerializer.')

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance.name = validated_data.get('name', instance.name)
        instance.short_name = validated_data.get('name', instance.short_name)
        instance.email = validated_data.get('email', instance.email)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class CreateAppUserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    name = serializers.CharField(source='user.name', read_only=True)
    short_name = serializers.CharField(source='user.short_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    device = serializers.CharField(required=False, write_only=True)
    user = UserSerializer(required=False, write_only=True)

    def __init__(self, instance=None, data=None, user_data=None, **kwargs):
        self.user_serializer = CreateUserSerializer(data=user_data)
        super(CreateAppUserSerializer, self).__init__(instance, data, **kwargs) 

    class Meta:
        model = AppUser
        fields = ('id', 'username', 'name', 'short_name', 'email', 
                  'user', 'device')

    def validate(self, attrs):
        try:
            device = Device.objects.get(uuid=attrs['device'])
            attrs['device'] = device
        except Device.DoesNotExist:
            raise ValidationError('Invalid Device.')
        if self.user_serializer.is_valid():
            user = self.user_serializer.save()
            attrs['user'] = user
        else:
            raise ValidationError(self.user_serializer.errors)
        return attrs

    def update(self, instance, validated_data):
        raise Exception('Cannot update user in the CreateAppUserSerializer. Use AppUserSerializer.')


class AppUserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    name = serializers.CharField(source='user.name', read_only=True)
    short_name = serializers.CharField(source='user.short_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    def __init__(self, instance=None, data=None, user_data=None, *args, 
                 **kwargs):
        if isinstance(instance, AppUser):
            extra = {}
            if user_data is not None:
                extra['data'] = user_data
            self.user_serializer = UserSerializer(instance.user, **extra)
        if data is not None:
            kwargs['data'] = data    
        super(AppUserSerializer, self).__init__(instance, *args, **kwargs) 

    class Meta:
        model = AppUser
        fields = ('id', 'username', 'name', 'short_name', 'email')

    def validate(self, attrs):
        if self.user_serializer.is_valid():
            user = self.user_serializer.save()
        else:
            raise ValidationError(self.user_serializer.errors)
        return attrs

    def create(self, validated_data):
        raise Exception('Cannot create user in the AppUserSerializer. Use CreateAppUserSerializer.')


class AppUserProgressionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUserProgression
        fields = ('device', 'app_user', 'module_name', 'enter_timestamp', 'app_session_id')
        write_only_fields = fields
