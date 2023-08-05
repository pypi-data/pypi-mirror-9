from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _
from uuidfield.fields import UUIDField
from mobile_framework.user.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    The main difference between the default and the
    custom user is that the first_name and last_name replaced with full_name
    and short_name.
    """
    name = models.CharField('Full Name', max_length=50, blank=True, null=True)
    short_name = models.CharField('Short Name', max_length=25, blank=True, null=True,
        help_text='What name would you like us to call you?')
    username = models.CharField('username', max_length=30, unique=True,
        help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[
            validators.RegexValidator(r'^[\w.@+-]+$',
                'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid'
            ),
        ],
        error_messages={
            'unique': 'A user with that username already exists.',
        })
    email = models.EmailField('Email', unique=True, blank=True, null=True)
    is_staff = models.BooleanField('staff status', default=False,
        help_text='Designates whether the user can log into this admin '
                    'site.')
    is_active = models.BooleanField('active', default=True,
        help_text='Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.')
    date_joined = models.DateTimeField('date joined', default=timezone.now)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __unicode__(self):
        return self.get_short_name()

    def __str__(self):
        return self.__unicode__()

    def get_short_name(self):
        """
        Returns the user's given short name. Uses the normal name if short_name
        does not exist.
        """
        if not self.short_name:
            if self.name:
                return self.name
            else:
                return self.username
        return self.short_name

    def get_full_name(self):
        return self.name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)


class AppUserBase(models.Model):
    """
    Base model that will be used as the app user profile. This model acts as an 
    identifier for the mobile users.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, swappable=True, blank=True, related_name='app_user')
    device = models.ForeignKey(settings.MOBILE_FRAMEWORK_DEVICE_MODEL, swappable=True, blank=True, db_index=True, verbose_name='app_user', related_name='app_users')

    class Meta:
        verbose_name = "Mobile App User"
        verbose_name_plural = "Mobile App Users"
        abstract = True

    def __str__(self):
        return u"appuser-{}".format(self.pk)

    def app_version(self):
        return self.device.app_version

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse('admin:{}_{}_change'.format(content_type.app_label, content_type.model), args=(self.user.pk,))


class AppUser(AppUserBase):
    class Meta(AppUserBase.Meta):
        swappable = "MOBILE_FRAMEWORK_APP_USER_MODEL"


class DetailedUserProgressionManager(models.Manager):
    def get_queryset(self):
        content_type = ContentType.objects.get_for_model(self.model)
        qs = super(DetailedUserProgressionManager, self).get_queryset()
        qs = qs.extra(select={
            'exit_timestamp': 'lead(enter_timestamp) OVER (PARTITION BY {}_{}.device_id, app_session_id ORDER BY enter_timestamp)'.format(content_type.app_label, content_type.model)
        })
        return qs


class AppUserProgressionBase(models.Model):
    """ Base model that will be used to track the usage of the appuser. """
    device = models.ForeignKey(settings.MOBILE_FRAMEWORK_DEVICE_MODEL, swappable=True, related_name='user_progressions')
    app_user = models.ForeignKey(settings.MOBILE_FRAMEWORK_APP_USER_MODEL, swappable=True, null=True, related_name='user_progressions')
    module_name = models.CharField(max_length=30, null=True) # The name of the module that the user has accessed
    enter_timestamp = models.DateTimeField(null=False) 
    app_session_id = models.IntegerField(null=True) # A random Integer created by the device

    objects = models.Manager()
    objects_detailed = DetailedUserProgressionManager()

    def __str__(self):
        enter_time_string = self.enter_timestamp.strftime("%b %d, %Y %H:%M:%S")
        uuid = None
        if self.app_user is not None:
            uuid = self.app_user.uuid
        return u"{} entered {} on {} during session {}".format(uuid, self.module_name, enter_time_string, self.app_session_id)

    def time_spent(self):
        if not hasattr(self, 'exit_timestamp'):
            raise AttributeError(_("You must use the UserProgression.objects_detailed manager to use this property."))
        if self.exit_timestamp is not None:
            return (self.exit_timestamp - self.enter_timestamp).total_seconds()
        return None

    def time_spent_friendly(self):
        ts = self.time_spent()
        if ts is None:
            return "--"
        if ts > 59:
            return "{m:.0f} m {s:.0f} s".format(m=ts // 60, s=ts % 60)
        return "{:.0f} s".format(ts)
    time_spent_friendly.short_description = "Time spent"

    def enter_timestamp_friendly(self):
        return self.enter_timestamp.strftime("%B %d, %Y. %H:%M:%S")
    enter_timestamp_friendly.short_description = "Enter Time"

    class Meta:
        ordering = ('enter_timestamp',)
        abstract = True


class AppUserProgression(AppUserProgressionBase):
    class Meta(AppUserProgressionBase.Meta):
        swappable = "MOBILE_FRAMEWORK_PROGRESSION_MODEL"