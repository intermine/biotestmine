import jprops

import interminepy.utils as imu


def is_builddb_run(curs):
    curs.execute("SELECT 'intermine_metadata'::regclass")
    return curs.rowcount != 0


def get_db_config(props_path, db_type):
    config = {}

    with open(props_path) as f:
        props = jprops.load_properties(f)
        config['db-host'] = props['db.%s.datasource.serverName' % db_type]
        config['db-name'] = props['db.%s.datasource.databaseName' % db_type]
        config['db-user'] = props['db.%s.datasource.user' % db_type]
        config['db-pass'] = props['db.%s.datasource.password' % db_type]

    return config


def integrate_source(_source, _options):
    imu.run(['./gradlew', 'integrate', '-Psource=%s' % _source.name, '--no-daemon'], _options)
