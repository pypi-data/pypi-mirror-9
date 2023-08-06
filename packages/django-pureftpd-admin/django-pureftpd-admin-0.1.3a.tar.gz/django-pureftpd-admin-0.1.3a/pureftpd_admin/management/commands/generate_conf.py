# -*- coding: utf-8 -*-
__author__ = 'ivan'


from django.db.models.loading import get_model
from django.db.models.query_utils import Q
from django.utils.datastructures import SortedDict
from django.db import connections
from django.core.management.base import BaseCommand, CommandError

from optparse import make_option

FtpUsers = get_model(app_label='pureftpd_admin', model_name='ftpusers')


class Command(BaseCommand):
    help = """Write to stdout example config for pureftpd when using mysql authentication

Add this argument in command line's run pureftpd server '-l mysql:/etc/pureftpd-mysql.conf'

INFO:

\L is replaced by the login of a user trying to authenticate.
\I is replaced by the IP address the client connected to.
\P is replaced by the port number the client connected to.
\R is replaced by the remote IP address the client connected from.
\D is replaced by the remote IPv4 address, as a long decimal number.

You will be comment some line if you don't want to use it."""


    def __init__(self):
        super(Command, self).__init__()
        self.option_list += (
            make_option('--socket', help="Mysql socket"),
            make_option('--address', dest="ADDRESS:PORT", help="Mysql address for connection, default is 'localhost:3306'"),
            make_option('--database-alias', default='default', help="Django database alias from DJANGO_SETTINGS_MODULE"),
            make_option('--any', action="store_true", default=False, help="Use not only cleartext password if field"),
        )

    def handle(self, *args, **options):
        context = SortedDict({})

        if options['socket']:
            context['MYSQLSocket'] = options['socket']
        elif options['ADDRESS:PORT']:
            context['MYSQLServer'], context['MYSQLPort'] = options['ADDRESS:PORT'].split(':')
        else:
            context['MYSQLServer'], context['MYSQLPort'] = ('localhost', '3306')

        if not options['any']:
            context['MYSQLCrypt'] = 'cleartext'

        try:
            connection = connections[options['database_alias']]
        except:
            raise CommandError("Can't find db or user for specified database alias: '%s'" % options['database_alias'])

        context['MYSQLDatabase'] = connection.settings_dict['NAME']
        context['MYSQLUser'] = connection.settings_dict['USER']
        context['MYSQLPassword'] = connection.settings_dict['PASSWORD']


        context['MYSQLGetPW'] = FtpUsers.objects.filter(username='"\L"', is_active=True).filter(Q(ipaccess='"*"') | Q(ipaccess='"\R"'))\
            .only('password').values_list('password', flat=True).query
        context['MYSQLGetUID'] = FtpUsers.objects.filter(username='"\L"')\
            .only('uid').values_list('uid', flat=True).query
        context['MYSQLGetGID'] = FtpUsers.objects.filter(username='"\L"')\
            .only('gid').values_list('gid', flat=True).query
        context['MYSQLGetDir'] = FtpUsers.objects.filter(username='"\L"')\
            .only('path').values_list('path', flat=True).query

        #Quota
        context['MySQLGetQTAFS'] = FtpUsers.objects.filter(username='"\L"')\
            .only('quota_files').values_list('quota_files', flat=True).query
        context['MySQLGetQTASZ'] = FtpUsers.objects.filter(username='"\L"')\
            .only('quota_size').values_list('quota_size', flat=True).query
        #Ratio
        context['MySQLGetRatioUL'] = FtpUsers.objects.filter(username='"\L"')\
            .only('upload_ratio').values_list('upload_ratio', flat=True).query
        context['MySQLGetRatioDL'] = FtpUsers.objects.filter(username='"\L"')\
            .only('download_ratio').values_list('download_ratio', flat=True).query
        #Bandwidth
        context['MySQLGetBandwidthUL'] = FtpUsers.objects.filter(username='"\L"')\
            .only('upload_bandwidth').values_list('upload_bandwidth', flat=True).query
        context['MySQLGetBandwidthDL'] = FtpUsers.objects.filter(username='"\L"')\
            .only('download_bandwidth').values_list('download_bandwidth', flat=True).query

        for option, value in context.iteritems():
            print option, '\t', value
