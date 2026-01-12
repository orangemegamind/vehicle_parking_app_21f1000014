from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, timezone
from sqlalchemy import DateTime, or_, and_

app = Flask(__name__)

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=3)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///car_parking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    email_id = db.Column(db.String, unique = True, nullable=False)
    first_name = db.Column(db.String,nullable=False)
    last_name = db.Column(db.String,nullable=False)
    username = db.Column(db.String,nullable=False,unique=True)
    address = db.Column(db.String,nullable=False)
    pincode = db.Column(db.Integer,nullable=False)
    password = db.Column(db.String,nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    role = db.Column(db.String,default='user')
    Reserve_Parking_Spot = db.relationship('Reserve_Parking_Spot',backref="User")

class Parking_lot(db.Model):
    __tablename__ = "Parking_Lot"
    lot_id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    loc_name = db.Column(db.String,nullable=False)
    price = db.Column(db.Integer,nullable=False)
    lot_address = db.Column(db.String,nullable=False)
    lot_pincode = db.Column(db.String,nullable=False)
    no_of_spots = db.Column(db.String,nullable=False)
    admin_created = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    Parking_Spot = db.relationship('Parking_Spot',backref="Parking_lot")
    Reserve_Parking_Spot = db.relationship('Reserve_Parking_Spot',backref='Parking_lot')

class Parking_Spot(db.Model): 
    __tablename__ = "Parking_Spot"
    spot_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    lot_id = db.Column(db.Integer,db.ForeignKey(Parking_lot.lot_id),nullable=False)
    is_aval = db.Column(db.Boolean,nullable=False,default=True)
    Reserve_Parking_Spot = db.relationship('Reserve_Parking_Spot',backref="Parking_Spot")
    
class Reserve_Parking_Spot(db.Model):
    __tablename__ = "Reserve_Parking_Spot"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    spot_id = db.Column(db.Integer,db.ForeignKey("Parking_Spot.spot_id"),nullable=False)
    lot_id = db.Column(db.Integer,db.ForeignKey("Parking_Lot.lot_id"),nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey(User.id),nullable=False)
    vehicle_no = db.Column(db.String,nullable=False,unique=True)
    parking_time = db.Column(db.String,nullable=False)
    leaving_time = db.Column(db.String,nullable=True)
    parking_cost = db.Column(db.Integer,nullable=False)
    status = db.Column(db.Boolean,nullable=False)

with app.app_context():
    db.create_all()

    if User.query.filter_by(username='admin').first() is None:
        admin_pass = generate_password_hash('admin@password')
        admin = User(username='admin',email_id='rishabhmaurya02@gmail.com',password = admin_pass,first_name='admin', last_name='user',address='Admin Street',pincode='000000', role='admin')

        db.session.add(admin)
        db.session.commit()
    else:
        print("Admin already exists!")
