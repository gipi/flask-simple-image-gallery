# encoding:utf-8
from flask import Flask, request
from flask.ext.login import LoginManager, UserMixin, current_user
from flask.ext.bootstrap import Bootstrap
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

class User(UserMixin):
    def __init__(self, username):
        self.name = username
        self.id   = username

    @classmethod
    def users(cls, username):
        return User('pippo')

    def str(self):
        return '<User: %s>' % self.name

app = Flask(__name__)
app.register_blueprint(gallery, url_prefix='/gallery')
login_manager = LoginManager()
login_manager.setup_app(app)

Bootstrap(app)

@login_manager.user_loader
def load_user(userid):
    user = User.users(userid)
    return user

class DefaultNamespace(BaseNamespace):
    def __init__(self, *args, **kwargs):
        super(DefaultNamespace, self).__init__(*args, **kwargs)

    def emit(self, event, args):
        self.socket.send_packet(dict(type="event", name=event,
            args=args, endpoint=self.ns_name))

    def on_start(self, data):
        app.logger.debug('%s:on_start: %s' % (self.request['user'], data))
        # this actually is a path like C:\\blablabla\img.jpeg
        self.name = data['name']
        self.emit('stream', {})

    def on_upload(self, data):
        # upload the file content into a directory named as the user with
        # the name given by the md5 of its content
        if not self.request['user'].is_authenticated():
            app.logger.error('user not authenticated')
            self.emit('error: you are not authenticated')
            return

        app.logger.debug('%s:on_upload %s' % (self.request['user'], data))
        # check for file extension
        ext = self.name.split('.')[-1]
        if ext not in UPLOAD_ALLOWED_EXTENSIONS:
            self.emit('error', 'extension not allowed')
            return
        # client side must be readAsBinaryString and here we MUST decode it
        # choosing latin-1 otherwise UnicodeEncodeError appears.
        with tempfile.NamedTemporaryFile(mode='w+b') as f:
            app.logger.debug('save into file \'%s\'' % f.name)
            h = hashlib.md5()
            chunk = data['chunk']
            f.write(chunk.encode('latin-1'))
            h.update(chunk.encode('latin-1'))

            upload_user_dir = os.path.join(UPLOAD_DIR, self.request['user'].name)
            if not os.access(upload_user_dir):
                # FIXME: check for permission
                os.mkdir(upload_user_dir)

            uploaded_file_path = os.path.join(upload_user_dir, '%s.%s' % (h.hexdigest(), ext))

            shutil.copy(f.name,  uploaded_file_path)

@app.route("/socket.io/<path:path>")
def run_socketio(path):
    """from http://gevent-socketio.readthedocs.org/en/latest/main.html#socketio.socketio_manage
    
    The request object is not required, but will probably be
    useful to pass framework-specific things into your Socket and
    Namespace functions. It will simply be attached to the Socket
    and Namespace object (accessible through self.request in both
    cases), and it is not accessed in any case by the gevent-socketio library.
    """
    # pass as request the object contained in the proxied current_user so
    # to have possibility to check for authentication
    req = {
        'user':current_user._get_current_object(),
    }
    app.logger.info('user \'%s\' has connected' % req['user'])
    socketio_manage(request.environ, {'/default': DefaultNamespace}, request=req)
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
