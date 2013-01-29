from flask import Blueprint, render_template
from .models import Image


gallery = Blueprint('gallery', __name__, template_folder='templates')


@gallery.route('/')
def show_gallery():
    images = Image.all()
    return render_template('index.html', images=images)
