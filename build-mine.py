#!/usr/bin/python3

import argparse
import coloredlogs
import logging

import interminepy.mine as imm
import interminepy.project as imp
import interminepy.utils as imu


# MAIN
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')

parser = argparse.ArgumentParser('Build the mine')

parser.add_argument(
    'mine_properties_path', help="path to the mine's properties file, e.g. ~/.intermine/biotestmine.properties")

parser.add_argument(
    'checkpoint_path',
    help='The directory in which to place database checkpoint dumps when the dump="true" flag is set in the <source>'
         ' entry of the project.xml')

parser.add_argument(
    '--dry-run', action='store_true', default=False,
    help='Don''t actually build anything, just show the commands that would be executed')

args = parser.parse_args()

imu.check_path_exists(args.mine_properties_path)
imu.check_path_exists(args.checkpoint_path)
imu.check_path_exists('project.xml')

options = {'dry-run': args.dry_run}

imu.run(['./gradlew', 'buildDB'], options)
imu.run(['./gradlew', 'buildUserDB'], options)
imu.run(['./gradlew', 'loadDefaultTemplates'], options)

with open('project.xml') as f:
    project = imp.Project(f)

db_config = imm.get_db_config(args.mine_properties_path, 'production')

for source in project.sources.values():
    imm.integrate_source(source, db_config, args.checkpoint_path, options)

imu.run(['./gradlew', 'postprocess', '--no-daemon'], options)

logger.info('Finished. Now run "./gradlew tomcatStartWar"')
