import os.path
import subprocess

import psycopg2


def check_path_exists(path):
    if not os.path.exists(path):
        print('Could not find %s. Exiting' % path)
        exit(1)


def connect_to_db(config):
    print('Connecting to database with host=%s, dbname=%s, user=%s, password=(hidden)'
          % (config['db-host'], config['db-name'], config['db-user']))

    conn = psycopg2.connect(
        host=config['db-host'], dbname=config['db-name'], user=config['db-user'], password=config['db-pass'])

    curs = conn.cursor()

    return conn, curs


def run(cmd, _options):
    print('Running:', ' '.join(cmd))

    if _options['dry-run']:
        return

    rc = subprocess.call(cmd)
    if rc != 0:
        print('Command [%s] failed with rc %d' % (' '.join(cmd), rc))
        exit(1)
