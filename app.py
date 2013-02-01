# encoding:utf-8
from flask import Flask, request
from werkzeug.wsgi import SharedDataMiddleware
from socketio.server import SocketIOServer
from socketio import socketio_manage
from socketio.namespace import BaseNamespace
import codecs

from gallery.views import gallery


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
        self.emit('stream', {})

    def on_upload(self, data):
        app.logger.debug('on_upload %s' % data)
        # client side must be readAsBinaryString and here we MUST decode it
        # choosing latin-1 otherwise UnicodeEncodeError appears.
        with codecs.open('/tmp/upload', mode='w+b', encoding='latin-1') as f:
            f.write(data['chunk'])

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
