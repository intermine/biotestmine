import os.path
import subprocess


def check_path_exists(path):
    if not os.path.exists(path):
        print('Could not find %s. Exiting' % path)
        exit(1)


def run(cmd, options={}):
    print('Running:', ' '.join(cmd))

    if options['dry-run']:
        return

    rc = subprocess.call(cmd)
    if rc != 0:
        print('Command [%s] failed with rc %d' % (' '.join(cmd), rc))
        exit(1)
