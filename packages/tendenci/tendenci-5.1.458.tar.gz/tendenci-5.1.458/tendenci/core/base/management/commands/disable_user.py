import sys
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission, User
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
    """
    Disable user in the system

    This command does the following to the user account:
        * Removes them from all groups
        * Removes all user level permissions
        * Sets is_staff to 0
        * Sets is_superuser to 0
        * Sets is_active to 0
        * Removes them from all tendenci user_groups
    """
    option_list = BaseCommand.option_list + (
        make_option('--username',
            action='store',
            dest='username',
            default=None,
            help='Username of the user account being disabled'),
        make_option('--email',
            action='store',
            dest='email',
            default=None,
            help='Email of the user account being disabled'),
        )


    def handle(self, *args, **options):
        from tendenci.apps.user_groups.models import GroupMembership

        verbosity = options['verbosity']
        username = options['username']
        email = options['email']

        if not any([username, email]):
            raise CommandError('downgrade_user: --username or email parameter is required')

        # get the user
        if username and email:
            users = User.objects.filter(username=username, email=email)
            if not users:
                print 'User with username=%s and email=%s could not be found' % (username, email)
        elif username:
            users = User.objects.filter(username=username)
            if not users:
                print 'User with username=%s could not be found' % username
        else:
            users = User.objects.filter(email=email)
            if not users:
                print 'User with email=%s could not be found' % email

        if not users:
            return

        for u in users:
            # Remove the user from all groups
            u.groups.clear()

            # Remove all user-level permissions
            u.user_permissions.clear()

            # Reset permission bits
            u.is_staff = False
            u.is_superuser = False
            u.is_active = False
            u.save()

            # Remove the tendenci group permissions
            group_memberships = GroupMembership.objects.filter(member=u)
            for m in group_memberships:
                m.delete()

            if verbosity >= 2:
                print 'Done downgrading user (%s).' % u
