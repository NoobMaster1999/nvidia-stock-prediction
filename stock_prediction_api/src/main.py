import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, redirect
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.prediction import prediction_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(prediction_bp, url_prefix='/api')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/')
def serve_frontend():
    # In development, redirect to Vite dev server
    return redirect('http://localhost:5000')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)