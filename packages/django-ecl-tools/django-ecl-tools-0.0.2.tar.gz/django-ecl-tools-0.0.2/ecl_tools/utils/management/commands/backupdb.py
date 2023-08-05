import os
import datetime
import subprocess
import logging

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from boto.s3.connection import S3Connection
from boto.s3.key import Key


def get_backup_settings(prefix='backup', defaults=dict()):

    s = dict()

    AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
    if not AWS_ACCESS_KEY_ID:
        raise Exception('Missing setting AWS_ACCESS_KEY_ID.')

    s.update({'AWS_ACCESS_KEY_ID': AWS_ACCESS_KEY_ID})


    AWS_SECRET_ACCESS_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
    if not AWS_SECRET_ACCESS_KEY:
        raise Exception('Missing setting AWS_SECRET_ACCESS_KEY.')

    s.update({'AWS_SECRET_ACCESS_KEY': AWS_SECRET_ACCESS_KEY})

    BACKUP_BUCKET_NAME = getattr(settings, 'BACKUP_BUCKET_NAME', None)
    if not BACKUP_BUCKET_NAME:
        raise Exception('Missing setting BACKUP_BUCKET_NAME.')

    s.update({'BACKUP_BUCKET_NAME': BACKUP_BUCKET_NAME})

    BACKUP_PATH = getattr(settings, 'BACKUP_PATH', '')
    if not BACKUP_PATH:
        BACKUP_PATH = ''
    elif BACKUP_PATH[-1:] != '/':
        BACKUP_PATH = BACKUP_PATH + '/'

    s.update({'BACKUP_PATH': BACKUP_PATH})

    TEMP_PATH = getattr(settings, 'TEMP_PATH', '')
    if not TEMP_PATH:
        TEMP_PATH = '/tmp'
    elif TEMP_PATH[-1:] != '/':
        TEMP_PATH = TEMP_PATH + '/'

    s.update({'TEMP_PATH': TEMP_PATH})

    s.update({'user': settings.DATABASES['default']['USER']})
    s.update({'password': settings.DATABASES['default']['PASSWORD']})
    host = settings.DATABASES['default']['HOST']
    if host == '':
        host = 'localhost'
    s.update({'host': host})
    s.update({'dbname': settings.DATABASES['default']['NAME']})

    s.update({'tmp_filename': '%s_%s.sql' % (s['dbname'], prefix)})
    s.update({'tmp_file': lambda: os.path.join(s['TEMP_PATH'], s['tmp_filename'])})
    s.update({'tmp_zip_file': lambda: os.path.join(s['TEMP_PATH'], s['tmp_filename'] + '.gz')})


    s.update(**defaults)


    if os.path.exists(s['tmp_file']()):
        os.remove(s['tmp_file']())

    if os.path.exists(s['tmp_zip_file']()):
        os.remove(s['tmp_zip_file']())

    return s


def add_path(s, key):
    """
    [backup path]/[key]
    """
    return '%s%s' % (s['BACKUP_PATH'], key)

def format_key_filename(database_name, date):
    """
    yyyy-MM/[dbname]_dd-hh-mm.sql.gz
    """
    return '%d-%d/%s_%d-%d-%d.sql.gz' % (date.year, date.month, database_name, date.day, date.hour, date.minute)

def format_key_filter(database_name, date):
    """
    yyyy-MM/[dbname]_dd
    """
    return '%d-%d/%s_%d' % (date.year, date.month, database_name, date.day)


#backupdb command
class Command(BaseCommand):
    help = 'Backup the database and archive in Amazon S3.'
    args = ''

    def handle(self, *args, **options):

        #try:

        s = get_backup_settings()

        sts = subprocess.call("export PGPASSWORD=%s && pg_dump -U %s -h %s %s > %s && export PGPASSWORD=" % (
        s['password'].replace('$', '\\$').replace('&', '\\&').replace('(', '\\('), s['user'], s['host'], s['dbname'], s['tmp_file']()), shell=True)
        sts = subprocess.call("gzip -9 %s" % s['tmp_file'](), shell=True)

        conn = S3Connection(s['AWS_ACCESS_KEY_ID'], s['AWS_SECRET_ACCESS_KEY'])
        bucket = conn.get_bucket(s['BACKUP_BUCKET_NAME'])
        now = datetime.datetime.now()
        k = Key(bucket)
        k.key = add_path(s, format_key_filename(s['dbname'], now))
        k.set_contents_from_filename(s['tmp_zip_file']())
        k.set_acl('private')
        conn.close()

        # except Exception, e:
        #   #logger.exception(e)
        #   raise
