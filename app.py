from flask import Flask
from extensions import db
from routes import init_routes
from werkzeug.utils import secure_filename
import os
from flask_login import LoginManager
from models import User

app = Flask(__name__)

# Add these configuration lines right after creating the Flask app
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# MySQL Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Adm1ralty21!@localhost/cars_and_bids'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key

# Initialize the database with the app
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

init_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
