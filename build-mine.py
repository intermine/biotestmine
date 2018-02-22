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

db_config = imm.get_db_config(args.mine_properties_path, 'production')
user_db_config = imm.get_db_config(args.mine_properties_path, 'userprofile-production')

conn, curs = imu.connect_to_db(db_config)
user_conn, user_curs = imu.connect_to_db(user_db_config)


with open('project.xml') as f:
    project = imp.Project(f)

cmd = ['./gradlew', 'buildDB']
if not imm.is_builddb_run(curs):
    imu.run(cmd, options)
else:
    print("Skipping '%s' as already detected run" % ' '.join(cmd))

cmd = ['./gradlew', 'buildUserDB']
if not imm.is_builddb_run(user_curs):
    imu.run(cmd, options)
else:
    print("Skipping '%s' as already detected run" % ' '.join(cmd))

imu.run(['./gradlew', 'loadDefaultTemplates'], options)

for source in project.sources.values():
    imm.integrate_source(source, options)

imu.run(['./gradlew', 'postprocess', '--no-daemon'], options)

user_curs.close()
user_conn.close()
curs.close()
conn.close()

print('Finished. Now run "./gradlew tomcatStartWar"')
