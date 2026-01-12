from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, make_response, Response
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt, get_jwt_identity, unset_jwt_cookies
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from backend.models import db,User,Parking_lot, Parking_Spot,Reserve_Parking_Spot,or_, and_
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from sqlalchemy.exc import IntegrityError
from celery import Celery
import smtplib
import redis
import os 
import csv
from io import StringIO
from jinja2 import Template
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#region Config for backend jobs
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "rishabhmaurya02@gmail.com"
REDIS_BROKER = "redis://localhost:6380/0"
REDIS_BACKEND = "redis://localhost:6380/0"
EMAIL_PASS = "wvtp gyoh ovhe ldbi"

#endregion

now = datetime.now()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # backend folder
INSTANCE_FOLDER = os.path.join(BASE_DIR, "instance")

print("BASE_DIR:", BASE_DIR)
print("Instance folder:", INSTANCE_FOLDER)

app = Flask(__name__, instance_path=INSTANCE_FOLDER)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(INSTANCE_FOLDER, 'car_parking.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'PARKING'


db.init_app(app)

CORS(app,origins='*')
jwt = JWTManager(app)
api = Api(app)
celery = Celery('parking_app', broker=REDIS_BROKER, backend=REDIS_BACKEND)
#API's

from celery.schedules import crontab
celery.conf.beat_schedule = {
    'daily-mail': {
        'task': 'backend.app.send_daily_reminder',
        'schedule': crontab(minute=30, hour=19), 
    },
    'monthly-report': {
        'task': 'backend.app.send_monthly_report',
        'schedule': crontab(minute=0, hour=0, day_of_month=1),  # 1st day of month
    },
}

celery.conf.timezone = 'Asia/Kolkata'

# region User
#data = ['username':'admin','password':'adminpass','role':'admin']

class SignupResource(Resource):
    def post(self):
        
        parser = reqparse.RequestParser()
        parser.add_argument('full_name',type=str,required=True)
        parser.add_argument('username',type=str,required=True)
        parser.add_argument('email_id',type=str,required=True)
        parser.add_argument('pincode',type=int,required=True)
        parser.add_argument('address',type=str,required=True)
        parser.add_argument('password',type=str)
        parser.add_argument('role',type=str,default='user')

        args = parser.parse_args() 
        
        fullname = args['full_name']
        lastspace = fullname.rfind(" ")
        if(lastspace==-1):
            first_name = fullname
            last_name = ""
        else:                
            first_name = fullname[:lastspace]
            last_name = fullname[lastspace+1:]

        hashed_password = generate_password_hash(args['password'])
        new_user = User(first_name=first_name, last_name=last_name, username=args['username'],
                            pincode=args['pincode'], address=args['address'], email_id=args['email_id'],
                            password = hashed_password,role=args['role'])

        try:
            db.session.add(new_user)
            db.session.commit()
            return {"message": "User Created Successfully"}, 200

        except IntegrityError as e:
            db.session.rollback()

            if 'username' in str(e.orig):
                return {"message": "Username already exists"}, 409
            elif 'email_id' in str(e.orig):
                return {"message": "Email ID already exists"}, 409
            else:
                return {"message": "A unique field conflict occurred"}, 409

        except Exception as e:
            db.session.rollback()
            return {"message": "Unexpected signup error", "error": str(e)}, 500
    
class UserInfo_Resource(Resource):
    @jwt_required()
    def get(self):

        if(get_jwt().get("role")=="admin"):
            users = User.query.all()

            user_info = [{
                "id":user.id,
                "email_id":user.email_id,
                "full_name":user.first_name + user.last_name,
                "address":user.address,
                "pincode":user.pincode
            }for user in users]

            return user_info,200 
        else:
            return {"message":"Users don't have access!"}, 404

class UserParkingSpots(Resource):
    @jwt_required()
    def get(self):
        if(get_jwt().get("role")=="user"):
            user_id = get_jwt_identity()
            user_spots = Reserve_Parking_Spot.query.filter(Reserve_Parking_Spot.user_id == user_id).all()
            if user_spots:
                user_spot_info = [{
                    "spot_id": spot.spot_id,
                    "lot_id": spot.lot_id,
                    "vehicle_no": spot.vehicle_no,
                    "parking_time": str(spot.parking_time),
                    "leaving_time": str(spot.leaving_time) if spot.leaving_time else None,
                    "parking_cost": spot.parking_cost  
                }for spot in user_spots]

                return user_spot_info,200
            return {"message":"Looks like you haven't booked any parking spots yet."}, 200
        else:
            return {"message":"Admins don't have access!"}, 404
    
class sign_In_resource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username',type=str,required=True)
        parser.add_argument('password',type=str,required=True)
        args = parser.parse_args()

        user = User.query.filter_by(username=args["username"]).first()

        if user and check_password_hash(user.password,args['password']):
            access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role}) # Token create a session for a particular time in this case 24 hrs (expires_delta=24)
            user.last_login = datetime.now()
            db.session.commit()
            user_info={
                "id" : user.id,
                "username" : user.username,
                "role" : user.role
            }

            return {'access_token':access_token,'user':user_info}, 200
        else:
            return {'message':'Invalid Username or Password'}, 401

class logout_resource(Resource):
    @jwt_required()
    def post(self):
        identity = get_jwt()
        role = identity["role"]
        resp = make_response(jsonify({"message": "User Logged Out Successfully!"}),200)
        unset_jwt_cookies(resp)

        return resp
# endregion    

# region Parking Lot 
class ParkingLot_Info(Resource):
   @jwt_required()
   def get(self):
        if(get_jwt().get("role")=="admin"):

            spots_data = defaultdict(lambda:{"available":[],"occupied":[]})
            spots = Parking_Spot.query.all()
            for spot in spots:                                     # No lots have same spot id
                if spot.is_aval:
                    status = "available"
                else:
                    status = "occupied"
                spots_data[spot.lot_id][status].append(spot.spot_id)  # here key is lot id and inside it there are 2 keys available and occupied with spot id element lists
        

            if(spots_data):
                spots_info = [{
                    "lot_id" : lot_id,
                    "Available": data["available"],
                    "Occupied": data["occupied"],
                    "Total" : len(data["available"]) + len(data["occupied"])    
                }for lot_id,data in spots_data.items()]

                return spots_info,200
            else:
                return {"message" : "Sorry, no available parking spots at the moment."}, 200
        else:
            return {"message":"Users don't have access!"}, 404

class ParkingLot(Resource):
    @jwt_required()
    def get(self):
        if(get_jwt().get("role")=="admin"):
        
            parser = reqparse.RequestParser()
            parser.add_argument("lot_id",type=int,required=True,location="args")
            args = parser.parse_args()
            print(args["lot_id"])
            lot = Parking_lot.query.filter_by(lot_id=args["lot_id"]).first()

            if(lot):
                return {
                    "lot_id": lot.lot_id,
                    "loc_name": lot.loc_name,
                    "price": lot.price,
                    "lot_address": lot.lot_address,
                    "lot_pincode": lot.lot_pincode,
                    "no_of_spots":lot.no_of_spots
                }, 200
            else:
                return {"message" : "Parking Lot Not Found."},404
        else:
            return {"message":"Users don't have access!"}, 404
       

    @jwt_required()
    def post(self):
        if(get_jwt().get("role")=="admin"):
            parser = reqparse.RequestParser()
            parser.add_argument("loc_name",type=str,required=True)
            parser.add_argument("price",type=int,required=True)
            parser.add_argument("lot_address",type=str,required=True)
            parser.add_argument("lot_pincode",type=int,required=True)
            parser.add_argument("no_of_spots",type=int,required=True)
            args = parser.parse_args()

            parkingLot = Parking_lot(loc_name=args["loc_name"],price=args["price"],
                    lot_address=args['lot_address'],lot_pincode=args["lot_pincode"],no_of_spots=args["no_of_spots"],admin_created=True)

            db.session.add(parkingLot)
            db.session.commit()

            for i in range(args["no_of_spots"]):
                parkingSpot = Parking_Spot(lot_id = parkingLot.lot_id, is_aval = True)
                db.session.add(parkingSpot)
                db.session.commit()

            return {"message":"Parking Lot created Successfully !"},201

        else:
            return {"message":"Users don't have access!"}, 404
        
    @jwt_required()
    def put(self):
        if(get_jwt().get("role")=="admin"):
            parser = reqparse.RequestParser()
            parser.add_argument("lot_id",type=int,required=True)
            parser.add_argument("loc_name",type=str,required=True)
            parser.add_argument("price",type=int,required=True)
            parser.add_argument("lot_address",type=str,required=True)
            parser.add_argument("lot_pincode",type=int,required=True)
            parser.add_argument("no_of_spots",type=int,required=True)
            args = parser.parse_args()

            lot = Parking_lot.query.filter_by(lot_id = args["lot_id"]).first()

            if(lot):
                lot.loc_name = args["loc_name"]
                lot.price = args["price"]
                lot.lot_address = args["lot_address"]
                lot.lot_pincode = args["lot_pincode"]
                db.session.commit()
                occupied_spots = Parking_Spot.query.filter(Parking_Spot.lot_id==args["lot_id"],Parking_Spot.is_aval==False).count()
                
                if (args["no_of_spots"] >= occupied_spots):                    # More than Occupied Spots
                    lot.no_of_spots = args["no_of_spots"]

                    all_spots = Parking_Spot.query.filter(Parking_Spot.lot_id==args["lot_id"]).count()
                    if(args["no_of_spots"] >= all_spots):                     # More than earlier
                        spot_count = args["no_of_spots"] - all_spots
                        count_init = all_spots
                        for i in range(spot_count):
                            count_init += 1
                            new_spot = Parking_Spot(lot_id = args["lot_id"], is_aval = True)
                            db.session.add(new_spot)
                            db.session.commit()
                    
                    else:                                                     # Less than earlier
                        spot_count = all_spots - args["no_of_spots"]         
                        count_init = all_spots 
                        del_count = 0
                        while del_count < spot_count:
                            
                            curr_spot = Parking_Spot.query.filter_by(lot_id = args["lot_id"], is_aval = True).first()
                            if(curr_spot):
                                db.session.delete(curr_spot)
                                db.session.commit()
                                del_count += 1
                            count_init -= 1

                    
                    return {"message":"Data Updated Successfully !"}, 202
                else:                                                          # Less than Occupied Spots
                    return {"message": f"{args['no_of_spots']} spots are occupied."}, 200
                
            else:
                return {"message":"Parking Lot does not exist"}, 404
        else:
            return {"message":"Access Denied!"}, 404
        
    @jwt_required()
    def delete(self):
        if(get_jwt().get("role")=="admin"):
            parser = reqparse.RequestParser()
            parser.add_argument("lot_id",type=int,required=True)
            args = parser.parse_args()

            lot = Parking_lot.query.filter_by(lot_id=args["lot_id"]).first()
            print(lot)
            if(lot):
                occupied_spots = Parking_Spot.query.filter(and_(Parking_Spot.is_aval==False,Parking_Spot.lot_id==args["lot_id"])).count()
                print(occupied_spots)
                if(occupied_spots):
                    return {"message": f"Cannot Delete. {occupied_spots} spots are occupied."}, 200
                

                all_spots = Parking_Spot.query.filter(Parking_Spot.lot_id==args["lot_id"]).all()

                spot_ids = [spot.spot_id for spot in all_spots]
                if spot_ids:
                    reservations = Reserve_Parking_Spot.query.filter(Reserve_Parking_Spot.spot_id.in_(spot_ids)).all()
                    for res in reservations:
                        db.session.delete(res)

                for i in all_spots:
                    db.session.delete(i)

                print("??")
                db.session.delete(lot)
                db.session.commit()
                print("ok")
                return {"message":"Parking Lot deleted successfully"}, 200
            else:
                return {"message":"Parking Lot does not exist !"}, 404
        else:
            return {"message":"access Denied !"}, 404
    
# endregion

# region Parking Spot

class ParkingSpot(Resource):
    @jwt_required()
    def get(self):
        if(get_jwt().get("role")=="admin"):
            parser = reqparse.RequestParser()
            parser.add_argument("spot_id",type=int,required=True,location="args")
            args = parser.parse_args()
        
            spot = Parking_Spot.query.filter_by(spot_id=args["spot_id"]).first()

            if(spot):
                ParkingSpot={
                    "lot_id": spot.lot_id,
                    "spot_id": spot.spot_id,
                    "is_aval": spot.is_aval
                }
                return ParkingSpot, 200
            else:
                return {"message" : "Parking Spot Not Found"}, 404
        else:
            return {"message":"access Denied !"}, 404
    
    @jwt_required()
    def delete(self):
        if(get_jwt().get("role")=="admin"):
            parser = reqparse.RequestParser()
            parser.add_argument("spot_id",type=int,required=True)
            args = parser.parse_args()

            spot = Parking_Spot.query.filter_by(spot_id=args["spot_id"]).first()

            if(spot):
                if(spot.is_aval == True):                     # means not occupied, the spot is available
                    db.session.delete(spot)
                    db.session.commit()
                    return {"message":"Spot Deleted Successfully"}
                else:
                    return {"message":"Spot is Occupied, can't be deleted!"}
        else:
            return {"message":"access Denied !"}, 404
            
class AvailableSpot(Resource):
    @jwt_required()
    def get(self):
        if(get_jwt().get("role")=="user"):
            lot_aval_id={}
            lot_aval_add = {}
            lots = [lot.lot_id for lot in Parking_lot.query.all()]
            for i in lots: 
                aval_lot = Parking_lot.query.filter_by(lot_id=i).first().lot_address
                aval_spots = Parking_Spot.query.filter_by(lot_id=i,is_aval=True).count()
                lot_aval_id[i] = aval_spots
                lot_aval_add[i] = aval_lot

            if(lot_aval_id):
                aval_spots_info = [{
                    "lot_id" : i,
                    "lot_address" : lot_aval_add[i],
                    "lot_no_of_spots" : lot_aval_id[i]
                }for i in lots]

                return aval_spots_info,200
            else:
                return {"message" : "No parking spots available"}, 200
        else:
            return {"message":"access Denied !"}, 404
        
# endregion

# region Reserve Parking Spot
class ReserveParkingSpotAdmin(Resource):
    @jwt_required()
    def get(self):
        if(get_jwt().get("role")=="admin"):
            parser = reqparse.RequestParser()
            parser.add_argument("lot_id",type=int,required=True,location="args")
            parser.add_argument("spot_id",type=int,required=True,location="args")
            args = parser.parse_args()
        
            reserve_spot = Reserve_Parking_Spot.query.filter(Reserve_Parking_Spot.spot_id == args["spot_id"],
                                                            Reserve_Parking_Spot.lot_id == args["lot_id"],
                                                            Reserve_Parking_Spot.status == True).first()
            
            # Spot Price Calculation
            park_time = datetime.strptime(reserve_spot.parking_time, "%Y-%m-%d %H:%M:%S")
            Lot_Price = Parking_lot.query.filter(Parking_lot.lot_id==args["lot_id"]).first().price
            duration = (datetime.strptime(now.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S") - 
                        park_time).total_seconds()
            User_Parking_Cost = (duration/60)*Lot_Price
            reserve_spot.parking_cost = User_Parking_Cost

            if(reserve_spot):
                Spot = {
                    "spot_id": reserve_spot.spot_id,
                    "user_id": reserve_spot.user_id,
                    "vehicle_no": reserve_spot.vehicle_no,
                    "parking_time": reserve_spot.parking_time,
                    "parking_cost": User_Parking_Cost
                }
                return Spot, 200
        else:
            return {"message":"access Denied !"}, 404
        
class ReserveParkingSpot(Resource):
    @jwt_required()
    def get(self):                                     # User clicks release button from home, not actualling releasing the vehicle
        if(get_jwt().get("role")=="user"):
            parser = reqparse.RequestParser()
            parser.add_argument("spot_id",type=int,required=True,location="args")
            parser.add_argument("veh_no",type=str,required=True,location="args")
            args = parser.parse_args()

            reserve_spot = Reserve_Parking_Spot.query.filter(Reserve_Parking_Spot.spot_id == args["spot_id"],
                                                             Reserve_Parking_Spot.vehicle_no == args["veh_no"]).first()
            
            print(reserve_spot,args["veh_no"])
            Lot_spot = Parking_Spot.query.filter(Parking_Spot.spot_id == args["spot_id"]).first()

            # Spot Price Calculation
            Lot_Price = Parking_lot.query.filter_by(lot_id=Lot_spot.lot_id).first().price
            duration = ((datetime.now() - datetime.strptime(reserve_spot.parking_time, "%Y-%m-%d %H:%M:%S")).total_seconds())/180
            User_Parking_Cost = (duration/60)*Lot_Price
            reserve_spot.parking_cost = User_Parking_Cost

            reserve_spot.leaving_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if(reserve_spot):
                Spot = {
                    "spot_id": reserve_spot.spot_id,
                    "vehicle_no": reserve_spot.vehicle_no,
                    "parking_time": reserve_spot.parking_time,
                    "leaving_time": reserve_spot.leaving_time,
                    "parking_cost": float(User_Parking_Cost)
                }
                return Spot, 200
            else:
                return {"message" : "Parking Spot Not Found"},200
        else:
            return {"message":"access Denied !"}, 404          
  
    @jwt_required()
    def delete(self):
        if(get_jwt().get("role")=="user"):
            parser = reqparse.RequestParser()
            parser.add_argument("spot_id",type=int,required=True)
            parser.add_argument("veh_no",type=str,required=True)

            args = parser.parse_args()

            reserve_spot = Reserve_Parking_Spot.query.filter(Reserve_Parking_Spot.spot_id == args["spot_id"],
                                                             Reserve_Parking_Spot.vehicle_no == args["veh_no"]).first()
            

            # Spot Price Calculation
            Lot_spot = Parking_Spot.query.filter(Parking_Spot.spot_id == args["spot_id"]).first()
            Lot_Price = Parking_lot.query.filter_by(lot_id=Lot_spot.lot_id).first().price
            duration = ((datetime.now() - datetime.strptime(reserve_spot.parking_time, "%Y-%m-%d %H:%M:%S")).total_seconds())/180
            User_Parking_Cost = (duration/100000)*Lot_Price
            reserve_spot.parking_cost = User_Parking_Cost
            reserve_spot.leaving_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            reserve_spot.status = False
            if(reserve_spot):
                parking_spot = Parking_Spot.query.filter(Parking_Spot.spot_id == args["spot_id"],
                                                        Parking_Spot.lot_id == Lot_spot.lot_id).first()
                parking_spot.is_aval = True
                db.session.commit()

                #db.session.delete(reserve_spot)
                #db.session.commit()

                return {"message":"Spot Released Successfully !"}, 200
        
            else:
                return {"message":"The spot is not reserved."}, 404
        else:
            return {"message":"access Denied !"}, 404
#endregion

#region Use Parking History    
class ParkingHistory(Resource):
    @jwt_required()
    def get(self):                                    
        if(get_jwt().get("role")=="user"):
            locations,park_hist_info = [],[]
            parser = reqparse.RequestParser()
            parser.add_argument("username",type=str,required=True,location="args")
            args = parser.parse_args()

            username = User.query.filter(User.username==args["username"]).first()
            user_id = username.id
            park_hist = Reserve_Parking_Spot.query.filter(Reserve_Parking_Spot.user_id==user_id).all()

            if(park_hist):
                #park_count=0
                for park in park_hist:
                    location = Parking_lot.query.filter(Parking_lot.lot_id == park.lot_id).first()
                    action = Reserve_Parking_Spot.query.filter(Reserve_Parking_Spot.vehicle_no == park.vehicle_no).first()
                    #park_count+=1
                    park_hist_info.append({
                        "spot_id": park.spot_id,
                        "id" : park.lot_id,
                        "location": location.loc_name,
                        "vehicle_no": park.vehicle_no,
                        "timestamp" : park.parking_time ,
                        "action": action.status
                    })
            else:
                return {"message":"No Parking History"},200

            return park_hist_info,200


#endregion

#region Book Spot
class BookSpot(Resource):
    @jwt_required()
    def get(self):                                    
        if(get_jwt().get("role")=="user"):
            parser = reqparse.RequestParser()
            parser.add_argument("lot_id",type=str,required=True,location="args")
            args = parser.parse_args()
            User_id = get_jwt_identity()

            free_spot = Parking_Spot.query.filter(Parking_Spot.lot_id == args["lot_id"], Parking_Spot.is_aval == 1).first()

            if(free_spot):
                return {
                    "spot_id" : free_spot.spot_id,
                    "user_id" : User_id
                }, 200
            else:
                return {"message": f"No Spot Available for lot ID {args['lot_id']}"}
            
    @jwt_required()
    def post(self):
        if(get_jwt().get("role")=="user"):
            parser = reqparse.RequestParser()
            parser.add_argument("spot_id",type=int,required=True)
            parser.add_argument("lot_id",type=int,required=True)
            parser.add_argument("vehicle_no",type=str,required=True)

            User_id = get_jwt_identity()
            args = parser.parse_args()

            park_time = datetime.strptime(now.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
            leave_time= None

            cost = Parking_lot.query.filter_by(lot_id = args["lot_id"]).first().price

            # Checking Vehicle number for uniqueness
            vehicle_nos = Reserve_Parking_Spot.query.all()
            for no in vehicle_nos:
                if(no.vehicle_no==args["vehicle_no"]):
                    return {"message":"This vehicle is already parked. Please release it before reserving again."},200

            # With the race condition (Locks the row)
            parkingSpot = Parking_Spot.query.filter_by(spot_id = args["spot_id"],
                                                            lot_id = args["lot_id"]).with_for_update().first()
             
            if(parkingSpot.is_aval == True):       
                reserve_parkingSpot = Reserve_Parking_Spot(spot_id=args["spot_id"],lot_id=args["lot_id"],
                                        user_id=int(User_id),vehicle_no=args["vehicle_no"],
                                        parking_time=park_time,
                                        leaving_time=leave_time,
                                        parking_cost=cost,
                                        status=True)
                db.session.add(reserve_parkingSpot)
                db.session.commit()
            else:
                return {"message":"No spots left !!"}, 200
            
            parkingSpot.is_aval= False
            db.session.commit()

            return {"message":"Reservation for Parking Spot is done successfully !!"}, 201
        else:
            return {"message":"Access Denied !"}, 404

#endregion

#region User Search
class UserSearch(Resource):
    @jwt_required()
    def get(self):
        if(get_jwt().get("role")=="user"):
            lot_id = []
            lot_Info = []
            
            parser = reqparse.RequestParser()
            parser.add_argument("selected",type=str,required=False,location="args")
            parser.add_argument("searched",type=str,required=False,location="args")
            args = parser.parse_args()

            if(args["selected"] == None):
                return {"message" : "Please Select something from Dropdown."}, 200
            elif(args["searched"] == None):
                return {"message" : "Kindly enter some value."}, 200
            
            if (args["selected"]=="location"):
                lot_row = Parking_lot.query.filter(Parking_lot.loc_name == args["searched"]).all()
                for i in lot_row:
                    lot_id.append(i)

            elif (args["selected"]=="pincode"):
                lot_row = Parking_lot.query.filter(Parking_lot.lot_pincode == args["searched"]).all()
                for i in lot_row:
                    lot_id.append(i)

            for i in lot_id:
                availables = len(Parking_Spot.query.filter(Parking_Spot.lot_id == i.lot_id, Parking_Spot.is_aval == 1 ).all())
                if availables>0:
                    lot_Info.append({
                        "id" : i.lot_id,
                        "address" : i.lot_address,
                        "availables" : availables
                    })
            
            if (len(lot_Info) == 0):
                return { "message" : "No data found!" }, 200
            
            return lot_Info, 200

#endregion

#region Search

class Search(Resource):
    @jwt_required()
    def get(self):
        if(get_jwt().get("role")=="admin"):
            spots = []
            lot_id = None 
            
            spots_data = defaultdict(lambda:{"available":[],"occupied":[]})
            parser = reqparse.RequestParser()
            parser.add_argument("selected",type=str,required=False,location="args")
            parser.add_argument("searched",type=str,required=False,location="args")
            args = parser.parse_args()

            if(args["selected"] == None):
                return {"message" : "Please Select something from Dropdown."}, 200
            elif(args["searched"] == None):
                return {"message" : "Kindly enter some value."}, 200
  
            if (args["selected"]=="user_id"):
                lot_id=[]
                lots= Reserve_Parking_Spot.query.with_entities(Reserve_Parking_Spot.lot_id).filter(Reserve_Parking_Spot.user_id == args["searched"]).distinct().all()

                if(lots):
                    for lot in lots:
                        lot_id.append(lot.lot_id)

            elif (args["selected"]=="lot_id"):
                lot_id = args["searched"]

            elif (args["selected"]=="spot_id"):
                spots =  Parking_Spot.query.filter(Parking_Spot.spot_id == args["searched"]).all()
                if(lot_id):
                    lot_id = spots.lot_id 

            elif (args["selected"]=="veh_no"):
                lot_id = Reserve_Parking_Spot.query.filter(Reserve_Parking_Spot.vehicle_no == args["searched"]).first()
                if(lot_id):
                    lot_id = lot_id.lot_id
            elif (args["selected"]=="loc_name"):
                lot_id=[]
                lots = Parking_lot.query.filter(Parking_lot.loc_name == args["searched"]).all()
                if(lots):
                    for lot in lots:
                        lot_id.append(lot.lot_id)
                    
            elif (args["selected"]=="loc_add"):
                lot_id=[]
                lots = Parking_lot.query.filter(Parking_lot.lot_address == args["searched"]).all()
                if(lots):
                    for lot in lots:
                        lot_id.append(lot.lot_id)

            elif (args["selected"]=="pincode"):
                lot_id=[]
                lots = Parking_lot.query.filter(Parking_lot.lot_pincode == args["searched"]).all()
                if(lots):
                    for lot in lots:
                        lot_id.append(lot.lot_id)

            elif (args["selected"]=="no_of_spots"):
                lot_id=[]
                lots = Parking_lot.query.filter(Parking_lot.no_of_spots == args["searched"]).all()
                if(lots):
                    for lot in lots:
                        lot_id.append(lot.lot_id)

            elif (args["selected"]=="price"):
                lot_id=[]
                lots = Parking_lot.query.filter(Parking_lot.price == args["searched"]).all()
                if(lots):
                    for lot in lots:
                        lot_id.append(lot.lot_id)

            if(lot_id is not None):
                if type(lot_id) == str or type(lot_id) == int:
                    spots = Parking_Spot.query.filter(Parking_Spot.lot_id == lot_id ).all()
                    print(spots)
                else:
                    print(lot_id)
                    for i in lot_id:
                        print(i)
                        spots += Parking_Spot.query.filter(Parking_Spot.lot_id == i).all()
            print("-------------------------")
            print(spots)
           

            for spot in spots:                                     # No lots have same spot id
                if spot.is_aval:
                    status = "available"
                else:
                    status = "occupied"
                spots_data[spot.lot_id][status].append(spot.spot_id)  # here key is lot id and inside it there are 2 keys available and occupied with spot id element lists
        

            if(spots_data):
                spots_info = [{
                    "lot_id" : lot_id,
                    "Available": data["available"],
                    "Occupied": data["occupied"],
                    "Total" : len(data["available"]) + len(data["occupied"])    
                }for lot_id,data in spots_data.items()]

                return spots_info,200
            else:
                return {"message" : "Couldn't Find Anything!"}, 200
        
            
#endregion

#region UserChart
class UserChart(Resource):
    @jwt_required()
    def get(self):
        if(get_jwt().get("role")=="user"):
            status = ["Parked Out", "Parked"]
            park_out = 0
            park_in = 0
            park = []

            Userid = get_jwt_identity()
            parks = Reserve_Parking_Spot.query.filter(Reserve_Parking_Spot.user_id == int(Userid)).all()
            for i in parks:
                if(i.status == False):
                    park_out += 1
                else:
                    park_in += 1

            park.append(park_out)
            park.append(park_in)

            data = {
                "status": status,
                "value": park
                }
            
            return data,200


#endregion



#region AdminChart
class AdminChart(Resource):
    @jwt_required()
    def get(self):
        if(get_jwt().get("role")=="admin"):
            status = ["Available", "Occupied"]
            lot_occ = set()
            lot_aval = set()
            park = []

            Userid = get_jwt_identity()
            occ = aval = Parking_Spot.query.filter(Parking_Spot.is_aval==False).all()
            for i in occ:
                lot_occ.add(i.lot_id)

            aval = Parking_Spot.query.filter(Parking_Spot.is_aval==True).all()
            for i in aval:
                lot_aval.add(i.lot_id)

            lot_aval = lot_aval - lot_occ


            park.append(len(lot_aval))
            park.append(len(lot_occ))

            data = {
                "status": status,
                "value": park
                }
            
            return data,200
#endregion


#region Jobs
class EmailSender:
    @staticmethod
    def send_email(to, subject, body, is_html=False):
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_USER
            msg['To'] = to
            msg['Subject'] = subject

            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print("error:", e)

@celery.task(name="backend.app.send_daily_reminder")
def send_daily_reminder():
    with app.app_context():
        print(f"[DEBUG] Using DB file: {app.config['SQLALCHEMY_DATABASE_URI']}")
        now_ist = datetime.now()
        today_ist = now_ist.date()
        print(f"[DEBUG] Current IST time: {now_ist}")

        new_lots = Parking_lot.query.filter(
            Parking_lot.admin_created == True,
            Parking_lot.created_at >= now_ist.replace(hour=0, minute=0, second=0, microsecond=0)
        ).all()
        print(f"[DEBUG] New lots today: {len(new_lots)}")

        users = User.query.filter(User.role == 'user').all()
        print(f"[DEBUG] Total users: {len(users)}")

        for user in users:
            print(f"[DEBUG] Processing user: {user.email_id}, role: {user.role}, last_login: {user.last_login}")
            no_visit_today = False
            if user.last_login is None:
                no_visit_today = True
            else:
                if user.last_login.date() < today_ist:
                    no_visit_today = True
                if((user.last_login.date() < today_ist) or (not user.last_login)):
                    no_visit_today =  not user.last_login

            new_lot_created = len(new_lots) > 0

            if no_visit_today or new_lot_created:

                lot = Parking_lot.query.filter(Parking_lot.admin_created == True).first()
                body = f"Hi {user.first_name},\n\n"
                if no_visit_today:
                    body += "You have not visited the parking area today.\n"
                if new_lot_created:
                    body += "A new parking lot has been added today!\n"
                body += "\nBest regards,\nParking System"

                EmailSender.send_email(user.email_id, "Daily Parking Reminder", body)
                print(f"[DEBUG] Email sent to {user.email_id}")

        for lot in new_lots:
            lot.admin_created = False
        db.session.commit()

        print("Daily reminder sent (IST).")

@app.route("/status")
def status():
    return jsonify({"message": "Parking system backend running."})


@celery.task(name="backend.app.send_monthly_report")
def send_monthly_report():
    with app.app_context():
        users = User.query.filter(User.role == 'user').all()

        template_path = Path(__file__).parent / "templates" / "monthly_report_template.html"
        template_content = template_path.read_text()

        for user in users:
            bookings = Reserve_Parking_Spot.query.filter(
                Reserve_Parking_Spot.user_id == user.id,
                Reserve_Parking_Spot.parking_time >= datetime(datetime.now().year, datetime.now().month, 1),
                Reserve_Parking_Spot.leaving_time != None
            ).all()

            total_booked = len(bookings)
            most_used_lot = ""
            total_amount = 0
            if bookings:
                for book in bookings:
                    total_amount += book.parking_cost
            else:
                total_amount = 0


            if bookings:
                lot_counts = {}
                for book in bookings:
                    lot_counts[book.lot_id] = lot_counts.get(book.lot_id, 0) + 1
                most_used_lot_id = max(lot_counts, key=lot_counts.get)
                print(most_used_lot_id)
                lot = Parking_lot.query.get(most_used_lot_id)
                most_used_lot = lot.lot_id if lot else "N/A"

            # Render HTML
            template = Template(template_content)
            body_html = template.render(
                first_name=user.first_name,
                total_booked=total_booked,
                most_used_lot=most_used_lot,
                total_amount=total_amount
            )

            # Send email
            EmailSender.send_email(user.email_id, "Your Monthly Parking Report", body_html,is_html=True)
            print(f"[DEBUG] Monthly report sent to {user.email_id}")

class UserCsv(Resource):
    @jwt_required()
    def get(self):
        if(get_jwt().get("role")=="user"):
            user_id = get_jwt_identity()

            user = User.query.get(user_id)
            parking_records = Reserve_Parking_Spot.query.filter(Reserve_Parking_Spot.user_id == user_id,
                                                                Reserve_Parking_Spot.leaving_time != None).all()

            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["Lot ID", "Spot ID", "Timestamp", "Cost"])  

            for record in parking_records:
                writer.writerow([
                    record.lot_id,
                    record.spot_id,
                    record.parking_time,
                    record.parking_cost
                ])

            csv_content = output.getvalue()
            output.close()

            return Response(
                csv_content,
                mimetype="text/csv",
                headers={"Content-Disposition": f"attachment;filename=user_{user_id}_parking.csv"}
            )
            

#endregion

api.add_resource(SignupResource,'/api/signup')
api.add_resource(sign_In_resource,'/api/signin')
api.add_resource(logout_resource,'/api/logout')
api.add_resource(UserInfo_Resource,'/api/userInfo') 
api.add_resource(UserParkingSpots,'/api/UserParkingSpots')
api.add_resource(ParkingLot_Info,'/api/parkingLotInfo')
api.add_resource(ParkingLot,'/api/parkingLot')
api.add_resource(ParkingSpot,'/api/parkingSpot') 
api.add_resource(AvailableSpot,'/api/availableSpot')
api.add_resource(ReserveParkingSpotAdmin,'/api/reserveParkingSpotAdmin')
api.add_resource(ReserveParkingSpot,'/api/reserveParkingSpot')
api.add_resource(Search,'/api/Search')
api.add_resource(ParkingHistory,'/api/ParkingHistory')
api.add_resource(UserSearch,'/api/UserSearch')
api.add_resource(BookSpot,'/api/BookSpot')
api.add_resource(UserChart,'/api/userChart')
api.add_resource(AdminChart,'/api/adminChart')
api.add_resource(UserCsv,'/api/userCsv')



if __name__ == "__main__":
    app.run(debug=True)
