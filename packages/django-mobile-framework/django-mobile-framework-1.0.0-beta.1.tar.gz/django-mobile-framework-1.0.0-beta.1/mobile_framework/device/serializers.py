from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from mobile_framework import get_device_model

Device = get_device_model()


class DeviceSerializer(serializers.ModelSerializer):
    """ Serializer for the Device """
    class Meta:
        model = Device
        fields = ('id', 'uuid', 'app_version', 'build', 'device', 'os', 'os_version', 'screen', 'first_seen', 'last_seen', 'alias')
        read_only_field = ('alias',)