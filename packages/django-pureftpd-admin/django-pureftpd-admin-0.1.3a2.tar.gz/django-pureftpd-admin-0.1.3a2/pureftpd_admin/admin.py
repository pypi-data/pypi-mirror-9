__author__ = 'ivan'

from django.conf import settings
from django.contrib import admin

from .forms import FtpUsersAdminForm
from .models import FtpUsers

class FtpUsersAdmin(admin.ModelAdmin):
    search_fields = ['username', 'path']
    list_display = ['username', 'password', 'display_link_uri', 'uid', 'gid', 'path', 'is_active']
    list_editable = ['is_active']
    list_filter = ['uid', 'gid', 'is_active',
                   'upload_bandwidth', 'download_bandwidth',
                   'upload_ratio', 'download_ratio', 'ipaccess',
                   'quota_files', 'quota_size']
    form = FtpUsersAdminForm
    list_max_show_all = 500

    fieldsets = (
        (None, {
            'fields': ('username', 'password', 'uid', 'gid', 'path','is_active',)
        }),
        ('Restriction options', {
            'classes': ('collapse',),
            'fields': ('upload_bandwidth', 'download_bandwidth', 'upload_ratio', 'download_ratio', 'ipaccess', 'quota_size', 'quota_files')
        }),
        (None, {
            'fields': ('description',)
        }),
    )

    class Media:
        js = (settings.STATIC_URL + 'localdir/js/script.js',)
        css = {
            'all': (settings.STATIC_URL + 'localdir/css/styles.css',)
        }

admin.site.register(FtpUsers, FtpUsersAdmin)
