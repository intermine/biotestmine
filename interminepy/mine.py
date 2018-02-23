import os.path

import jprops
import logging

import interminepy.utils as imu


logger = logging.getLogger('interminepy')


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


def integrate_source(source, db_config, checkpoint_path, options):
    imu.run(['./gradlew', 'integrate', '-Psource=%s' % source.name, '--no-daemon'], options)

    if source.dump:
        logger.info('Checkpoint dumping at source %s', source.name)

        imu.run_on_db(
            ['pg_dump',
             '-Fc',
             '-f', make_checkpoint_path(checkpoint_path, source),
             db_config['name']],
            db_config,
            options)


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
