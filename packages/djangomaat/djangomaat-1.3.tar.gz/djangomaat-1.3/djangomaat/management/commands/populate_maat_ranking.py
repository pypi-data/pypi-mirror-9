from __future__ import unicode_literals

from optparse import make_option

from django.core.management.base import BaseCommand
from django.db.models.loading import get_model

from djangomaat.register import maat


class Command(BaseCommand):
    args = '[<app_label.model_name app_label.model_name ...>]'
    help = "Delete the old ranking and store the new ones."
    option_list = BaseCommand.option_list + (
        make_option('-s', '--simulate',
            action='store_true',
            dest='simulate',
            default=False,
            help='Simulation mode'),
        )

    def get_model_from_arg(self, arg):
        app_label, model_name = arg.split('.')
        return get_model(app_label, model_name)

    def handle(self, *args, **options):
        simulate = options['simulate']
        verbosity = options['verbosity']

        if verbosity > 0:
            logger = self.stdout
        else:
            logger = None

        if args:
            handlers = [maat.get_handler_for_model(self.get_model_from_arg(i))
                        for i in args]
        else:
            handlers = maat.get_registered_handlers()

        if not handlers and verbosity > 0:
            self.stdout.write('No registered handlers found.\n')

        for handler in handlers:
            handler.flush_ordered_objects(logger=logger, simulate=simulate)
