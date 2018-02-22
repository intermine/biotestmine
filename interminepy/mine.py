import interminepy.utils as imu


def integrate_source(_source, _options):
    imu.run(['./gradlew', 'integrate', '-Psource=%s' % _source.name, '--no-daemon'], _options)
