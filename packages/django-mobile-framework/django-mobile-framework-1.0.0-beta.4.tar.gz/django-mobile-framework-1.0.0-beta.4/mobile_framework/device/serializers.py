from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from mobile_framework import get_device_model, get_app_version_model
from mobile_framework.version.serializers import AppVersionSerializer

Device = get_device_model()
AppVersion = get_app_version_model()


class DeviceSerializer(serializers.ModelSerializer):
    """ Serializer for the Device """
    app_version = AppVersionSerializer()

    def create(self, validated_data):
        app_version_data = validated_data.pop('app_version')
        app_version, _ = AppVersion.objects.get_or_create(defaults=app_version_data, **app_version_data)
        return Device.objects.create(app_version=app_version, **validated_data)

    def update(self, instance, validated_data):
        fields = self.Meta.fields
        app_version_data = validated_data.pop('app_version', None)
        app_version, _ = AppVersion.objects.get_or_create(defaults=app_version_data, **app_version_data)

        for field in fields:
            if field == 'app_version':
                instance.app_version = app_version
            else:
                instance_value = getattr(instance, field, None)
                setattr(instance, field, validated_data.get(field, instance_value))
        instance.save()
        return instance

    class Meta:
        model = Device
        fields = ('uuid', 'app_version', 'device', 'os', 'os_version', 'screen', 'first_seen', 'last_seen')