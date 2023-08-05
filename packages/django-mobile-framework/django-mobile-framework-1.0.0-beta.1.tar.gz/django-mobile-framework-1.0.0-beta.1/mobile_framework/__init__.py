"""
A framework containing the commonly used models, and permissions for Morningstar
Enterprises backend servers.
Copyright (C) 2015  Morningstar Enterprises Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
try:
    # Django's new application loading system
    from django.apps import apps
    get_model = apps.get_model
except ImportError:
    from django.db.models import get_model

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models.loading import get_model
from django.utils.translation import ugettext as _

default_app_config = 'mobile_framework.apps.MobileFrameworkConfig'

__all__ = ['get_app_user_model', 'get_device_model', 'get_app_version_model', 'get_app_user_progression_model']

def parse_model(swappable):
    try:
        return swappable.split('.')
    except ValueError:
        raise ImproperlyConfigured(_('{} must be in the format app_label.model_name.'.format(swappable)))

def get_app_user_model():
    """
    Gets the current App User Model, it will return the swapped model if specified in the settings.
    """
    try:
        app_label, model_name = parse_model(settings.MOBILE_FRAMEWORK_APP_USER_MODEL)
        return get_model(app_label, model_name)
    except LookupError:
        raise ImproperlyConfigured(
            _("MOBILE_FRAMEWORK_APP_USER_MODEL refers to model '{}' that has not been installed".format(settings.MOBILE_FRAMEWORK_APP_USER_MODEL))
        )

def get_device_model():
    """
    Gets the current Device Model, it will return the swapped model if specified in the settings.
    """
    try:
        app_label, model_name = parse_model(settings.MOBILE_FRAMEWORK_DEVICE_MODEL)
        return get_model(app_label, model_name)
    except LookupError:
        raise ImproperlyConfigured(
            _("MOBILE_FRAMEWORK_DEVICE_MODEL refers to model '{}' that has not been installed".format(settings.MOBILE_FRAMEWORK_DEVICE_MODEL))
        )

def get_app_version_model():
    """
    Gets the current App Version Model, it will return the swapped model if specified in the settings.
    """
    try:
        app_label, model_name = parse_model(settings.MOBILE_FRAMEWORK_APP_VERSION_MODEL)
        return get_model(app_label, model_name)
    except LookupError:
        raise ImproperlyConfigured(
            _("MOBILE_FRAMEWORK_APP_VERSION_MODEL refers to model '{}' that has not been installed".format(settings.MOBILE_FRAMEWORK_APP_VERSION_MODEL))
        )

def get_app_user_progression_model():
    """
    Gets the current App Version Model, it will return the swapped model if specified in the settings.
    """
    try:
        app_label, model_name = parse_model(settings.MOBILE_FRAMEWORK_PROGRESSION_MODEL)
        return get_model(app_label, model_name)
    except LookupError:
        raise ImproperlyConfigured(
            _("MOBILE_FRAMEWORK_PROGRESSION_MODEL refers to model '{}' that has not been installed".format(settings.MOBILE_FRAMEWORK_PROGRESSION_MODEL))
        )