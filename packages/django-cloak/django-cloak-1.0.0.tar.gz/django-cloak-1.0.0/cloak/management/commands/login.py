from __future__ import print_function
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.core.signing import TimestampSigner
from django.core.urlresolvers import reverse
from django.core.exceptions import FieldError
from ...views import login

class Command(BaseCommand):
    args = '[USERNAME_FIELD value]'
    help = 'Login as a user using a temporary URL'

    def handle(self, *args, **options):
        """
        With no arguments, find the first user in the system with the
        is_superuser or is_staff flag set to true, or just the first user in
        the system period.

        With a single argument, look for the user with that value as the
        USERNAME_FIELD value.

        When a user is found, print out a URL slug you can paste into your
        browser to login as the user.
        """
        user_model = get_user_model()

        if len(args) == 0:
            # find the first superuser, or staff member or user
            filters = [{"is_superuser": True}, {"is_staff": True}, {}]
            user = None
            for f in filters:
                try:
                    user = user_model._default_manager.filter(**f).order_by("pk").first()
                    if user:
                        break
                except FieldError as e:
                    pass

            if user is None:
                raise CommandError("No users found!")

        elif len(args) == 1:
            # find the user with the USERNAME_FIELD equal to the command line
            # argument
            try:
                user = user_model._default_manager.get_by_natural_key(args[0])
            except user_model.DoesNotExist as e:
                raise CommandError("The user does not exist")
        else:
            raise CommandError("You passed me too many arguments")

        signer = TimestampSigner()
        signature = signer.sign(str(user.pk))

        self.stdout.write(reverse(login, args=(signature,)))
