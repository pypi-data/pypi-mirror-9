from django.contrib.admin import TabularInline

class ReadonlyTabularInline(TabularInline):
    " http://djangosnippets.org/snippets/2629/ "
    can_delete = False
    extra = 0
    editable_fields = []

    def get_readonly_fields(self, request, obj=None):
        fields = []
        for field in self.fields:
            if (not field == 'id'):
                if (field not in self.editable_fields):
                    fields.append(field)
        return fields

    def has_add_permission(self, request):
        return False