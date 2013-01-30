from flask import Blueprint, render_template, request, abort
import simplejson
from .models import Image


# Static files only work for blueprints registered with url_prefix
#  https://github.com/mitsuhiko/flask/issues/348
gallery = Blueprint('gallery', __name__, template_folder='templates', static_folder='static')


@gallery.route('/')
def show_gallery():
    images = Image.all()
    return render_template('index.html', images=images)

@gallery.route('/json')
def json():
    """Return a JSON containing an array of URL pointing to
    the images.
    """
    images = Image.all()
    if request.method == 'GET' and 'start' in request.args:
        images = images[int(request.args('start')):]
    if request.method == 'GET' and 'stop' in request.args:
        images = images[int(request.args.get('stop')):]

    image_filenames = map(lambda x: x.filename, images)

    return simplejson.dumps(image_filenames)


@gallery.route('/upload', methods=['POST',])
def upload():
    if request.method == 'POST' and 'image' in request.files:
        image = request.files['image']
        Image('', image)

        return ("ok", 201,)

