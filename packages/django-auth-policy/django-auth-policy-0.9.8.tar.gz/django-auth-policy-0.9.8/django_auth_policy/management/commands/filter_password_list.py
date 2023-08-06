from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from django.conf import settings

from django_auth_policy.handlers import PasswordStrengthPolicyHandler


class Command(BaseCommand):
    help = ("Filters a list of password by removing all passwords that do not "
            "comply with the configured password strength policies."
            "Provide file paths as arguments.")

    def handle(self, *args, **options):
        if not args:
            print ("Please provide one or more file paths for files with "
                   "password lists.")
            return

        pw_handler = PasswordStrengthPolicyHandler()

        for arg in args:
            fh = open(arg, 'r')
            for pw in fh:
                try:
                    pw = pw.decode('utf8')
                except UnicodeDecodeError:
                    continue

                pw = pw.strip()

                try:
                    pw_handler.validate(pw)
                except ValidationError:
                    continue

                print pw.encode('utf8')

            fh.close()
