from flask import Flask
from models import db, Patient  # Import your database and models

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    # Drop a specific table (e.g., Patient)
    Patient.__table__.drop(db.engine)
    User.__table__.drop(db.engine)
    print("Patient table dropped successfully!")

