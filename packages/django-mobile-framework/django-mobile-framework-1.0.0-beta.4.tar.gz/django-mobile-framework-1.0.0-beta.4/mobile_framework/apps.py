from django.apps import AppConfig

class MobileFrameworkConfig(AppConfig):
    name = 'mobile_framework'
    verbose_name = 'Mobile Framework'

class VersionConfig(AppConfig):
    name = 'mobile_framework.version'
    verbose_name = 'Mobile App Version'