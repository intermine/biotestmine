#!/usr/bin/python3

import argparse
import os.path
import subprocess

import jprops

import interminepy.project as imp


# FUNCTIONS
def check_path_exists(path):
    if not os.path.exists(path):
        print('Could not find %s. Exiting' % path)
        exit(1)


def run(cmd, _options):
    print('Running:', ' '.join(cmd))

    if _options['dry-run']:
        return

    rc = subprocess.call(cmd)
    if rc != 0:
        print('Command [%s] failed with rc %d' % (' '.join(cmd), rc))
        exit(1)


def integrate_source(_source, _options):
    run(['./gradlew', 'integrate', '-Psource=%s' % _source.name, '--no-daemon'], _options)


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

check_path_exists(args.mine_properties_path)
check_path_exists('project.xml')
options = {'dry-run': args.dry_run}

with open(args.mine_properties_path) as f:
    props = jprops.load_properties(f)

with open('project.xml') as f:
    project = imp.Project(f)

run(['./gradlew', 'buildDB'], options)
run(['./gradlew', 'buildUserDB'], options)
run(['./gradlew', 'loadDefaultTemplates'], options)

for source in project.sources.values():
    integrate_source(source, options)

run(['./gradlew', 'postprocess', '--no-daemon'], options)

print('Finished. Now run "./gradlew tomcatStartWar"')
