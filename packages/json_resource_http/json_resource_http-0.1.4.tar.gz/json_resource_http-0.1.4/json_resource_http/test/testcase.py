import multiprocessing

from flask_json_resource.test import testcase

TestResource = testcase.TestResource


class TestCase(testcase.TestCase):
    port = 5080

    def setUp(self):
        self.app = self.api.test_client()
        self._run()

        super(TestCase, self).setUp()

    def tearDown(self):
        self._process.terminate()

        super(TestCase, self).tearDown()

    @property
    def server_url(self):
        return 'http://127.0.0.1:%s' % self.port

    def _run(self):
        def worker(api, port):
            api.run('127.0.0.1', port=port)

        self._process = multiprocessing.Process(
            target=worker, args=(self.api, self.port)
        )

        self._process.start()
