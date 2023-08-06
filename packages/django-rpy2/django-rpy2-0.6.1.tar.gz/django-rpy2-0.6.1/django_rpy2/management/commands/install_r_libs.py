from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.utils.importlib import import_module

from django_rpy2.models import AvailableLibrary

import sys

class Command(NoArgsCommand):
    help = "Can be run as a cronjob or directly to install any scheduled libraries."

    def handle_noargs(self, **options):
        for lib in AvailableLibrary.objects.filter(scheduled=True):
            sys.stderr.write("Installing R Library: %s" % str(lib))
            sys.stderr.flush()
            sys.stderr.write(" (%s)\n" % str(lib.install()))
        AvailableLibrary.objects.refresh()

