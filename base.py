from flask import Flask, json, jsonify, redirect, request, Response, Blueprint ,  send_file, make_response,render_template
from twilio.rest import Client
import random
# import requests
# from common import mongoDb_operation as cmo
from common import mongoDb_operation as cmo
from common import twillio_msg as twillio_msg
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
    
    
# 46SCB552K2TSZP771XA827BY

