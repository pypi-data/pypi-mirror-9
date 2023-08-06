from django.db import models


class LogEntry(models.Model):
    level       = models.CharField(max_length=16)
    message     = models.TextField()
    logged_at   = models.DateTimeField(auto_now_add=True)


class LogTag(models.Model):
    tag         = models.CharField(max_length=64)
    log_entries = models.ManyToManyField(LogEntry, related_name='tags')

