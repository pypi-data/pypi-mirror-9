
from django.conf.urls import patterns, url
from django.contrib.admin.views.decorators import staff_member_required

__author__ = 'ivan'

from pureftpd_admin.localdir.views import serve
import pureftpd_admin.settings as ftpusets_settings

urlpatterns = patterns('',
                       url(r'^localdir/(?P<path>.*)$', staff_member_required(serve),
                           kwargs={'document_root': ftpusets_settings.ROOT_PATH}, name='localdir-ftpusers-url')
)
