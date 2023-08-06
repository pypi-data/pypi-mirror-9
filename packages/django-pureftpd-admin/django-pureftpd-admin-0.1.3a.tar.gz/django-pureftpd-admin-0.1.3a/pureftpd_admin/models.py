from django.db import models
from django.utils.translation import ugettext_lazy as _

import settings as ftpusets_settings

class FtpUsers(models.Model):
    username = models.CharField(_('User name'), max_length=16, unique=True)
    is_active = models.BooleanField(_('Is active'), default=True)
    password = models.CharField(_('Password'), max_length=64)
    uid = models.SmallIntegerField(_('Uid'), default=ftpusets_settings.DEFAULT_UID)
    gid = models.SmallIntegerField(_('Gid'), default=ftpusets_settings.DEFAULT_GID)
    path = models.TextField(_('Directory on server'))
    upload_bandwidth = models.PositiveSmallIntegerField(_('Upload bandwidth'), default=ftpusets_settings.DEFAULT_UPLOAD_BANDWIDTH,
        help_text=_("MySQLGetBandwidthUL is the upload bandwidth restrictions. Values should be in KB/s."))
    download_bandwidth = models.PositiveSmallIntegerField(_('Download bandwidth'), default=ftpusets_settings.DEFAULT_DOWNLOAD_BANDWIDTH,
        help_text=_("MySQLGetBandwidthDL is the download bandwidth restrictions. Values should be in KB/s."))
    upload_ratio = models.PositiveSmallIntegerField(_('Upload ratio'), default=ftpusets_settings.DEFAULT_UPLOAD_RATIO,
        help_text=_("MySQLGetRatioUL is the ratio upload/download."))
    download_ratio = models.PositiveSmallIntegerField(_('Download ratio'), default=ftpusets_settings.DEFAULT_DOWNLOAD_RATIO,
        help_text=_("MySQLGetRatioDL is the ratio download/upload."))
    description = models.TextField(_('Description'), blank=True)
    ipaccess = models.CharField(_('Ip access'), max_length=15, default=ftpusets_settings.DEFAULT_IPACCESS)
    quota_files = models.PositiveIntegerField(_('Quota files (Num)'), default=ftpusets_settings.DEFAULT_QUOTA_FILES,
        help_text=_('MySQLGetQTAFS is the maximal number of files a user can store in his home directory.'))
    quota_size = models.PositiveSmallIntegerField(_('Quota size (Mb)'), default=ftpusets_settings.DEFAULT_QUOTA_SIZE,
        help_text=_('MySQLGetQTASZ is the maximal disk usage, in Megabytes.'))

    def get_uri(self):
        return "ftp://%(username)s:%(password)s@%(hostname)s" % {'username': self.username,
                                                                'password': self.password,
                                                                'hostname': ftpusets_settings.DEFAULT_HOSTNAME}

    def display_link_uri(self):
        uri = self.get_uri()
        return "<a target='_blank' href='%s'>%s</a>" % (uri, uri)
    display_link_uri.allow_tags = True

    class Meta:
        verbose_name = 'Ftp user'
        verbose_name_plural = 'Ftp users'
        db_table = 'ftpusers'

