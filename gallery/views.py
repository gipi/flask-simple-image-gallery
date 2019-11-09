from flask import Blueprint, render_template, request, current_app
import simplejson
from .models import Image


# Static files only work for blueprints registered with url_prefix
#  https://github.com/mitsuhiko/flask/issues/348
gallery = Blueprint('gallery', __name__, template_folder='templates', static_folder='static')


@gallery.route('/', methods=['GET', 'POST'])
def show_gallery():
    images = Image.all(current_app.config['GALLERY_ROOT_DIR'])
    return render_template('index.html', images=images)


@gallery.route('/json')
def json():
    """Return a JSON containing an array of URL pointing to
    the images.
    """
    images = Image.all(current_app.config['GALLERY_ROOT_DIR'])
    start = 0
    stop = len(images)

    try:
        if request.method == 'GET' and 'start' in request.args:
            start = int(request.args.get('start'))
        if request.method == 'GET' and 'stop' in request.args:
            stop = int(request.args.get('stop'))
    except ValueError:
        current_app.logger.debug(request)
        return ("start/stop parameters must be numeric", 400)

    images = images[start:stop]

    image_filenames = map(lambda x: x.filename, images)

    return simplejson.dumps(image_filenames)


@gallery.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST' and 'image' in request.files:
        image = request.files['image']
        Image('', post=image, root=current_app.config['GALLERY_ROOT_DIR'])

        return ("ok", 201,)

    return (simplejson.dumps({'error': 'you need to pass an image'}), 400)
