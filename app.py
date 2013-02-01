# encoding:utf-8
from flask import Flask, request
from werkzeug.wsgi import SharedDataMiddleware
from socketio.server import SocketIOServer
from socketio import socketio_manage
from socketio.namespace import BaseNamespace

import tempfile
import hashlib
import shutil
import os
from gallery.views import gallery


ROOT_DIR = os.path.dirname(__file__)

UPLOAD_DIR = os.path.join(ROOT_DIR, 'uploads')
UPLOAD_ALLOWED_EXTENSIONS = (
    'jpg',
    'jpeg',
    'png',
    'gif',
)
app = Flask(__name__)
app.register_blueprint(gallery, url_prefix='/gallery')

class DefaultNamespace(BaseNamespace):
    def __init__(self, *args, **kwargs):
        super(DefaultNamespace, self).__init__(*args, **kwargs)

    def emit(self, event, args):
        self.socket.send_packet(dict(type="event", name=event,
            args=args, endpoint=self.ns_name))

    def on_start(self, data):
        app.logger.debug('on_start: %s' % data)
        # this actually is a path like C:\\blablabla\img.jpeg
        self.name = data['name']
        self.emit('stream', {})

    def on_upload(self, data):
        app.logger.debug('on_upload %s' % data)
        # check for file extension
        ext = self.name.split('.')[-1]
        if ext not in UPLOAD_ALLOWED_EXTENSIONS:
            self.emit('error', 'extension not allowed')
            return
        # client side must be readAsBinaryString and here we MUST decode it
        # choosing latin-1 otherwise UnicodeEncodeError appears.
        with tempfile.NamedTemporaryFile(mode='w+b') as f:
            # save into a temporary file and to the end rename it with the md5 of the contents
            app.logger.debug('save into file \'%s\'' % f.name)
            h = hashlib.md5()
            chunk = data['chunk']
            f.write(chunk.encode('latin-1'))
            h.update(chunk.encode('latin-1'))

            shutil.copy(f.name, os.path.join(UPLOAD_DIR, '%s.%s' % (h.hexdigest(), ext)))

@app.route("/socket.io/<path:path>")
def run_socketio(path):
    socketio_manage(request.environ, {'/default': DefaultNamespace})
    return ''

if __name__ == '__main__':
    app.debug = True
    app.logger.info('Listening on http://localhost:8080')
    server = SocketIOServer(
        ('0.0.0.0', 8080),
        SharedDataMiddleware(app, {}),
        namespace="socket.io",
        policy_server=False
    )
    server.serve_forever()
    app.run(debug=True)
