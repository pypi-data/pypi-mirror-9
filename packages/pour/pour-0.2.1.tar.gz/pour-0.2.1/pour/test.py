import unittest
import app


class TestCase(unittest.TestCase):

    def setUp(self):
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()

    def tearDown(self):
        pass

    def test_get_index(self):
        rv = self.app.get('/')
        assert 'Hello World' in rv.data

if __name__ == '__main__':
    unittest.main()
