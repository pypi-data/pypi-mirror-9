from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from djangomaat.register import maat


class Command(BaseCommand):
    help = "Shows all registered handlers."

    def handle(self, *args, **options):

        handlers = maat.get_registered_handlers()

        if not handlers:
            self.stdout.write('No registered handlers found.\n')

        for handler in handlers:
            self.stdout.write('{}\n'.format(handler))
