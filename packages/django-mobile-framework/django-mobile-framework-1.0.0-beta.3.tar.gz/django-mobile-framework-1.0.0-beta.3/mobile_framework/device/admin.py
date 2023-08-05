from django.contrib import admin

from mobile_framework import get_app_user_model
from mobile_framework.device.models import Device
from mobile_framework.version.models import AppVersion

AppUser = get_app_user_model()


class DeviceAdmin(admin.ModelAdmin):
    fields = ('uuid', 'app_version', 'device_friendly', 'os', 'os_version', 'screen', 'first_seen', 'last_seen', 'alias')
    readonly_fields = ('uuid', 'app_version', 'device_friendly', 'os', 'os_version', 'screen', 'first_seen', 'last_seen')
    list_display = ('__str__', 'app_version_detailed', 'device_friendly', 'num_users', 'last_seen')
    ordering = ('-last_seen', )
    change_form_template = 'admin/device_change_form.html'
    list_filter = ('app_version',)

    def get_queryset(self, request):
        qs = super(DeviceAdmin, self).get_queryset(request)
        # select_related to avoid hundreds of AppVersion queries
        qs = qs.select_related('app_version',)
        return qs

    def num_users(self, obj):
        return AppUser.objects.filter(device=obj).count()
    num_users.short_description = '# Users'

    def app_version_detailed(self, inst):
        result = str(inst.app_version)
        if inst.app_version.status == AppVersion.STATUS_PUBLISHED:
            if inst.build != inst.app_version.app_store_build:
                # The build hash does not match the hash of the signed build
                # that we submitted to the app store.
                result += u' <span style="color: red;" title="Device app build does not match expected value.">({})</span>'.format(inst.build)
        elif inst.app_version.status == AppVersion.STATUS_DEVELOPMENT:
            result += ' <span title="Development version">(dev)</span>'
        else:
            # This is an unknown version
            result += u' <span style="color: red;" title="Unknown version">(??)</span>'
        return result
    app_version_detailed.short_description = "App Version"
    app_version_detailed.allow_tags = True

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        """
        Add User Information used by our custom change_form template
        """
        # Get users
        app_users = AppUser.objects.filter(device=obj).order_by()
        context['app_users'] = app_users
        return super(DeviceAdmin, self).render_change_form(request, context, change, obj, form_url)

    def has_add_permission(self, *args, **kwargs):
        return False

admin.site.register(Device, DeviceAdmin)