from django.db import models
from django.utils import six
from django.utils.translation import ugettext as _


class Version(object):
    """
    Simple type that holds a three-part version number and can represent it as
    an integer or string. e.g. '2.0.1'.
    """
    StringTypes = (six.string_types, six.text_type, bytes)

    def __init__(self, value):
        if (isinstance(value, self.StringTypes)):  
            self._value = Version._str2int(value)
        else:
            self._value = int(value)

    def __repr__(self):
        return "AppVersion({})".format(self._value)

    def __str__(self):
        return "{}.{}.{}".format(self._value >> 16, (self._value >> 8) & 255, self._value & 255)

    def __int__(self):
        return self._value

    @staticmethod
    def _str2int(val):
        """
        Converts the Version into an INT equivalent.
        """
        error_msg = _("Invalid version string: '{}'. Expected e.g. '1.2.0'".format(val))
        parts = val.split('.')
        if len(parts) != 3:
            raise ValueError(error_msg)
        try:
            parts = [int(p) for p in parts]
        except ValueError:
            raise ValueError(error_msg)
        for p in parts:
            if p < 0 or p > 99:
                raise ValueError("Invalid version component '{}': {}".format(p, val))
        return (parts[0] << 16) | (parts[1] << 8) | parts[2]


class AppVersionManager(models.Manager):
    """
    A Manger that accepts integral or string representations of the 'version' 
    field 
    """
    def _convert_version_arg(self, kwargs):
        if 'version' in kwargs:
            kwargs['version_raw'] = int(Version(kwargs['version']))
            del kwargs['version']

    def get(self, **kwargs):
        self._convert_version_arg(kwargs)
        return super(AppVersionManager, self).get(**kwargs)

    def create(self, **kwargs):
        self._convert_version_arg(kwargs)
        return super(AppVersionManager, self).create(**kwargs)


class AppVersionBase(models.Model):
    """ 
    Base model that will contain information about the different versions of the 
    mobile application. Versions that weren't added by the administrators 
    (auto-created when a device checks to the server).
    """
    version_raw = models.IntegerField(blank=True, unique=True, db_index=True)
    STATUS_PUBLISHED = 0
    STATUS_DEVELOPMENT = 1
    STATUS_UNKNOWN = 2  # Applied to any unrecognized version that is auto-created when a device calls home
    STATUS_CHOICES = (
        (STATUS_PUBLISHED, "Published"),
        (STATUS_DEVELOPMENT, "In development"),
        (STATUS_UNKNOWN, "Unknown"),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, null=False, default=STATUS_DEVELOPMENT)
    app_store_build = models.CharField(blank=True, max_length=7, help_text=_("The 7 character git commit hash of the signed build submitted to the app stores."))

    objects = AppVersionManager()

    @property
    def version(self):
        return Version(self.version_raw)

    @version.setter
    def version(self, value):
        " .version can be set to a Version(), a string 'a.b.c', or an int "
        if isinstance(value, Version):
            self.version_raw = int(value)
        else:
            self.version_raw = int(Version(value))

    def __str__(self):
        return str(self.version)

    class Meta:
        verbose_name = 'App Version'
        verbose_name_plural = 'App Versions'
        abstract = True
        ordering = ('-version_raw',)


class AppVersion(AppVersionBase):
    class Meta(AppVersionBase.Meta):
        swappable = "MOBILE_FRAMEWORK_APP_VERSION_MODEL"