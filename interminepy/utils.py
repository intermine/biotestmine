import logging
import os.path
import subprocess


logger = logging.getLogger('interminepy')


def does_db_exist(db_name, options):
    """
    Check if the database given in the config exists

    :param db_config:
    :param options:
    :return: true if it exists, false if not
    """
    # FIXME: There is a better way of doing this but need to make sure it works
    # SQL statement at https://stackoverflow.com/a/17757560/607179 instead of cutting up human command line output
    return run_return_rc(
        "psql -lqt | cut -d \| -f 1 | grep -qe '\s%s\s'" % db_name,
        {**options, **{'run-in-shell': True}}) == 0


def check_path_exists(path):
    if not os.path.exists(path):
        logger.error('Could not find %s. Exiting' % path)
        exit(1)


def create_db(db_config, options):
    run_on_db(['createdb', '-E', 'UTF8', db_config['name']], db_config, options)


def copy_db(source_db_name, dest_db_name, db_config, options):
    run_on_db(
        ['createdb', '-T', source_db_name, dest_db_name],
        db_config, options)


def drop_db_if_exists(db_config, options):
    if does_db_exist(db_config['name'], options):
        # FIXME: We are having to do this for now because InterMine is not shutting down its connections properly
        pg_terminate_backend(db_config, options)
        run_on_db(['dropdb', db_config['name']], db_config, options)


def restore_db(db_config, checkpoint_path, options):
    run_on_db(
        ['pg_restore', '-1', '-d', db_config['name'], checkpoint_path],
        db_config, options)


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
