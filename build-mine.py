#!/usr/bin/python3

import argparse
import logging

import coloredlogs
import jprops

import interminepy.mine as imm
import interminepy.project as imp
import interminepy.utils as imu


# When changing this code, please make sure it conforms to Python PEP8 style guidelines.  JetBrains pycharm is one IDE
# that will show whether code is in compliance.

# MAIN
logger = logging.getLogger('build-mine.py')
coloredlogs.install(level='DEBUG')

parser = argparse.ArgumentParser('Build the mine')

parser.add_argument(
    'mine_properties_path', help="path to the mine's properties file, e.g. ~/.intermine/biotestmine.properties")

parser.add_argument(
    '-c', '--checkpoints-location',
    help='The location for reading/writing database checkpoints',
    default=imm.DATABASE_CHECKPOINT_LOCATION)

parser.add_argument(
    '--dry-run', action='store_true', default=False,
    help='Don''t actually build anything, just show the commands that would be executed')

args = parser.parse_args()
print(args)
if args.checkpoints_location is None:
    logger.info('No checkpoints location. Exiting')
    exit(0)

imu.check_path_exists(args.mine_properties_path)

if args.checkpoints_location != imm.DATABASE_CHECKPOINT_LOCATION:
    imu.check_path_exists(args.checkpoints_location)

imu.check_path_exists('project.xml')

options = {'dry-run': args.dry_run, 'run-in-shell': False}

with open('project.xml') as f:
    project = imp.Project(f)

for source_name in project.sources:
    logger.debug('Found source %s in project.xml', source_name)

with open(args.mine_properties_path) as f:
    mine_java_properties = jprops.load_properties(f)

db_configs = {}
for type_ in 'production', 'common-tgt-items', 'userprofile-production':
    db_configs[type_] = imm.get_db_config(mine_java_properties, type_)

imu.drop_db_if_exists(db_configs['production'], options)
imu.run_on_db(['createdb', '-E', 'UTF8', db_configs['production']['name']], db_configs['production'], options)

if args.checkpoints_location != imm.DATABASE_CHECKPOINT_LOCATION:
    last_checkpoint_location = imm.get_last_checkpoint_path(project, args.checkpoints_location)

    if last_checkpoint_location is not None:
        logger.info('Restoring from last found checkpoint %s', last_checkpoint_location)

        imu.run_on_db(
            ['pg_restore', '-1', '-d', db_configs['production']['name'], last_checkpoint_location],
            db_configs['production'], options)

        source_name = imm.split_checkpoint_path(last_checkpoint_location)[2]
        logger.info('Resuming after source %s', source_name)
        next_source_index = list(project.sources.keys()).index(source_name) + 1
    else:
        next_source_index = 0
else:
    # TODO: implement restore from db checkpoint
    next_source_index = 0

if next_source_index <= 0:
    logger.info('No previous checkpoint found, starting build from the beginning')
    imu.run(['./gradlew', 'buildDB', '--stacktrace', '--no-daemon'], options)
    imu.run(['./gradlew', 'buildUserDB', '--stacktrace', '--no-daemon'], options)
    imu.run(['./gradlew', 'loadDefaultTemplates', '--stacktrace', '--no-daemon'], options)

if next_source_index < len(project.sources):
    source_names = list(project.sources.keys())[next_source_index:]
    for source_name in source_names:
        # FIXME: We are having to do this for now because InterMine is not shutting down its connections properly
        imu.pg_terminate_backends(db_configs, options)
        imm.integrate_source(project.sources[source_name], db_configs['production'], args.checkpoints_location, options)

# FIXME: We are having to do this for now because InterMine is not shutting down its connections properly
imu.pg_terminate_backends(db_configs, options)
imu.run(['./gradlew', 'postprocess', '--no-daemon', '--stacktrace'], options)

logger.info('Finished. Now run "./gradlew tomcatStartWar"')
