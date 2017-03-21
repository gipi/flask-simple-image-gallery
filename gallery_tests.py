import shutil
import unittest
import tempfile
from StringIO import StringIO

from app import app


class GalleryTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        app.config['GALLERY_ROOT_DIR'] = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(app.config['GALLERY_ROOT_DIR'])

    def test_index(self):
        response = self.client.get('/')

        assert response.status_code == 302

    def test_json(self):
        response = self.client.get('/gallery/json')

        assert response.status_code == 200
        self.assertEqual(response.data, "miao")

    def test_GET_upload(self):
        response = self.client.get('/gallery/upload')

        self.assertEqual(response.status_code, 405)

    def test_POST_upload_wo_images(self):
        response = self.client.post('/gallery/upload')

        self.assertEqual(response.status_code, 400)

    def test_POST_upload_w_image_but_not_valid(self):
        '''Only certain type of files can be uploaded'''
        # https://gist.github.com/DazWorrall/1779861
        response = self.client.post(
            '/gallery/upload',
            data = {
                'image': (StringIO('my file contents'), 'hello world.txt'),
            },
        )

        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
