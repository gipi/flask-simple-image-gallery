from flask import Flask
from gallery.views import gallery

app = Flask(__name__)
app.register_blueprint(gallery)


if __name__ == '__main__':
    app.run(debug=True)
