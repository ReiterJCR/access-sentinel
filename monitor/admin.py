from django.contrib import admin

from .models import AccessLog, File, User, AnomalyLog

admin.site.register(User)
admin.site.register(File)
admin.site.register(AccessLog)
admin.site.register(AnomalyLog)
