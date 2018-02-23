import logging
import os.path
import subprocess


logger = logging.getLogger('interminepy')


def check_path_exists(path):
    if not os.path.exists(path):
        logger.error('Could not find %s. Exiting' % path)
        exit(1)


def run(cmd, options={}):
    logger.info('Running: %s', ' '.join(cmd))

    if options['dry-run']:
        return

    rc = subprocess.call(cmd)
    if rc != 0:
        logging.error('Command [%s] failed with rc %d' % (' '.join(cmd), rc))
        exit(1)
