#!/usr/bin/python3

import argparse

import interminepy.mine as imm
import interminepy.project as imp
import interminepy.utils as imu


# MAIN
parser = argparse.ArgumentParser('Build the mine')
parser.add_argument(
    '--dry-run', action='store_true', default=False,
    help='Don''t actually build anything, just show the commands that would be executed')
args = parser.parse_args()

imu.check_path_exists('project.xml')
options = {'dry-run': args.dry_run}

imu.run(['./gradlew', 'buildDB'], options)
imu.run(['./gradlew', 'buildUserDB'], options)
imu.run(['./gradlew', 'loadDefaultTemplates'], options)

with open('project.xml') as f:
    project = imp.Project(f)

for source in project.sources.values():
    imm.integrate_source(source, options)

imu.run(['./gradlew', 'postprocess', '--no-daemon'], options)

print('Finished. Now run "./gradlew tomcatStartWar"')
