#!/usr/bin/python3

import argparse
import subprocess


# FUNCTIONS
def run(cmd, _options):
    print('Running:', ' '.join(cmd))

    if _options['dry-run']:
        return

    rc = subprocess.call(cmd)
    if rc != 0:
        print('Command [%s] failed with rc %d' % (' '.join(cmd), rc))
        exit(1)


def integrate_source(source_name, _options):
    run(['./gradlew', 'integrate', '-Psource=%s' % source_name, '--no-daemon'], _options)


# MAIN
parser = argparse.ArgumentParser('Build the mine')
parser.add_argument(
    '--dry-run', action='store_true', default=False,
    help='Don''t actually build anything, just show the commands that would be executed')
args = parser.parse_args()

options = {'dry-run': args.dry_run}

sources = ['uniprot-malaria', 'malaria-gff', 'malaria-chromosome-fasta', 'go', 'go-annotation', 'update-publications', 'entrez-organism']

run(['./gradlew', 'buildDB'], options)
run(['./gradlew', 'buildUserDB'], options)
run(['./gradlew', 'loadDefaultTemplates'], options)

for source in sources:
    integrate_source(source, options)

run(['./gradlew', 'postprocess', '--no-daemon'], options)

print('Finished. Now run "./gradlew tomcatStartWar"')
