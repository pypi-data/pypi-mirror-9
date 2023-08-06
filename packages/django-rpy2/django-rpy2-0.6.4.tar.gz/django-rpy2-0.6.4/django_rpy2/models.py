from django.db.models import *
from django.utils.text import slugify
from django.utils.timezone import now
from django.core.files.base import File
from django.dispatch import receiver

import os
import sys

from .settings import DATABASES, LIB_PATH
from .core import *

__all__ = ('AvailableLibrary', 'UploadedScript', 'ScriptResult')

class LibraryManager(Manager):
    def refresh(self):
        for (name, version, location) in AvailableLibrary.PACKAGES.installed():
            goc = self.get_or_create(name=name, location=location,
                    defaults=dict(installed=now(), scheduled=False))
            goc[0].version = version
            goc[0].save()

class AvailableLibrary(Model):
    PACKAGES  = Packages()

    name      = CharField(max_length=32, choices=PACKAGES)
    version   = CharField(max_length=12, null=True, blank=True)
    location  = CharField(max_length=255, default="unknown")
    installed = DateTimeField(null=True, blank=True)
    attempted = DateTimeField(null=True, blank=True)
    scheduled = BooleanField("Schedule Install", default=True)

    objects = LibraryManager()

    class Meta:
        verbose_name_plural = 'Available Libraries'
        unique_together = ('name', 'location')

    def __str__(self):
        (a, b) = (bool(self.installed), bool(self.attempted))
        if self.location[0] == '/' and \
           self.location.rstrip('/') != LIB_PATH.rstrip('/'):
            msg = 'system lib'
        else:
            msg = [['not installed', 'failed install'],
                   ['manual install', 'installed']][a][b]

        if self.scheduled:
            msg = 'scheduled'

        version = self.version + ' ' if self.version else ''
        return "%s (%s%s)" % (self.name, version, msg)

    def is_installed(self):
        return bool(self.installed)
    is_installed.boolean = True

    def install(self):
        self.attempted = now()
        self.scheduled = False
        if Library().install(self.name):
            self.installed = now()
            self.location = LIB_PATH
        self.save()
        return bool(self.installed)

    def uninstall(self, keep=True):
        Library().uninstall(self.name)
        if keep:
            self.installed = None
            self.location = 'deleted'
            self.save()


@receiver(signals.pre_delete, sender=AvailableLibrary, dispatch_uid='dellib')
def delete_lib(sender, instance, using, **kwargs):
    instance.uninstall(keep=False)


DB_CHOICES = [ (db, db) for db in DATABASES.keys() ]

class UploadedScript(Model):
    name  = CharField(max_length=64)
    slug  = SlugField(max_length=64)
    libs  = ManyToManyField(AvailableLibrary, null=True, blank=True, limit_choices_to={'installed__isnull': False})
    db    = CharField('Database', max_length=32, choices=DB_CHOICES, null=True, blank=True)

    rsc   = TextField('R Script', help_text="""Use data sources:

      Uploaded CSV Data is available as 'csv'
      Website databases available as 'default' or name of database.
      Output filename is 'filename'.
    """)
    csv    = FileField('CSV Data', upload_to='rpy/csv/', null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super(UploadedScript, self).save()

    def get_libs(self):
        libs = Library()
        for lib in self.libs.filter(installed__isnull=False):
            try:
                libs.append(lib.name)
            except ImportError:
                lib.installed = None
                lib.save()
        return libs

    def run(self, **variables):
        result = self.results.create()
        result.started = now()
        result.save()

        runner = ScriptRunner(libs=self.get_libs())

        if self.db:
            runner.use_database(self.db)

        try:
            ret = runner.run(str(self.rsc).replace('\r',''), **variables)
        except Exception as error:
            result.error = True
            result.result = str(error)
        else:
            result.result = str(ret)

        if os.path.isfile(runner.filename):
            with open(runner.filename, 'r') as fhl:
                result.fn_out.save(os.path.basename(runner.filename), File(fhl))
                os.unlink(runner.filename)

        result.output = runner.r.out
        result.ended = now()
        result.save()

        return result


class ScriptResult(Model):
    script = ForeignKey(UploadedScript, related_name='results')

    started = DateTimeField(null=True, blank=True)
    ended   = DateTimeField(null=True, blank=True)

    fn_out = FileField('File Output', upload_to='rpy/out/', null=True, blank=True)
    output = TextField('Printed to Screen', null=True, blank=True)
    result = TextField('Result or Error', null=True, blank=True)
    error  = BooleanField(default=False)

    class Meta:
        ordering = ('-started',)

    def __str__(self):
        return "Script run for '%s' on '%s'" % (str(self.script), str(self.started))


