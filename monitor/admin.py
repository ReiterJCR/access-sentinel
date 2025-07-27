from django.contrib import admin

from .models import AccessLog, AnomalyLog, File, User

admin.site.register(User)
admin.site.register(File)
admin.site.register(AccessLog)
admin.site.register(AnomalyLog)
