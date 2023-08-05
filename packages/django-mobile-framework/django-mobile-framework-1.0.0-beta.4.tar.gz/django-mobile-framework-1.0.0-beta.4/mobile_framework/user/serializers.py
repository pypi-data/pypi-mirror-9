from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from uuidfield.fields import StringUUID
from rest_framework import serializers
from rest_framework.compat import OrderedDict
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty
from rest_framework.validators import UniqueValidator
from oauth2_provider.models import get_application_model
from mobile_framework import (
    get_app_user_model, get_app_user_progression_model, get_device_model)
from mobile_framework.core.validators import RelatedObjectFieldUniqueValidator
from mobile_framework.core.serializers import HasCreateRequired
from mobile_framework.device.serializers import DeviceSerializer

User = get_user_model()
Application = get_application_model()
Device = get_device_model()
AppUser = get_app_user_model()
AppUserProgression = get_app_user_progression_model()


class UserSerializer(HasCreateRequired):
    create_required_fields = ('username', 'email', 'password')

    username = serializers.CharField(
        validators=[UniqueValidator(User.objects.all())],
        required=False
    )

    def validate(self, attrs):
        attrs['password'] = None
        password1 = self.initial_data.get('password1', None)
        password2 = self.initial_data.get('password2', None)
        if password1 and password2:
            if password1 == password2:
                attrs['password'] = password2
            else:
                raise ValidationError(_(u'Passwords did not match.'))
        return super(UserSerializer, self).validate(attrs)

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data.get('password'))
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for key in validated_data.keys():
            setattr(instance, key, validated_data.get(key, getattr(instance, key, None)))
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('pk', 'username', 'email', 'name', 'short_name')


class AppUserSerializer(HasCreateRequired):
    create_required_fields = ('user.username', 'user.email', 'password')

    device = serializers.CharField(required=False)
    pk = serializers.IntegerField(source='user.pk', read_only=True)
    username = serializers.CharField(
        source='user.username',
        required=False,
        validators=[
            RelatedObjectFieldUniqueValidator(User.objects.all()),
        ]
    )
    email = serializers.EmailField(source='user.email', required=False)
    name = serializers.CharField(source='user.name', required=False)
    short_name = serializers.CharField(source='user.short_name', required=False)

    def validate_device(self, value):
        try:
            uuid = str(StringUUID(value))
            device = Device.objects.get(uuid=uuid)
        except Device.DoesNotExist:
            raise ValidationError(_(u'Invalid Device UUID.'))
        return device

    def validate(self, attrs):
        attrs['password'] = None
        password1 = self.initial_data.get('password1', None)
        password2 = self.initial_data.get('password2', None)
        if password1 and password2:
            if password1 == password2:
                attrs['password'] = password2
            else:
                raise ValidationError(_(u'Passwords did not match.'))
        return super(AppUserSerializer, self).validate(attrs)

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = validated_data.pop('password')

        # Create a new User and use it when creating an AppUser
        user = User(**user_data)
        user.set_password(password)
        user.save()
        app_user = AppUser(user=user, **validated_data)
        app_user.save()
        return app_user

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        password = validated_data.pop('password', None)
        user = instance.user
        for key in user_data.keys():
            setattr(user, key, user_data.get(key, getattr(user, key, None)))
        if password:
            user.set_password(password)
        user.save()
        instance.save()
        return instance

    class Meta:
        model = AppUser
        fields = ('pk', 'username', 'email', 'name', 'short_name', 'device')


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
        fields = ('device', 'app_user', 'module_name', 'enter_timestamp', 
                  'app_session_id')
        write_only_fields = fields


class AppUserProgressionListSerializer(serializers.ListSerializer):
    child = AppUserProgressionSerializer()
