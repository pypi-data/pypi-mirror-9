from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from django_auth_policy.models import LoginAttempt


class Command(BaseCommand):
    help = "Remove all locks on usernames and IP addresses"

    def handle(self, *args, **options):
        c = LoginAttempt.objects.filter(lockout=True).update(lockout=False)
        print u'Unlocked {0} login attempts.'.format(c)
