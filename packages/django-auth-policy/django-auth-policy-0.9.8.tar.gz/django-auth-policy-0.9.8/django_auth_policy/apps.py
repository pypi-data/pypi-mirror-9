from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DjangoAuthPolicyConfig(AppConfig):
    name = 'django_auth_policy'
    verbose_name = _('Django Authentication Policy')

    def ready(self):
        # Import (and register) checks after app is ready
        import django_auth_policy.checks
