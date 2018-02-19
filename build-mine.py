#!/usr/bin/python3

import subprocess


def run(cmd):
    print('Running:', ' '.join(cmd))
    rc = subprocess.call(cmd)
    if rc != 0:
        print('Command [%s] failed with rc %d' % (' '.join(cmd), rc))
        exit(1)


def integrate_source(source_name):
    run(['./gradlew', 'integrate', '-Psource=%s' % source_name, '--no-daemon'])


sources = ['uniprot-malaria', 'malaria-gff', 'malaria-chromosome-fasta', 'go', 'go-annotation', 'update-publications', 'entrez-organism']

run(['./gradlew', 'buildDB'])
run(['./gradlew', 'buildUserDB'])
run(['./gradlew', 'loadDefaultTemplates'])

for source in sources:
    integrate_source(source)

run(['./gradlew', 'postprocess', '--no-daemon'])

print('Finished. Now run "./gradlew tomcatStartWar"')
