from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _

from uuidfield.fields import UUIDField

from mobile_framework import get_app_version_model
from mobile_framework.version.models import Version

DEVICE_NAMES = {
    'iPhone1,2': 'iPhone 3G',
    'iPhone2,1': 'iPhone 3GS',
    'iPhone3,1': 'iPhone 4',  # GSM
    'iPhone3,3': 'iPhone 4',  # CDMA
    'iPhone4,1': 'iPhone 4S',
    'iPhone5,1': 'iPhone 5',  # GSM/LTE/AWS
    'iPhone5,2': 'iPhone 5',  # CDMA
    'iPhone5,3': 'iPhone 5c',
    'iPhone5,4': 'iPhone 5c',
    'iPhone6,1': 'iPhone 5s',
    'iPhone6,2': 'iPhone 5s',
    'iPod1,1': 'iPod touch Original',
    'iPod2,1': 'iPod touch 2nd Gen',
    'iPod3,1': 'iPod touch 3rd Gen',
    'iPod4,1': 'iPod touch 4th Gen',
    'iPod5,1': 'iPod touch 5th Gen',
    'iPad1,1': 'iPad Original',
    'iPad2,1': 'iPad 2',
    'iPad2,2': 'iPad 2',
    'iPad2,3': 'iPad 2',
    'iPad2,4': 'iPad 2',
    'iPad2,5': 'iPad mini',
    'iPad3,1': 'iPad 3rd Gen',
    'iPad3,2': 'iPad 3rd Gen',
    'iPad3,3': 'iPad 3rd Gen',
    'iPad3,4': 'iPad 4th Gen',
    'iPad3,5': 'iPad 4th Gen',
    'SGH-I747M': 'Samsung Galaxy S III',
    'SCH-I535': 'Samsung Galaxy S III',
    'SPH-D710': 'The Samsung Galaxy S II Epic',
    'SGH-T989D': 'Samsung Galaxy S II X',
    'SGH-I317M': 'Samsung Galaxy Note II',
    'GT-S7560M': 'Samsung Galaxy Ace II x',
}


class DeviceBase(models.Model):
    """
    Base model that will contain information about the different devices that 
    have checked into the server.
    """
    uuid = UUIDField(unique=True, db_index=True, verbose_name=_('Unique ID'))
    app_version = models.ForeignKey(settings.MOBILE_FRAMEWORK_APP_VERSION_MODEL, swappable=True, related_name='devices')
    device = models.CharField(max_length=100) # The name of the device (ie. IOS)
    os = models.CharField(max_length=100) # The name of the operating system of the device (ie. Darwin)
    os_version = models.CharField(max_length=100) # Version of the operating system
    screen = models.CharField(max_length=25)  # example value "320x640"
    first_seen = models.DateTimeField(auto_now_add=True) 
    last_seen = models.DateTimeField(auto_now_add=True)
    alias = models.CharField(blank=True, null=False, max_length=100)  # Custom, staff-specified name for this device

    class Meta:
        abstract = True
        ordering = ("device",)

    def __str__(self):
        if self.alias:
            return u"{} ({})".format(self.alias, str(self.uuid)[-6:])
        return u"Anonymous {} ({})".format(self.device_friendly(), str(self.uuid)[-6:])

    def num_users(self):
        return self.app_users.count()
    num_users.short_description = "# of users"

    @staticmethod
    def get_friendly_device_name(code):
        return DEVICE_NAMES.get(code, code)

    def device_friendly(self):
        return self.get_friendly_device_name(self.device)
    device_friendly.short_description = u"Device"

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse('admin:{}_{}_change'.format(content_type.app_label, content_type.model), args=(self.uuid,))


class Device(DeviceBase):
    class Meta(DeviceBase.Meta):
        swappable = "MOBILE_FRAMEWORK_DEVICE_MODEL"