import unittest

from app import app


class GalleryTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_index(self):
        response = self.client.get('/')

        assert response.status_code == 302


if __name__ == '__main__':
    unittest.main()
