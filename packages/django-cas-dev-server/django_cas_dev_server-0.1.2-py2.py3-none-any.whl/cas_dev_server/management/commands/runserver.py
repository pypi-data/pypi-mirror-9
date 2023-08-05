import os
import subprocess
import sys
from optparse import make_option

from django.apps import apps

from cas_dev_server.management import subprocess_environment

if apps.is_installed('django.contrib.staticfiles'):
    from django.contrib.staticfiles.management.commands.runserver import Command as RunserverCommand
else:
    from django.core.management.commands.runserver import Command as RunserverCommand

class Command(RunserverCommand):

    option_list = RunserverCommand.option_list + (
        make_option('--nocas', action='store_false', dest='use_cas', default=True,
            help='Tells Django to NOT start the CAS development server.'),
        make_option('--cas-port', action='store', type='int', dest='cas_port', default=8008,
            help='Which port to start the CAS server on (default 8008).'),
    )
    help = 'Starts a lightweight Web server for development and also one for CAS.'

    def run(self, *args, **options):
        """
        Runs the server, using the autoreloader if needed, and starts the CAS server
        """
        if options['use_cas'] and os.environ.get('RUN_MAIN') != 'true':
            subprocess.Popen((sys.executable, '-m', 'django.bin.django-admin', 'runserver',
                              '{}:{}'.format(self.addr, options['cas_port'])),
                             stdout=self.stdout, stderr=self.stderr, env=subprocess_environment())
        super(Command, self).run(*args, **options)
