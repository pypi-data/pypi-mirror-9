from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class HasCreateRequired(serializers.ModelSerializer):
    default_error_message = _('{field_name} is required.')

    def check_create_required_fields(self, attrs):
        error_list = {}
        for field in self.create_required_fields:
            parsed_field, data = self._get_data(field, attrs)
            if not data:
                error_list[parsed_field] = self.default_error_message.format(field_name=parsed_field)
        if error_list:
            raise ValidationError(error_list)

    def _get_data(self, field, attrs):
        keys = field.split('.')
        parsed_field = keys[0]
        parent = attrs.get(keys[0], None)
        if len(keys) == 2:
            parsed_field = keys[1]
            if parent:
                return parsed_field, parent.get(keys[1], None)
            else:
                return parsed_field, None
        return parsed_field, parent

    def validate(self, attrs):
        super(HasCreateRequired, self).validate(attrs)
        if not self.instance:
            self.check_create_required_fields(attrs)
        return attrs