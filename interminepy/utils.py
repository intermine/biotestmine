import logging
import os.path
import subprocess


logger = logging.getLogger('interminepy')


def check_path_exists(path):
    if not os.path.exists(path):
        logger.error('Could not find %s. Exiting' % path)
        exit(1)


def drop_db_if_exists(db_config, options):
    if run_return_rc(
            "psql -lqt | cut -d \| -f 1 | grep -qe '\s%s\s'" % db_config['name'],
            {**options, **{'run-in-shell': True}}) == 0:

        # FIXME: We are having to do this for now because InterMine is not shutting down its connections properly
        pg_terminate_backend(db_config, options)
        run_on_db(['dropdb', db_config['name']], db_config, options)


def run(cmd, options):
    rc = run_return_rc(cmd, options)
    if rc != 0:
        logger.error('Command [%s] failed with rc %d', ' '.join(cmd), rc)
        exit(1)


def run_return_rc(cmd, options):
    if isinstance(cmd, list):
        raw_cmd = ' '.join(cmd)
    else:
        raw_cmd = cmd

    logger.info('Running: %s', raw_cmd)

    if options['dry-run']:
        return 0

    return subprocess.call(cmd, shell=options['run-in-shell'])


def run_on_db(cmd, db_config, options):
    access_db_params = ['-U', db_config['user'], '-h', db_config['host']]
    run(cmd + access_db_params, options)


def pg_terminate_backends(db_configs, options):
    for db_config in db_configs.values():
        pg_terminate_backend(db_config, options)


def pg_terminate_backend(db_config, options):
    run_on_db(
        ['psql',
         '-P', 'pager=off',
         '-q',
         '-o', '/dev/null',
         '-c', 'SELECT pg_terminate_backend(pg_stat_activity.pid)'
               ' FROM pg_stat_activity '
               ' WHERE datname = current_database()'
               ' AND pid <> pg_backend_pid();', db_config['name']], db_config, options)
