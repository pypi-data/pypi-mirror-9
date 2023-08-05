from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from oauth2_provider.models import get_application_model
from mobile_framework import get_app_user_model

@receiver(post_save, sender=settings.MOBILE_FRAMEWORK_APP_USER_MODEL)
def create_oauth_application(sender, **kwargs):
    Application = get_application_model()
    obj = kwargs.get('instance')
    values = {
        'user': obj.user,
        'name': u'{}-application'.format(obj.user.username),
        'client_type': Application.CLIENT_CONFIDENTIAL,
        'authorization_grant_type': Application.GRANT_CLIENT_CREDENTIALS
    }
    Application.objects.create(**values)