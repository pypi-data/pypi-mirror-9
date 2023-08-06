from django.contrib import admin
from .models import LogEntry

class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('message', 'level', 'logged_at', 'tags')
    readonly_fields = ('level', 'message', 'logged_at', 'tags')
    list_filter = ('level', )
    search_fields = ('message', 'tags__tag')

    def tags(self, obj):
        tags = ''
        for t in obj.tags.all():
            tags += '{}, '.format(t.tag)

        return tags[:-2]

admin.site.register(LogEntry, LogEntryAdmin)

