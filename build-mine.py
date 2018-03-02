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
coloredlogs.install(level='DEBUG', fmt='%(asctime)s %(name)s %(levelname)s %(message)s')

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

parser.add_argument(
    '--fbt', '--force-backend-termination',
    help='If true, then we will periodically run the postgres function pg_terminate_backend() to try and clear out'
         ' old connections. This may help if InterMine is not properly closing its connections.',
    action='store_true', default=False)

args = parser.parse_args()
if args.checkpoints_location is None:
    logger.info('No checkpoints location. Exiting')
    exit(0)

imu.check_path_exists(args.mine_properties_path)

if args.checkpoints_location != imm.DATABASE_CHECKPOINT_LOCATION:
    imu.check_path_exists(args.checkpoints_location)
imu.check_path_exists('project.xml')

options = {'dry-run': args.dry_run, 'run-in-shell': False, 'force-backend-termination': args.fbt}

with open('project.xml') as f:
    project = imp.Project(f)

# for source_name in project.sources:
#     logger.debug('Found source %s in project.xml', source_name)

with open(args.mine_properties_path) as f:
    mine_java_properties = jprops.load_properties(f)

db_configs = {}
for type_ in 'production', 'common-tgt-items', 'userprofile-production':
    db_configs[type_] = imm.get_db_config(mine_java_properties, type_)

# The production database we want in SQL_ASCII for performance reasons
# See http://intermine.readthedocs.io/en/latest/system-requirements/software/postgres/postgres/#character-set-encoding
db_configs['production'].update({'template': 'template0', 'encoding': 'SQL_ASCII'})

imu.create_db_if_not_exists(db_configs['common-tgt-items'], options)
imu.create_db_if_not_exists(db_configs['userprofile-production'], options)

if args.checkpoints_location == imm.DATABASE_CHECKPOINT_LOCATION:
    next_source_index = imm.restore_cp_from_db(project, db_configs['production'], options)
else:
    next_source_index = imm.restore_cp_from_fs(project, args.checkpoints_location, db_configs['production'], options)

if next_source_index <= 0:
    logger.info('No previous checkpoint found, starting build from the beginning')
    imu.run(['./gradlew', 'buildDB', '--stacktrace', '--no-daemon'], options)
    imu.run(['./gradlew', 'buildUserDB', '--stacktrace', '--no-daemon'], options)
    imu.run(['./gradlew', 'loadDefaultTemplates', '--stacktrace', '--no-daemon'], options)

if next_source_index < len(project.sources):
    imm.integrate_sources_from_index(project, next_source_index, args.checkpoints_location, db_configs, options)

# FIXME: We are having to do this for now because InterMine is not shutting down its connections properly
imu.pg_terminate_backends(db_configs, options)
imu.run(['./gradlew', 'postprocess', '--no-daemon', '--stacktrace'], options)

logger.info('Finished. Now run "./gradlew tomcatStartWar"')
