from django.contrib import admin
from .models import uploadFile, shareFile, urlMapping, passwordResetRequest

admin.site.register(uploadFile)
admin.site.register(shareFile)
admin.site.register(urlMapping)
admin.site.register(passwordResetRequest)