from optparse import make_option

from django.core import management
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Migrates data between 2 databases'

    option_list = BaseCommand.option_list + (
        make_option('--origin', action='store', dest='origin',
                    default='sqlite', help='Database alias to use as the source of data'),
        make_option('--destination', action='store', dest='destination',
                    default='default', help='Database alias to use as the destination of data'),
        make_option('--dump-file', action='store', dest='dumpfile',
                    default='/tmp/dump.json', help='Name of fixture file'),
        make_option('-e', '--exclude', dest='exclude',action='append',
                    default=['contenttypes', 'sessions.Session', 'south.Migrationhistory', 'auth.Permission'],
                    help="An appname or appname.ModelName to exclude (use multiple --exclude to exclude multiple apps/models). "
                    "Defaults to ['contenttypes', 'sessions.Session', 'south.Migrationhistory', 'auth.Permission']"),
    )

    def handle(self, *args, **options):
        self.origin = options.get('origin')
        self.destination = options.get('destination')
        self.dumpfile = options.get('dumpfile')
        self.exclude = options.get('exclude')

        # setup the destication db
        self.stdout.write("Setting up destination: %s\n" % self.destination)
        management.call_command('syncdb', database=self.destination, interactive=False, load_initial_data=False)
        management.call_command('migrate', database=self.destination, load_inital_data=False)

        # dump sqlite data
        self.stdout.write("Dumping data from origin: %s\n" % self.origin)
        with open(self.dumpfile, 'w+') as f:
            management.call_command('dumpdata',
                                    database=self.origin,
                                    use_base_manager=True,
                                    use_natrual_keys=True,
                                    exclude=self.exclude,
                                    stdout=f,
            )

        # load dump
        self.stdout.write("Loading data into destination: %s\n" % self.destination)
        management.call_command('loaddata', self.dumpfile, using=self.destination)

        self.stdout.write("Successfully migrated")
