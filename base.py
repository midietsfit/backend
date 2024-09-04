from flask import Flask, json, jsonify, redirect, request, Response, Blueprint ,  send_file, make_response
from twilio.rest import Client
import random
# import requests
# from common import mongoDb_operation as cmo
from common import mongoDb_operation as cmo
from flask_cors import CORS
import jwt
from bson.objectid import ObjectId
from pymongo import MongoClient
from functools import wraps
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
from blueprints_routes.auth import token_required
from datetime import datetime
import datetime as d
from twilio.rest import Client
from io import BytesIO
import json
##########Implement Web Socket API###############
from flask_socketio import SocketIO, emit 
################ Impleting Firebase #############
import firebase_admin

def getRole(roleName):
    aggr = [
        {"$match": {"role": roleName}},
        {"$project": {"_id": {"$toString": "$_id"}, "role": 1}},
    ]
    getrole=list(cmo.finding_aggregate("userRole",aggr))
    if len(getrole):
        return getrole[0]['_id']
    else:
        return "None"

# def send_otp_to_mobile(mobile_number):
#     account_sid = 'AC5507190ad516af84144107b5a5e2d250'
#     auth_token = '642531ab3b431354a2d631b829f71eb4'
#     twilio_phone_number = '+91 8708182238'
#     generated_otp = str(random.randint(100000, 999999))
#     print("Generated OTP",generated_otp)
#     client = Client(account_sid, auth_token)
#     message = client.messages.create(
#         body=f"Your OTP is: {generated_otp}",
#         from_=twilio_phone_number,
#         to=mobile_number
#     )
#     print("Message sent to mobile_number with SID: {message.sid}")

# mobile_number = '+91 75056 20556'
# send_otp_to_mobile(mobile_number)