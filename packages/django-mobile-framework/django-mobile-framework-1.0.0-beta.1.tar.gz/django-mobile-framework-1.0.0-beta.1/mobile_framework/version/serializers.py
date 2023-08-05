from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from mobile_framework import get_app_version_model
from mobile_framework.version.models import Version, AppVersion


class AppVersionSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppVersion
        fields = ('version', 'version_raw', 'status', 'app_store_build')
        read_only_fields = ('version',)
        write_only_feilds = ('version_raw',)

    def validate(self, attrs):
        """
        Check if the version is given, and check if it's the correct format 
        (1.1.1).
        """
        try:
            version_str = self.initial_data['version']
            version = Version(version_str)
            version_raw = version
        except KeyError as e:
            raise ValidationError('Version is required.')
        except ValueError as e:
            raise ValidationError(e)
        attrs['version_raw'] = version_raw
        return attrs

    def create(self, validated_data):
        """
        Gets or creates the new AppVersion object.
        """
        ModelClass = self.Meta.model
        defaults = {
            'status': ModelClass.STATUS_UNKNOWN
        }
        defaults.update(validated_data)
        obj, _ = ModelClass.objects.get_or_create(version_raw=validated_data['version_raw'], defaults=defaults)
        return obj