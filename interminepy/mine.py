import interminepy.utils as imu


def is_builddb_run(curs):
    curs.execute("SELECT 'intermineobject'::regclass")
    return curs.rowcount != 0


def integrate_source(_source, _options):
    imu.run(['./gradlew', 'integrate', '-Psource=%s' % _source.name, '--no-daemon'], _options)
