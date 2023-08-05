from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from mobile_framework import get_app_version_model
from mobile_framework.version.models import Version

AppVersion = get_app_version_model()


class AppVersionSerializer(serializers.ModelSerializer):
    version = serializers.CharField(source='version_raw')

    def validate_version(self, value):
        if isinstance(value, Version):
            return value
        else:
            return Version(value)

    def validate(self, attrs):
        version = attrs.pop('version_raw', None)
        attrs['version_raw'] = int(Version(version))
        return attrs

    def update(self, instance, validated_data):
        raise Exception(_(u'AppVersion cannot be updated outside of the Admin Panel.'))

    class Meta:
        model = AppVersion
        fields = ('version', 'status', 'app_store_build')