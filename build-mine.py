#!/usr/bin/python3

import argparse
import os.path

import jprops
import psycopg2

import interminepy.mine as imm
import interminepy.project as imp
import interminepy.utils as imu


# MAIN
parser = argparse.ArgumentParser('Build the mine')
parser.add_argument(
    'mine_properties_path', help="path to the mine's properties file, e.g. ~/.intermine/biotestmine.properties")
parser.add_argument(
    '--dry-run', action='store_true', default=False,
    help='Don''t actually build anything, just show the commands that would be executed')
args = parser.parse_args()

if not os.path.exists(args.mine_properties_path):
    print('Could not find %s. Exiting' % args.mine_properties_path)
    exit(1)

imu.check_path_exists(args.mine_properties_path)
imu.check_path_exists('project.xml')
options = {'dry-run': args.dry_run}

with open(args.mine_properties_path) as f:
    props = jprops.load_properties(f)
    db_host = props['db.production.datasource.serverName']
    db_name = props['db.production.datasource.databaseName']
    db_user = props['db.production.datasource.user']
    db_pass = props['db.production.datasource.password']

print('Connecting to database with host=%s, dbname=%s, user=%s, password=(hidden)' % (db_host, db_name, db_user))

conn = psycopg2.connect(host=db_host, dbname=db_name, user=db_user, password=db_pass)
curs = conn.cursor()

with open('project.xml') as f:
    project = imp.Project(f)

cmd = ['./gradlew', 'buildDB']
if not imm.is_builddb_run(curs):
    imu.run(cmd, options)
else:
    print("Skipping '%s' as already detected run" % ' '.join(cmd))

imu.run(['./gradlew', 'buildUserDB'], options)
imu.run(['./gradlew', 'loadDefaultTemplates'], options)

for source in project.sources.values():
    imm.integrate_source(source, options)

imu.run(['./gradlew', 'postprocess', '--no-daemon'], options)

curs.close()
conn.close()

print('Finished. Now run "./gradlew tomcatStartWar"')
