import subprocess
import sys
from optparse import OptionParser

from django.core.management import LaxOptionParser
from django.core.management.base import BaseCommand, CommandError

from cas_dev_server.management import subprocess_environment

class Command(BaseCommand):

    option_list = BaseCommand.option_list[1:]
    args = '[command] [arguments]'
    help = 'Runs a management command on the CAS development server.'

    def handle(self, *args, **options):
        if not args:
            raise CommandError('Must specify a command.')
        subprocess_args = (sys.executable, '-m', 'django.bin.django-admin', args[0])
        if options['settings']:
            subprocess_args += '--settings=' + options['settings'],
        if options['pythonpath']:
            subprocess_args += '--pythonpath=' + options['pythonpath'],
        if options['traceback']:
            subprocess_args += '--traceback',
        if options['no_color']:
            subprocess_args += '--no-color',
        subprocess.call(subprocess_args + args[1:], stdout=self.stdout, stderr=self.stderr,
                        env=subprocess_environment())

    def create_parser(self, prog_name, subcommand, parser_class=LaxOptionParser):
        """
        Create and return the ``OptionParser`` which will be used to
        parse the arguments to this command.

        """
        return parser_class(prog=prog_name,
                            usage=self.usage(subcommand),
                            version=self.get_version(),
                            option_list=self.option_list)

    def print_help(self, prog_name, subcommand):
        """
        Print the help message for this command, derived from
        ``self.usage()``.

        """
        parser = self.create_parser(prog_name, subcommand, OptionParser)
        parser.print_help()
