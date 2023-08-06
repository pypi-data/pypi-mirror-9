from django.contrib.admin import *
from django.utils.safestring import mark_safe
from django_object_actions import DjangoObjectActions

from .models import *
from .forms import LibraryForm

def schedule_reinstall(modeladmin, request, queryset):
    queryset.update(installed=None, attempted=None)
schedule_reinstall.short_description = "Re-schedule installation or upgrade"

class LibraryAdmin(ModelAdmin):
    list_display = ('__str__', 'is_installed', 'installed', 'scheduled', 'attempted')
    ordering = 'installed',
    actions = [ schedule_reinstall ]
    readonly_fields = ['installed', 'attempted', 'version']
    form = LibraryForm


class ResultsInline(TabularInline):
    exclude = ['fn_out']
    fields = ['render_url', 'started', 'ended', 'output', 'result']
    readonly_fields = ['render_url', 'output', 'result', 'started', 'ended']
    model = ScriptResult
    extra = 0
    max_num = 0

    def render_url(self, obj):
        if obj.fn_out:
            return mark_safe("""<a href="%s">%s</a>""" % (obj.fn_out.url, obj.fn_out.name))
        return "No File"

class UploadAdmin(DjangoObjectActions, ModelAdmin):
    inlines = [ ResultsInline ]
    exclude = ['slug']
    readonly_fields = []
    objectactions = ('run', 'download')

    class Media:
        css = { 'all' : ('css/no-inline-label.css',) }

    def run(self, request, obj):
        obj.run()

    run.label = "Run Script"
    run.short_description = "Run this script right now (no save)"

    def download(self, request, obj):
        obj.run(save_instead=True)

    download.label = "Download Script"
    download.short_description = "Compile the script as it would be sent to R and output as the result instead of running."


site.register(AvailableLibrary, LibraryAdmin)
site.register(UploadedScript, UploadAdmin)
site.register(ScriptResult)

