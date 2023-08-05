from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from mobile_framework.version.models import Version, AppVersion


class AppVersionAdminForm(forms.ModelForm):
    version = forms.CharField()

    class Meta:
        model = AppVersion
        fields = ('version', 'status', 'app_store_build')

    def __init__(self, *args, **kwargs):
        super(AppVersionAdminForm, self).__init__(*args, **kwargs)
        self.fields['app_store_build'].widget.attrs['style'] = "font-family: monospace; width: 7em;"
        if self.instance.pk:
            self.fields['version'].initial = str(self.instance.version)

    def clean_version(self):
        try:
            v = Version(self.cleaned_data.get('version', '--').strip())
            return str(v)
        except ValueError as e:
            raise ValidationError(str(e))

    def save(self, *args, **kwargs):
        " Set version_raw using version "
        kwargs['commit'] = False
        obj = super(forms.ModelForm, self).save(*args, **kwargs)
        obj.version = self.cleaned_data.get('version')
        obj.save()
        return obj


class AppVersionAdmin(admin.ModelAdmin):
    form = AppVersionAdminForm
    fields = ('version', 'status', 'app_store_build')
    list_display = ('version', 'status')

admin.site.register(AppVersion, AppVersionAdmin)