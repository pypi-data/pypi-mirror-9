from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from uuidfield.fields import StringUUID

from rest_framework import serializers
from rest_framework.compat import OrderedDict
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty, SkipField

from oauth2_provider.models import get_application_model

from mobile_framework import (get_app_user_model, get_app_user_progression_model, 
                              get_device_model)
from mobile_framework.device.serializers import DeviceSerializer

User = get_user_model()
Application = get_application_model()
Device = get_device_model()
AppUser = get_app_user_model()
AppUserProgression = get_app_user_progression_model()


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, required=False)
    password1 = serializers.CharField(write_only=True, required=False)
    password2 = serializers.CharField(write_only=True, required=False)

    def validate(self, attrs):
        password1 = attrs.pop('password1', None)
        password2 = attrs.pop('password2', None)
        if password1 and password2:
            if password1 == password2:
                attrs['password'] = password2
            else:
                raise ValidationError(_(u'Passwords did not match.'))
        return attrs

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data.get('password'))
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.name = validated_data.get('name', instance.name)
        instance.short_name = validated_data.get('short_name', instance.short_name)
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('pk', 'username', 'password', 'password1', 'password2', 'email', 'name', 'short_name')


class AppUserSerializer(serializers.ModelSerializer):
    device = serializers.CharField(write_only=True, required=False)
    user = UserSerializer(write_only=True)
    pk = serializers.IntegerField(source='user.pk', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    name = serializers.CharField(source='user.name', read_only=True)
    short_name = serializers.CharField(source='user.short_name', read_only=True)

    def validate_device(self, value):
        try:
            uuid = str(StringUUID(value))
            device = Device.objects.get(uuid=uuid)
        except Device.DoesNotExist:
            raise ValidationError(_(u'Invalid Device UUID.'))
        return device

    def validate(self, attrs):
        user_data = attrs.get('user', None)
        # Username is required in Create
        if not self.instance:
            if not attrs.get('device', None):
                raise ValidationError(_(u'Device is required.'))
            if user_data and not user_data.get('username', None):
                raise ValidationError(_(u'Username is required.'))
        return attrs

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = user_data.pop('password')
        # Create a new User and use it when creating an AppUser
        user = User(**user_data)
        user.set_password(password)
        user.save()
        app_user = AppUser(user=user, **validated_data)
        app_user.save()
        return app_user

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        instance.user.email = user_data.get('email', instance.user.email)
        instance.user.name = user_data.get('name', instance.user.name)
        instance.user.short_name = user_data.get('short_name', instance.user.short_name)
        password = user_data.get('password', None)
        if password:
            instance.user.set_password(password)
        instance.user.save()
        instance.save()
        return instance

    class Meta:
        model = AppUser
        fields = ('pk', 'user', 'username', 'email', 'name', 'short_name', 'device')


class AppUserProgressionSerializer(serializers.ModelSerializer):
    device = serializers.CharField(write_only=True)

    def validate_device(self, value):
        try:
            uuid = str(StringUUID(value))
            device = Device.objects.get(uuid=uuid)
        except Device.DoesNotExist:
            raise ValidationError(_(u'Invalid Device UUID.'))
        return device

    class Meta:
        model = AppUserProgression
        fields = ('device', 'app_user', 'module_name', 'enter_timestamp', 'app_session_id')
        write_only_fields = fields


class AppUserProgressionListSerializer(serializers.ListSerializer):
    child = AppUserProgressionSerializer()
