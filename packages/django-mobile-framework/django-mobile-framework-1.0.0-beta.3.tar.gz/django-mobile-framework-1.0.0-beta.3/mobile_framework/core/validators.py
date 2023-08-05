from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator


class RelatedObjectFieldUniqueValidator(UniqueValidator):

    def set_context(self, serializer_field):
        """
        This hook is called by the serializer instance,
        prior to the validation call being made.
        """
        # Determine the underlying model field name. This may not be the
        # same as the serializer field name if `source=<>` is set.
        self.field_name = serializer_field.source_attrs[-1]
        # Determine the existing instance, if this is an update operation.
        self.instance = getattr(serializer_field.parent, 'instance', None)


class RequiredOnCreateValidator:
    default_message = _('This field is required.')

    def __init__(self, message=None):
        self.message = message if message else self.default_message

    def set_context(self, serializer_field):
        self.field = serializer_field
        self.is_create = serializer_field.parent.instance is None

    def __call__(self, value):
        if self.is_create and not value:
            raise ValidationError(self.message)