"""Flask App"""
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_pyfile('config.py', silent=True)
    CORS(app)
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)
    return app

app = create_app()
if __name__ == '__main__': app.run(debug=True)
