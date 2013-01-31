from flask import Flask
from socketio.server import SocketIOServer
from werkzeug.wsgi import SharedDataMiddleware
from gallery.views import gallery

app = Flask(__name__)
app.register_blueprint(gallery, url_prefix='/gallery')


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
