import shutil
import unittest
from pathlib import Path
import tempfile
from io import BytesIO

from app import app


class GalleryTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        tmp = tempfile.mkdtemp()
        app.config['GALLERY_ROOT_DIR'] = tmp
        (Path(tmp) / "miao").touch()

    def tearDown(self):
        shutil.rmtree(app.config['GALLERY_ROOT_DIR'])

    def test_index(self):
        response = self.client.get('/')

        assert response.status_code == 302

    def test_json(self):
        response = self.client.get('/gallery/json')

        assert response.status_code == 200
        self.assertEqual(response.data, b'["miao"]\n')
        self.assertEqual(response.content_type, 'application/json')

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
                'image': (BytesIO(b'my file contents'), 'hello world.txt'),
            },
        )

        self.assertEqual(response.status_code, 400)

    def test_POST_upload_w_valid_image(self):
        '''Only certain type of files can be uploaded'''
        # https://gist.github.com/DazWorrall/1779861
        response = self.client.post(
            '/gallery/upload',
            data = {
                'image': (BytesIO(b'my file contents'), 'hello world.png'),
            },
        )

        self.assertEqual(response.status_code, 201)


if __name__ == '__main__':
    unittest.main()
