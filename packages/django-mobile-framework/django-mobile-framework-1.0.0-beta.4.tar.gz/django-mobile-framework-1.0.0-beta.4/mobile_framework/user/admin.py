from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as AuthAdmin
from django.core.urlresolvers import reverse
from mobile_framework.core.admin import ReadonlyTabularInline
from mobile_framework.user.models import AppUser, AppUserProgression
from mobile_framework.user.forms import UserCreationForm, UserChangeForm

User = get_user_model()


class UserAdmin(AuthAdmin):
    """ Custom UserAdmin based on Django's default UserAdmin """
    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Information', {'fields': ('name', 'short_name')}),
        ('Permissions', {'fields':  ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')
        }),
    )
    readonly_fields = ('last_login', 'date_joined')
    
    list_display = ('username', 'email', 'name', 'short_name', 'is_staff', 'is_active', 'last_login')
    list_filter = ('is_staff', 'is_active', 'last_login')
    search_fields = ('username', 'email', 'name', 'short_name')
    ordering = ('username', 'email')
    filter_horizontal = ('groups', 'user_permissions')

admin.site.register(User, UserAdmin)


class AppUserProgressionInline(ReadonlyTabularInline):
    model = AppUserProgression
    verbose_name_plural = ('User progression')
    fields = ('app_session_id', 'module_name', 'enter_timestamp_friendly', 'time_spent_friendly')
    readonly_fields = ('module_name', 'enter_timestamp_friendly', 'time_spent_friendly')
    ordering = ['enter_timestamp']

    def get_queryset(self, request):
        if not self.has_change_permission(request):
            return get_queryset.none()
        # Ues the "detailed" queryset that gives us "time_spent"
        qs = self.model.objects_detailed.get_queryset()
        # And select_related to avoid hundreds of user/mission/location queries
        qs = qs.select_related('app_user',)
        return qs

    def enter_timestamp_friendly(self, inst):
        return inst.enter_timestamp.strftime("%B %d, %Y. %H:%M:%S")
    enter_timestamp_friendly.short_description = "Enter Time"


class AppUserAdmin(admin.ModelAdmin):
    fields = ('user', 'device_link_detailed')
    readonly_fields = fields
    list_display = ('user', 'device_link', 'app_version')
    inlines = (AppUserProgressionInline,)

    def get_queryset(self, request):
        qs = super(AppUserAdmin, self).get_queryset(request)
        # Select_related to avoid hundreds of related object queries
        qs = qs.select_related('device', 'device__app_version')
        return qs

    def device_link(self, inst):
        return u'<a href="{}">{}</a>'.format(inst.device.get_admin_url(), inst.device)
    device_link.short_description = u"Device"
    device_link.allow_tags = True

    def device_link_detailed(self, inst):
        result = u'<a href="{}">{}</a>'.format(inst.device.get_admin_url(), inst.device)
        other_users = inst.device.num_users() - 1
        if other_users > 0:
            result += " ({} other users)".format(other_users)
        else:
            result += " (sole user)"
        return result
    device_link_detailed.short_description = u"Device"
    device_link_detailed.allow_tags = True

    def has_add_permission(self, *args, **kwargs):
        return False

admin.site.register(AppUser, AppUserAdmin)