import logging
import os.path
import subprocess


logger = logging.getLogger('interminepy')


def check_path_exists(path):
    if not os.path.exists(path):
        logger.error('Could not find %s. Exiting' % path)
        exit(1)


def run(cmd, options):
    rc = run_return_rc(cmd, options)
    if rc != 0:
        logging.error('Command [%s] failed with rc %d' % (' '.join(cmd), rc))
        exit(1)


def run_return_rc(cmd, options):
    if isinstance(cmd, list):
        raw_cmd = ' '.join(cmd)
    else:
        raw_cmd = cmd

    logger.info('Running: %s', raw_cmd)

    if options['dry-run']:
        return

    return subprocess.call(cmd, shell=options['run-in-shell'])


def run_on_db(cmd, db_config, options):

    access_db_params = ['-U', db_config['user'], '-h', db_config['host']]

    run(cmd + access_db_params, options)
