from flask import Flask
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

csrf = CSRFProtect()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
csrf.init_app(app)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)

from Scholarly.routes.general_routes import general_bp
from Scholarly.routes.auth_routes import auth_bp
from Scholarly.routes.notes_routes import notes_bp
from Scholarly.routes.quiz_routes import quiz_bp
from Scholarly.routes.learn_routes import learn_bp

app.register_blueprint(general_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(notes_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(learn_bp)