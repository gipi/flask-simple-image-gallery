from flask import Blueprint, render_template, request, current_app, redirect, url_for
from flask.ext.login import login_user, logout_user
import simplejson
from .models import Image


# Static files only work for blueprints registered with url_prefix
#  https://github.com/mitsuhiko/flask/issues/348
gallery = Blueprint('gallery', __name__, template_folder='templates', static_folder='static')

@gallery.route('/', methods=['GET', 'POST',])
def show_gallery():
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            current_app.logger.debug('%s:%s' % (username, password))
            if username == 'test' and password == 'password':
                login_user(app.User.users(''))
    images = Image.all()
    return render_template('index.html', images=images)

@gallery.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('.show_gallery'))

@gallery.route('/json')
def json():
    """Return a JSON containing an array of URL pointing to
    the images.
    """
    images = Image.all()
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


@gallery.route('/upload', methods=['POST',])
def upload():
    if request.method == 'POST' and 'image' in request.files:
        image = request.files['image']
        Image('', image)

        return ("ok", 201,)

# FIXME: make more modular to avoid the import below
# this import is here to avoid circular hell import
import app
