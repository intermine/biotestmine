import os.path

import jprops
import logging

import interminepy.utils as imu


logger = logging.getLogger('interminepy')

DATABASE_CHECKPOINT_LOCATION_CONST = ':database:'


def get_db_config(props_path, db_type):
    config = {}

    with open(props_path) as f:
        props = jprops.load_properties(f)
        config['host'] = props['db.%s.datasource.serverName' % db_type]
        config['name'] = props['db.%s.datasource.databaseName' % db_type]
        config['user'] = props['db.%s.datasource.user' % db_type]
        config['pass'] = props['db.%s.datasource.password' % db_type]

    return config


def get_last_checkpoint_path(project, checkpoint_path):
    last_checkpoint_path = None
    for source in project.sources.values():
        path = os.path.join(checkpoint_path, make_checkpoint_filename(source))
        if os.path.isfile(path):
            last_checkpoint_path = path

    return last_checkpoint_path


def integrate_source(source, db_config, checkpoint_location, options):
    # FIXME: We are having to do this for now because InterMine is not shutting down its connections properly
    imu.run_on_db(['psql', '-P', 'pager=off', '-q', '-c', 'SELECT pg_terminate_backend(pg_stat_activity.pid)'
                                                          ' FROM pg_stat_activity '
                                                          ' WHERE datname = current_database()'
                                                          ' AND pid <> pg_backend_pid();', db_config['name']],
                  db_config, options)

    imu.run(['./gradlew', 'integrate', '-Psource=%s' % source.name, '--stacktrace', '--no-daemon'], options)

    if source.dump:
        logger.info('Checkpoint dumping at source %s', source.name)

        if checkpoint_location == DATABASE_CHECKPOINT_LOCATION_CONST:
            # FIXME: We are having to do this for now because InterMine is not shutting down its connections properly
            imu.run_on_db(['psql', '-P', 'pager=off', '-q', '-c', 'SELECT pg_terminate_backend(pg_stat_activity.pid)'
                                                                  ' FROM pg_stat_activity '
                                                                  ' WHERE datname = current_database()'
                                                                  ' AND pid <> pg_backend_pid();', db_config['name']], db_config, options)

            imu.run_on_db(
                ['createdb', '-T', db_config['name'], make_checkpoint_db_name(db_config, source)],
                db_config, options)
        else:
            imu.run_on_db(
                ['pg_dump',
                    '-Fc',
                    '-f', make_checkpoint_path(checkpoint_location, source),
                    db_config['name']],
                db_config,
                options)


def make_checkpoint_db_name(db_config, source):
    return '%s:%s' % (db_config['name'], source.name)


def make_checkpoint_path(checkpoint_path, source):
    return os.path.join(checkpoint_path, make_checkpoint_filename(source))


def make_checkpoint_filename(source):
    return 'integrate_%s.pgdump' % source.name


def split_checkpoint_path(path):
    """
    Splits a checkpoint path into components (dir, action, source.name, extension)
    e.g. ('dumpdir', 'integrate', 'go-annotation', 'pgdump')

    :param path:
    :return:
    """

    return [os.path.dirname(path)] + split_checkpoint_filename(os.path.basename(path))


def split_checkpoint_filename(name):
    """
    Splits a checkpoint filename into components (action, source.name, extension)
    e.g. ('integrate', 'go-annotation', 'pgdump')

    :param name:
    :return:
    """

    parts = name.split('_', 1)
    return [parts[0]] + parts[1].rsplit('.')
