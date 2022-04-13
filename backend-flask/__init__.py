from flask import Flask, url_for
from flask_cors import CORS


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    CORS(app)

    from . import graph, auth
    app.register_blueprint(graph.bp)
    app.register_blueprint(auth.bp)

    @app.route('/')
    def root():
        return 'Hello!'

    return app


if __name__ == '__main__':
    create_app().run()
