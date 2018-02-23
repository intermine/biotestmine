import os.path

import jprops

import interminepy.utils as imu


def get_db_config(props_path, db_type):
    config = {}

    with open(props_path) as f:
        props = jprops.load_properties(f)
        config['host'] = props['db.%s.datasource.serverName' % db_type]
        config['name'] = props['db.%s.datasource.databaseName' % db_type]
        config['user'] = props['db.%s.datasource.user' % db_type]
        config['pass'] = props['db.%s.datasource.password' % db_type]

    return config


def integrate_source(source, db_config, checkpoint_path, options=None):
    if options is None:
        options = {}

    imu.run(['./gradlew', 'integrate', '-Psource=%s' % source.name, '--no-daemon'], options)

    if source.dump:
        print('Checkpoint dumping at source %s', source.name)

        imu.run(
            ['pg_dump',
             '-Fc',
             '-U', db_config['user'],
             '-h', db_config['host'],
             '-f', os.path.join(checkpoint_path, 'integrate_%s.pgdump' % source.name)],
            options)
