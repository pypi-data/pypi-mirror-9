import amulet
import unittest


class TestDeployment(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.deployment = amulet.Deployment(series='trusty')

        cls.deployment.add('nagios')
        cls.deployment.add('haproxy')
        cls.deployment.add('rsyslog-forwarder')
        cls.deployment.relate('nagios:website', 'haproxy:reverseproxy')
        cls.deployment.relate('nagios:juju-info', 'rsyslog-forwarder:juju-info')

        try:
            cls.deployment.setup(timeout=900)
            cls.deployment.sentry.wait()
        except amulet.helpers.TimeoutError:
            amulet.raise_status(
                amulet.SKIP, msg="Environment wasn't stood up in time")
        except:
            raise

        cls.nagios = cls.deployment.sentry['nagios/0']
        cls.haproxy = cls.deployment.sentry['haproxy/0']
        cls.rsyslogfwd = cls.deployment.sentry['rsyslog-forwarder/0']
        cls.nagios.run(
            'mkdir -p /tmp/amulet-test/test-dir;'
            'echo contents > /tmp/amulet-test/test-file;'
        )
        cls.rsyslogfwd.run(
            'echo more-contents > /tmp/amulet-sub-test;'
        )

    def test_info(self):
        self.assertTrue('public-address' in self.nagios.info)
        self.assertEqual('nagios', self.nagios.info['service'])
        self.assertEqual('0', self.nagios.info['unit'])
        self.assertEqual('nagios/0', self.nagios.info['unit_name'])

    def test_file_stat(self):
        path = '/tmp/amulet-test/test-file'
        stat = self.nagios.file_stat(path)
        self.assertTrue(stat.pop('mtime'))
        self.assertEqual(
            stat, {
                'size': 9,
                'uid': 0,
                'gid': 0,
                'mode': '0100644',
            },
        )

    def test_file_contents(self):
        path = '/tmp/amulet-test/test-file'
        self.assertEqual(
            self.nagios.file_contents(path),
            'contents\n',
        )

    def test_subordinate_file_contents(self):
        path = '/tmp/amulet-sub-test'
        self.assertEqual(
            self.rsyslogfwd.file_contents(path),
            'more-contents\n',
        )

    def test_directory_stat(self):
        path = '/tmp/amulet-test'
        stat = self.nagios.directory_stat(path)
        self.assertTrue(stat.pop('mtime'))
        self.assertEqual(
            stat, {
                'size': 4096,
                'uid': 0,
                'gid': 0,
                'mode': '040755',
            },
        )

    def test_directory_listing(self):
        path = '/tmp/amulet-test'
        self.assertEqual(
            self.nagios.directory_listing(path), {
                'files': ['test-file'],
                'directories': ['test-dir'],
            },
        )

    def test_relation(self):
        nagios_info = self.nagios.relation(
            'website', 'haproxy:reverseproxy')
        for key in ['hostname', 'port', 'private-address']:
            self.assertTrue(key in nagios_info)

        haproxy_info = self.haproxy.relation(
            'reverseproxy', 'nagios:website')
        self.assertEqual(list(haproxy_info.keys()), ['private-address'])

    def test_run(self):
        self.assertEqual(
            self.nagios.run('echo hello'),
            ('hello', 0),
        )


if __name__ == '__main__':
    unittest.main()
