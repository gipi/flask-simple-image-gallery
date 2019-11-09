from flask import Blueprint, render_template, request, current_app
from flask import jsonify
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

    image_filenames = list(map(lambda x: str(x.path), images))

    return jsonify(image_filenames)


@gallery.route('/upload', methods=['POST'])
def upload():
    current_app.logger.info(f'uploading')
    if request.method == 'POST' and 'image' in request.files:
        image = Image('', post=request.files['image'], root=current_app.config['GALLERY_ROOT_DIR'])

        if image.path.suffix in current_app.config['UPLOAD_ALLOWED_EXTENSIONS']:
            return ("ok", 201,)

        current_app.logger.info(f'failed to upload {image!r}')

    return (jsonify({'error': 'you need to pass an image'}), 400)
