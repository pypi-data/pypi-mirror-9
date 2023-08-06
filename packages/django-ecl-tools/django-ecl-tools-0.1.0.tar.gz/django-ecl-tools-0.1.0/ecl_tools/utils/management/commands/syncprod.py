import subprocess
import datetime

import django.db
from django.conf import settings
from django.core.management.base import BaseCommand

from boto.s3.connection import S3Connection

from .backupdb import get_backup_settings, add_path, format_key_filter


def do_sync(s, s3key, skip_download):

    if not skip_download:
        print('Downloading ...')
        s3key.get_contents_to_filename(s['tmp_zip_file']())

        print('Unzipping ...')
        try:
            sts = subprocess.check_output("gunzip %s" % s['tmp_zip_file'](), shell=True)
        except subprocess.CalledProcessError, e:
            return False, "gunzip returned %s" % e.output

    django.db.close_connection()

    print('Restoring DB ...')
    print(s3key)

    cmds = (
        'dropdb %s' % s['dbname'],
        'createdb %s' % s['dbname'],
        'psql -d %s -f %s' % (s['dbname'], s['tmp_file']())
    )

    use_sudo = ''
    if getattr(settings, 'SYNCPROD_SUDO', False):
        use_sudo = "sudo "

    for cmd in cmds:
        if s.has_key('user') and s['user']:
            cmd += ' -U ' + s['user']

        if s.has_key('host') and s['host']:
            cmd += ' -h ' + s['host']

        try:
            sts = subprocess.check_output(use_sudo + cmd, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            if not 'ERROR:  database "%s" does not exist' % s['dbname'] in e.output:
                return False, "'%s' returned %s" % (cmd, e.output)
            raise e

    return True, ""

#syncprod command
class Command(BaseCommand):
    help = 'Sync the latest production database'
    args = '[dbname override] [yyyy-MM-dd - optional date of db backup to restore]'

    def handle(self, *args, **options):

        skip_download = False
        #skip_download = True

        day = datetime.date.today()
        auto_seek = True
        settings_prefix = 'sync'

        if len(args) > 1:
            day = args[1]
            if isinstance(day, str):
                day = datetime.datetime.strptime(day, '%Y-%m-%d').date() #yyy-MM-dd
                auto_seek = False
                settings_prefix = 'sync_%s' % day

        s = get_backup_settings(settings_prefix, defaults={'TEMP_PATH': '/tmp'})

        if len(args) > 0:
            download_db_name = args[0]
        else:
            download_db_name = s['dbname']


        conn = S3Connection(s['AWS_ACCESS_KEY_ID'], s['AWS_SECRET_ACCESS_KEY'])
        bucket = conn.get_bucket(s['BACKUP_BUCKET_NAME'])

        while 1:
            prefix = add_path(s, format_key_filter(download_db_name, day))
            print("Searching for backup at %s" % prefix)
            keys = sorted(bucket.list(prefix), key=lambda k: k.last_modified)
            if len(keys) > 0:
                print("Found backup '%s'. Syncing..." % keys[-1])
                result, msg = do_sync(s, keys[-1], skip_download)
                if not result:
                    print(msg)
                    #Exit!
                    return
                else:
                    break

            else:
                if not auto_seek:
                    print('No match found for your date')
                    break
                print("No match found for %s." % day)
                day = day - datetime.timedelta(days=1)
                print("Attempting new match for %s." % day)
