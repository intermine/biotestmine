#!/usr/bin/python3

import argparse
import os.path

import jprops

import interminepy.project as imp
import interminepy.utils as imu


def integrate_source(_source, _options):
    imu.run(['./gradlew', 'integrate', '-Psource=%s' % _source.name, '--no-daemon'], _options)


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
    db_server_name = props['db.production.datasource.serverName']
    db_name = props['db.production.datasource.databaseName']
    db_user = props['db.production.datasource.user']
    db_pass = props['db.production.datasource.password']

with open('project.xml') as f:
    project = imp.Project(f)

imu.run(['./gradlew', 'buildDB'], options)
imu.run(['./gradlew', 'buildUserDB'], options)
imu.run(['./gradlew', 'loadDefaultTemplates'], options)

for source in project.sources.values():
    integrate_source(source, options)

imu.run(['./gradlew', 'postprocess', '--no-daemon'], options)

print('Finished. Now run "./gradlew tomcatStartWar"')
