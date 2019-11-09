# encoding:utf-8
import os

from flask import Flask, redirect, url_for
from gallery.views import gallery
import settings

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


ROOT_DIR = os.path.dirname(__file__)

UPLOAD_DIR = os.path.join(ROOT_DIR, 'uploads')


app = Flask(__name__)
app.register_blueprint(gallery, url_prefix='/gallery')
app.config['GALLERY_ROOT_DIR'] = settings.GALLERY_ROOT_DIR
app.config['UPLOAD_ALLOWED_EXTENSIONS'] = settings.UPLOAD_ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return redirect(url_for('gallery.show_gallery'))


if __name__ == '__main__':
    app.logger.info('Listening on http://localhost:8000')
    app.run(port=8000, debug=True)
