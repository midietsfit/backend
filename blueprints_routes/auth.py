import jwt
from base import *
import os
from datetime import datetime, timedelta
import pytz
from flask_socketio import disconnect

UPLOAD_FOLDER = os.path.join("uploads", "image") 



# from base import Blueprint
# from base import getRole
def unique_timestamp():
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist)
    timestamp = int(current_time.timestamp() * 1000)
    return timestamp

def unique_timestamp_dayWise(days=1):
    ist = pytz.timezone('Asia/Kolkata')

    current_time = datetime.now(ist)
    days_after = current_time + timedelta(days=days)
    timestamp = int(days_after.timestamp() * 1000)

    return (timestamp)




auth_blueprint = Blueprint("Auth_User", __name__)


def getRole(roleName):
    aggr = [
        {
            '$match': {
                'role': roleName
            }
        }, {
            '$project': {
                '_id': {
                    '$toString': '$_id'
                }, 
                'role': 1
            }
        }
    ]
    getrole = list(cmo.finding_aggregate("userRole", aggr))
    if len(getrole):
        return getrole[0]["_id"]
    else:
        return "None"


def tokenGenerate(token=None,encode=False,userDetails=None):
    data=[]
    if encode:
        data=jwt.encode(
                    {"userDetails": userDetails[0], "userId": userDetails[0]["_id"],'exp': unique_timestamp_dayWise(1)},
                    key="admin",
                    algorithm="HS512",
                )
    else:
        data=jwt.decode(
                    token.split(" ")[-1],
                    algorithms="HS512",
                    key="admin",
                )
    return data

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        #modify code to handle token from websocket
        if "Authorization" in request.headers:
            token = request.headers["Authorization"]
        elif 'token' in request.args:
            token = request.args.get('token')
        elif 'token' in kwargs:
            token = kwargs['token']
        if not token:
            return (jsonify({"msg": "a valid token is missing","status":'false'}),404)
        print("asfasfsadfsadfsafdsadfdsafdsafsadfas",token)
        try:
            data = tokenGenerate(token,False)
            aggr = [
                {
                    "$match": {
                        "_id": ObjectId(data["userId"]),
                    }
                },
                {"$addFields": {"role": {"$toObjectId": "$role"}}},
                {
                    "$lookup": {
                        "from": "userRole",
                        "localField": "role",
                        "foreignField": "_id",
                        "as": "userRole",
                    }
                },
                {
                    "$addFields": {
                        "roleId": {"$toString": "$role"},
                        "role": {"$arrayElemAt": ["$userRole.role", 0]},
                        "_id": {"$toString": "$_id"},
                    }
                },
                {
                    "$project": {
                        "userRole": 0,
                    }
                },
            ]
            current_user = list(cmo.finding_aggregate("users", aggr))
            print("afafasfasfsadfdsafasfasfdasd",current_user)
            database_data = len(current_user)
            if database_data == 0:
                return jsonify({"msg": "token is invalid","status":False}),401
            # if data["exp"]<unique_timestamp() :
            #     access_token=tokenGenerate(token,True,current_user)
                
                # return (
                #     jsonify(
                #         {
                #             "msg": "Login Successfully",
                #             "user": current_user[0],
                #             "statusCode": 200,
                #             "userId": current_user[0]["_id"],
                #             "token": access_token,
                #             "Current Plan":'',
                #             'Plan Status':'',
                #             'status':True
                #         }
                #     ),
                #     200,
                # )
        except Exception as e:
            return jsonify({"msg": "token is invalid",'status':'false'}), 401
        print("asfsfsfsdfasfasddsafertyu",current_user[0])
        return f(current_user[0], *args, **kwargs)
    
    return decorator

@auth_blueprint.route("/genrateToken", methods=["GET", "POST"])
@token_required
def genrateToken():
    token = None
    if "Authorization" in request.headers:
            token = request.headers["Authorization"]
    if not token:
            return (jsonify({"msg": "a valid token is missing"}),)
    data = tokenGenerate(token,False)
    access_token = tokenGenerate(token,True,data)
    return jsonify({"token":access_token}),200




@auth_blueprint.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        
        email = request.form.get("email")
        password = request.form.get("password")
        mobile = request.form.get("mobile")
        UserRole = request.form.get("role")
        if not UserRole:
            return jsonify({"msg": "Please Provide UserRole"}),400
        if not any([email, mobile]):
            return jsonify({"msg": "Please provide email or mobile"}), 404
        matchObj = {"role": getRole(UserRole)}
        if email:
            matchObj["email"] = email
        elif mobile:
            matchObj["mobile"] = int(mobile)

        aggregation_pipeline = [
            {
                "$match": matchObj,
            }, {
                "$addFields":{
                    "role": {"$toObjectId": "$role"}
                }
            }, {
                "$lookup": {
                    "from": "userRole",
                    "localField": "role",
                    "foreignField": "_id",
                    "as": "userRole",
                }
            }, {
                "$addFields": {
                    "roleId": {"$toString": "$role"},
                    "role": {"$arrayElemAt": ["$userRole.role", 0]},
                    "_id": {"$toString": "$_id"},
                    "userId": {"$toString": "$_id"},
                }
            }, {
                "$project": {
                    "userRole": 0,
                    "appointments": 0,
                    "mobile": 0,
                }
            },
        ]
        userDetails = list(cmo.finding_aggregate("users", aggregation_pipeline))
        if len(userDetails):
            if userDetails[0]['status'] != False:
                password = request.form.get("password")
                if not password:
                    return jsonify({"msg": "Please Enter Your Password"}), 400 
                if "password" in userDetails[0] and (password) == str(userDetails[0]["password"]):
                    access_token = tokenGenerate(None,True,userDetails)
                    return (
                        jsonify(
                            {
                                "msg": "Login Successfully",
                                "user": userDetails[0],
                                "statusCode": 200,
                                "userId": userDetails[0]["_id"],
                                "token": access_token,
                            }
                        ),
                        200,
                    )
                else:
                    return jsonify({"msg": "Please enter valid password"}), 404
            else:
                return jsonify({'msg':'This user is restricted by Admin','statusCode':404,'status':'true'}),404
            # elif mobile:
            #     otp = random.randint(1000, 9999)
            #     # role: getRole("USER")
            #     id = userDetails[0]["_id"]
            #     data = {
            #         'otp':otp
            #     }
            #     updateBy={'_id':ObjectId(id)}
            #     cmo.update("users",updateBy,data,False)
            #     return jsonify({'msg':"success",'OTP':otp}),200
            # else:
            #     return jsonify({"msg": "Please enter valid Credentials"}), 404
        else:
            return jsonify({"msg": "Please enter valid Credentials"}),404
            if any([mobile]):
                mobile = request.form.get("mobile")
                otp = random.randint(1000, 9999)
                data = {"mobile": int(mobile), "otp":  otp, "role": getRole("USER")}
                respond = cmo.insertion("users", data)
                return jsonify({"msg": "registered successfully", "otp": otp}), 201
            else:
                return jsonify({"msg": "Please enter valid Credentials"}), 404
            
# ------------------for User--------------------#




@auth_blueprint.route("/registration", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        mobile = request.form.get("mobile")
        if not mobile:
            return jsonify({"msg": "Please Provide Mobile Number",'status':'false','statusCode':404}),404
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        age = request.form.get("age")
        gender = request.form.get("gender")
        height = request.form.get("height")
        weight= request.form.get("weight")
        goal= request.form.get("goal")
        foodPreference= request.form.get("foodPreference")
        bio= request.form.get("bio")

        arra = [
            {
                '$match':{
                    'mobile':mobile,
                    'isDeleted':{'$ne':1},
                }
            }, {
                '$addFields': {
                    '_id': {
                        '$toString': '$_id'
                    }
                }
            }
        ]
        userDetails = list(cmo.finding_aggregate("users",arra))
        if len(userDetails):
            if userDetails[0]['status'] != False:
                otp = random.randint(1000, 9999)
                id = userDetails[0]["_id"]
                updateBy={'_id':ObjectId(id)}
                
                
                twillio_msg.send_sms(mobile,f"Your MiDiets App verification code is {otp} to verify your number")
                # message = client.messages.create(
                #     body=otp,
                #     from_="+15642166902",
                #     to=userDetails[0]["mobile"]
                # )
                data = {
                    'otp':otp
                }


                cmo.update("users",updateBy,data,False)
                userDetails = list(cmo.finding_aggregate("users",arra))
                return jsonify({'status':"true","msg":"Success","statusCode":200,"data":userDetails[0],'otp':otp}),200
            else:
                return jsonify({'msg':'This User is restricted by Admin','status':'false','statusCode':404}),404
        else:
            otp = random.randint(1000, 9999)


            twillio_msg.send_sms(mobile,f"Your MiDiets App verification code is {otp} to verify your number")
            # account_sid = acc_id
            # auth_token = acc_sec
            # client = Client(account_sid, auth_token)
            # message = client.messages.create(
            #     from_=from_msg,
            #     body=f"Your MiDiets App verification code is {otp} to verify your number",
            #     to=to_msg
            # )

            



            
            data = {"fullname":fullname,
                    "mobile": mobile,
                    'email':email,
                    "otp": otp, 
                    'age':age,
                    'gender':gender,
                    'height':height,
                    'weight':weight,
                    'goal':goal,
                    'foodPreference':foodPreference,
                    'bio':bio,
                    "role": getRole("USER"),
                    "roleName":"USER",
                    'planStatus':False,
                    'otpStatus':1,
                    'status':True,
                    'dietStatus':'',
                    'date':datetime.now().strftime("%Y-%m-%d")
                    }
            respond = cmo.insertion("users",data)
            arra = [
                {
                    '$match': {
                        'isDeleted': {'$ne': 1}, 
                        'mobile': mobile
                    }
                }, {
                    '$addFields': {
                        '_id': {
                            '$toString':'$_id'
                        }
                    }
                }
            ]
            data = list(cmo.finding_aggregate("users",arra))
            return jsonify({"status": "true", "msg":"Success","statusCode":201,"data":data[0],'otp':otp}),201


@auth_blueprint.route("/loginInternal", methods=["GET", "POST"])
@token_required
def loginInternal(current_user):
    userid = current_user["_id"]
    if request.method == "POST":
        mobile = request.form.get("mobile")
        if not mobile:
            return jsonify({"msg":'Please Enter Your Mobile Number','status':'false','statusCode':404}),404
        arra = [
            {"$match": {"mobile": mobile, "isDeleted": {"$ne": 1}}},
            {"$addFields": {"_id": {"$toString": "$_id"}}},
            {"$addFields": {"userid": "$_id"}},
            {"$match": {"_id": {"$eq": userid}}},
        ]
        data = list(cmo.finding_aggregate("users", arra))
        if len(data):
            return (
                jsonify(
                    {
                        "msg": "Login Successfully",
                        "statusCode": 200,
                        'status':'true',
                        'data':{
                            'uniqueId':data[0]['_id'],
                        }
                    }
                ),
                200,
            )
        else:
            return jsonify({"msg": "please Enter valid Mobile Number",'status':'false'})
    else:
        return jsonify({"msg": "Invalid Token",'status':'false'})
        



@auth_blueprint.route("/verifyotp", methods=["GET", "POST"])
def verifyOtp():
    if request.method == "POST":
        mobile = request.form.get("mobile")
        if not mobile:
            return jsonify({"msg": "Please Provide Mobile Number","status":False,"statusCode":400}),400
        arr = [
            {
                "$match": {
                    "mobile": mobile,
                    'isDeleted':{'$ne':1}
                }
            },
            {
                "$addFields": {
                    "_id": {"$toString": "$_id"},
                }
            },
        ]
        userDetails = list(cmo.finding_aggregate("users", arr))
        if len(userDetails):
            otp = request.form.get("otp")
            if not otp:
                return jsonify({"msg": "Please Provide otp","status":False,"statusCode":400}),400
            if userDetails[0]["otp"] == int(otp):
                data={
                    'otpStatus':0
                }
                updateBy = {
                    '_id':ObjectId(userDetails[0]['_id'])
                }
                cmo.update("users",updateBy,data,False)
                userDetails = list(cmo.finding_aggregate("users", arr))
                access_token =tokenGenerate(None,True,userDetails)
                return (
                    jsonify(
                        {
                            "msg": "Login Successfully",
                            "user": userDetails[0],
                            "statusCode": 200,
                            "userId": userDetails[0]["_id"],
                            "token": access_token,
                            "CurrentPlan":'',
                            'PlanStatus':'',
                            'Level':"",
                            'XP':'',
                            'status':'true'
                        }
                    ),
                    200,
                )
            else:
                return jsonify({"msg": "Invalid otp","status":'false','statusCode':404}),404
        else:
            return jsonify({"msg": "Please Enter Valid Mobile Number","status":'false','statusCode':404}),404
    else:
        return jsonify({"msg": "Invalid Request",'status':'false','statusCode':404}),404


@auth_blueprint.route("/updateProfile", methods=["GET", "POST"])
@token_required
def ProfileUpdate(current_user):
    print(current_user,'current_user')
    if request.method == "POST":
        fullname = request.form.get("fullname")
        image = request.files.get("img")
        bio = request.form.get("bio")
        email=request.form.get("email")
        # mobile=request.form.get("mobile")
        age=request.form.get("age")
        location=request.form.get("location")
        height=request.form.get("height")
        weight=request.form.get("weight")
        gender=request.form.get("gender")
        goal=request.form.get("goal")
        foodPreference=request.form.get("foodPreference")
        data = {}
        if image:
            ext = str(image.filename).split(".")[-1]
            fileName = str(unique_timestamp()) + "." + ext
            path = os.path.join(UPLOAD_FOLDER, fileName)
            image.save(path)
            data["img"] = path
        if fullname:
            data["fullname"] = fullname
        if bio:
            data["bio"] = bio
        if email:
            data['email'] = email
        # if mobile:
        #     data['mobile'] = mobile
        if age:
            data['age'] = age
        if location:
            data['location'] = location
        if height:
            data['height'] = height
        if weight:
            data['weight'] = weight
        if gender:
            data['gender'] = gender
        if goal:
            data['goal'] = goal
        if foodPreference: 
            data['foodPreference'] = foodPreference

        update = {
            "_id": ObjectId(current_user["_id"])
        }
        updated_user = cmo.update("users", update, data, False)
        if updated_user:
            return jsonify({"msg": "User updated successfully.", "code": 200,"status":'true'}),200
        else:
            return jsonify({"msg": "User not found.", "code": 404,"status":'false'}),404


@auth_blueprint.route('/updateTarget',methods=['POST'])
@token_required
def updateTarget(current_user):
    if request.method == "POST":
        data = request.get_json()
        update = {
            "_id": ObjectId(current_user["_id"])
        }
        updated_user = cmo.update("users", update, data, False)
        if updated_user:
            return jsonify({"msg": "User updated successfully.", "code": 200,"status":'true'}),200
        else:
            return jsonify({"msg": "User not found.", "code": 404,"status":'false'}),404
        

@auth_blueprint.route("/getprofile", methods=["GET"])
@token_required
def getprofile(current_user):
    print("asfddsafasdfasfasfddsaf__current_user",current_user)
    if request.method == "GET":
        arra = [
    {
        '$match': {
            'isDeleted': {
                '$ne': 1
            }, 
            '_id': ObjectId(current_user['_id'])
            # '_id': ObjectId('6593e76018806c38b4accda3')
        }
    }, {
        '$addFields': {
            '_id': {
                '$toString': '$_id'
            }
        }
    }, {
        '$project': {
            # 'img': 1, 
            # 'fullname': 1, 
            # 'target': 1, 
            # 'current_target': 1, 
            # 'left_target': 1, 
            # 'email': 1, 
            # 'rating': 1, 
            # 'bio': 1, 
            # 'age': 1, 
            # 'foodPreference': 1, 
            # 'goal': 1, 
            # 'gender': 1, 
            # 'height': 1, 
            # 'location': 1, 
            # 'number': 1, 
            # 'weight': 1, 
            # 'achievment': 1, 
            # 'duration': 1, 
            # 'feedback': 1, 
            # 'member': 1, 
            # 'mobile': 1, 
            '_id': 0
        }
    }
]
        data = list(cmo.finding_aggregate("users", arra))
        return jsonify({"data": data,'status':'true','statusCode':200}),200


# @auth_blueprint.route("/login", methods=["POST", "GET"])
# def login():
#     email = request.form.get("email")
#     password = request.form.get("password")
#     mobile = request.form.get("mobile")
#     if not any([email, mobile]):
#         return jsonify({"msg": "Please provide email or mobile"}), 404
#     matchObj = {}
#     if email:
#         matchObj["email"] = email
#     elif mobile:
#         matchObj["mobile"] = int(mobile)
#     aggregation_pipeline = [
#         {"$match": matchObj},
#         {"$addFields": {"role": {"$toObjectId": "$role"}}},
#         {
#             "$lookup": {
#                 "from": "userRole",
#                 "localField": "role",
#                 "foreignField": "_id",
#                 "as": "userRole",
#             }
#         },
#         {
#             "$addFields": {
#                 "roleId": {"$toString": "$role"},
#                 "role": {"$arrayElemAt": ["$userRole.role", 0]},
#                 "_id": {"$toString": "$_id"},
#                 "userId":{"$toString": "$_id"}
#             }
#         },
#         {"$project": {"userRole": 0,"appointments":0}},
#     ]
#     userDetails = list(cmo.finding_aggregate("users", aggregation_pipeline))
#     length=len(userDetails)

#     if length>0:
#         if email and password:
#             
#             if "password" in userDetails[0] and (password) == str(
#                 userDetails[0]["password"]
#             ):
#                
#                 access_token = jwt.encode(
#                     {"userDetails": userDetails[0], "userId": userDetails[0]["_id"]},
#                     key="sandeep",
#                     algorithm="HS512",
#                 )
#                 return (
#                     jsonify(
#                         {
#                             "msg": "Login Successfully",
#                             "user": userDetails[0],
#                             "statusCode": 200,
#                             "userId": userDetails[0]["_id"],
#                             "token": access_token,
#                         }
#                     ),
#                     200,
#                 )
#             else:
#                 return jsonify({"msg": "Please enter valid credentdials"}), 404
#         elif mobile:
#             # if any([mobile]):
#                 mobile = request.form.get("mobile")
#                 #body['role'] =getRole("MEMBER")

#                 otp = random.randint(1000, 9999)
#                 # data = {"mobile": int(mobile), "otp": otp,"role":getRole("USER")}
#                 data = { "otp": otp}
#                 respond = cmo.update("users", {"_id",ObjectId(userDetails[0]["_id"])},data)
#                 return jsonify({"msg": "registered successfully",'otp':otp}),200
#         else:
#                 return jsonify({"msg": "Please enter valid Credentials"}),404

#             # return jsonify({'msg':"You are already registerd"}),200
#             # mobile = request.form.get("mobile")
#             # otp = random.randint(2000, 9999)
#             # data = {"mobile": int(mobile), "otp": otp}
#             # respond = cmo.insertion("users", data)
#             # return jsonify({"msg": "registered successfully"})
#             # if "otp" in userDetails[0] and int(otp) == userDetails[0]["otp"]:
#             #     access_token = jwt.encode(
#             #         {"userDetails": userDetails[0], "userId": userDetails[0]["_id"]},
#             #         key="sandeep",
#             #         algorithm="HS512",
#             #     )
#             #     return (
#             #         jsonify(
#             #             {
#             #                 "msg": "Login Successfully",
#             #                 "user": userDetails[0],
#             #                 "statusCode": 200,
#             #                 "userId": userDetails[0]["_id"],
#             #                 "token": access_token,
#             #             }
#             #         ),
#             #         200,
#             #     )
#             # else:
#             #     return jsonify({"msg": "Please enter valid OTP"}), 404
#     else:
#         # return jsonify({"msg": "Please enter valid Credentials"}), 404
#         if any([mobile]):
#             mobile = request.form.get("mobile")
#             #body['role'] =getRole("MEMBER")

#             otp = random.randint(1000, 9999)
#             data = {"mobile": int(mobile), "otp": otp,"role":getRole("USER")}
#             respond = cmo.insertion("users", data)
#             return jsonify({"msg": "registered successfully",'otp':otp}),201
#         else:
#             return jsonify({"msg": "Please enter valid Credentials"}),404
