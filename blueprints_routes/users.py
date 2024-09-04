from base import *
import os
import jwt
from datetime import datetime
from common.mongoDb_operation import unique_timestamp
from common.mail import send_email

user=Blueprint("user_data",__name__)

UPLOAD_FOLDER = os.path.join("uploads", "image")

@user.route("/uploads/<subDir>/<fileName>")
def send_file_route(subDir, fileName):
    try:
        file_path = os.path.join(os.getcwd(),"uploads", subDir, fileName)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return "File not found", 404
    except Exception as e:
        # Log the exception or handle it appropriately
        return f"Error: {str(e)}", 500


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

@user.route('/user',methods=['GET','POST','PUT','PATCH',"DELETE"])
@user.route('/user/<id>',methods=["GET",'POST','PUT','PATCH',"DELETE"])
@user.route('/user/<id>/<memberid>',methods=["GET",'POST','PUT','PATCH',"DELETE"])
@token_required
def userDetails(current_user,id=None,memberid=None):
    if request.method == 'GET':
        arra=[
            {
                '$match': {
                    'isDeleted': {'$ne': 1},
                    'role':getRole('USER')
                }
            }, {
                '$addFields': {
                    'date': {
                        '$dateToString': {
                            'format': '%Y-%m-%d', 
                            'date': {
                                '$toDate': '$date'
                            }
                        }
                    }
                }
            }, {
                '$lookup': {
                    'from': 'Appointments', 
                    'localField': 'mobile', 
                    'foreignField': 'mobile', 
                    'pipeline': [
                        {
                            '$match': {
                                'isDeleted':{'$ne':1},
                                '$expr': {
                                    '$gte': [
                                        '$date', datetime.now().strftime("%Y-%m-%d")
                                    ]
                                }
                            }
                        }
                    ], 
                    'as': 'result'
                }
            }, {
                '$addFields': {
                    'length': {
                        '$size': '$result'
                    }
                }
            }, {
                '$addFields': {
                    'appointStatus': {
                        '$cond': {
                            'if': {
                                '$gt': [
                                    '$length', 0
                                ]
                            }, 
                            'then': 'Yes', 
                            'else': 'No'
                        }
                    }
                }
            }, {
                '$project':{
                    'result':0
                }
            }
        ]
        if request.args.get("fetch"):
            arra = arra + [
                {
                    '$match':{
                        'assignMemberId':current_user['_id']
                    }
                }
            ]
            if (request.args.get('fetch') == "inactive"):
                arra = arra + [
                    {
                        '$match':{
                            'planStatus':False
                        }
                    }
                ]
        if id!=None:
            arra = arra + [
                {
                    '$match':{
                        'assignMemberId':id
                    }
                }
            ]
        if (request.args.get('q') == "unverified"):
            arra = arra + [
                {
                    '$match':{'otpStatus':{'$eq':1}}
                }
            ]
        if (request.args.get('q') == "active"):
            arra = arra + [
                {
                    '$match':{
                        'planStatus':True,
                        'otpStatus':{'$ne':1}
                    }
                }
            ]
        if (request.args.get('q') == "inactive"):
            arra = arra + [
                {
                    '$match':{
                        'planStatus':False,
                        'otpStatus':{'$ne':1}
                    }
                }
            ]
        arra = arra + [
            {
                '$addFields': {
                    'userId': {
                        '$toString': '$_id'
                    }, 
                    '_id': {
                        '$toString': '$_id'
                    }
                }
            }, {
                '$lookup': {
                    'from': 'meals', 
                    'let': {
                        'uId': {
                            '$toString': '$userId'
                        }
                    }, 
                    'pipeline': [
                        {
                            '$match': {
                                'isDeleted': {
                                    '$ne': 1
                                }
                            }
                        }, {
                            '$addFields': {
                                'dateDb': {
                                    '$dateFromString': {
                                        'dateString': '$date', 
                                        'format': '%d/%m/%Y'
                                    }
                                }, 
                                'dateCurr': {
                                    '$dateFromString': {
                                        'dateString': datetime.now().strftime("%d/%m/%Y"), 
                                        'format': '%d/%m/%Y'
                                    }
                                }
                            }
                        }, {
                            '$match': {
                                '$expr': {
                                    '$gte': [
                                        '$dateDb', '$dateCurr'
                                    ]
                                }
                            }
                        }, {
                            '$match': {
                                '$expr': {
                                    '$eq': [
                                        '$primaryId', '$$uId'
                                    ]
                                }
                            }
                        }, {
                            '$addFields': {
                                'uniqueId': {
                                    '$toString': '$_id'
                                }
                            }
                        }, {
                            '$project': {
                                '_id': 0
                            }
                        }, {
                            '$group': {
                                '_id': {
                                    'meal': '$meal', 
                                    'date': '$date'
                                }, 
                                'data': {
                                    '$push': '$$ROOT'
                                }, 
                                'count': {
                                    '$sum': 1
                                }, 
                                'meal': {
                                    '$first': '$meal'
                                }
                            }
                        }, {
                            '$group': {
                                '_id': '$_id.date', 
                                'data': {
                                    '$push': '$$ROOT'
                                }, 
                                'cot': {
                                    '$sum': '$count'
                                }
                            }
                        }, {
                            '$match': {
                                'cot': {
                                    '$gte': 1
                                }
                            }
                        }
                    ], 
                    'as': 'result'
                }
            }, {
                '$addFields': {
                    'memberColorSize': {
                        '$size': '$result'
                    }
                }
            }, {
                '$project': {
                    'result': 0
                }
            }
        ]
        
        
        print(arra,"arraarraarra")
        data=list(cmo.finding_aggregate("users",arra))
        return jsonify({'msg':"success",'status':'true','data':data,'statusCode':200}),200
    
    if request.method == 'POST':
        body=request.get_json()
        arra=[
            {
                '$match':{
                'mobile':{
                    '$eq':body["mobile"]
                }
                }
            }, {
                '$addFields': {
                    '_id': {
                        '$toString': '$_id'
                    },
                }
            }
        ]  
        data=list(cmo.finding_aggregate("users",arra))
        if len(data):
            return jsonify({'msg':'This Mobile Number is already exist...','status':'false','statusCode':404}),404
        
        if request.args.get('completion'):
            updateCompStatus={
                'completionStatus':'completion'
            }
            cmo.update("users",updateCompStatus)
            pass

        else:
            body['role'] = getRole('USER')
            body['roleCreatedBy'] = current_user['role']
            body['idCreatedBy'] = current_user['_id']
            if current_user['role'] == "MEMBER":
                body['assignMemberId'] = current_user['_id']
                body['assign'] = current_user['fullname']

            body.setdefault('status',True)
            respond=(cmo.insertion("users",body))
            return jsonify({'msg':'Data Added Successfully','status':'true','statusCode':201}),201
        
        # if request.args.get('completion')
    if request.method == "PUT":

        if id!=None: 
            if request.args.get('completion'):
                print('completionnnnnnnnnnnnnnnnnnnnn',request.args.get('completion'))
                updateBy={'_id':ObjectId(id)}
                updateCompStatus={
                    'completionStatus':True,
                }

                cmo.update("users",updateBy,updateCompStatus)
                
        
            body=request.get_json()
            print(body,'bodybodybodybodybody')
            print(body,'body')
            if memberid!=None:
                body['assignMemberId'] = memberid
            updateBy={'_id':ObjectId(id)}
            respond=cmo.update("users",updateBy,body,False)
            return jsonify({'msg':'Data Updated Successfully','status':'true','statusCode':200}),200
        
            

        else:
            return jsonify({'msg':'Data is not Updated','status':'false','statusCode':404}),404
    if request.method == "DELETE":
        if id!=None:
            respond=cmo.deleteStatus("users",id)
            return jsonify({'msg':'Successfully Deleted'})
        else:
            return jsonify({'msg':'Unsuccessfully Updated'})

@user.route('/userDashboard',methods=['GET','POST','PUT','PATCH',"DELETE"])
@token_required
def userdashboard(current_user):
    if request.method == "GET":
        arra = [
            {
                '$match':{
                    'assignMemberId':current_user['_id']
                }
            }, {
                '$addFields':{
                    '_id':{
                        '$toString':'$_id'
                    }
                }
            }
        ]
        response = list(cmo.finding_aggregate("users",arra))
        return jsonify({"msg":'Data Get Successfully','data':response}),200


        
@user.route('/vishal/<id>',methods=['GET','POST','PUT','PATCH',"DELETE"])
@token_required
def vishal(current_user,id=None):
    if request.method == "GET":
        arra = [
            {
                '$match': {
                    'isDeleted': {
                        '$ne': 1
                    }, 
                    '_id': ObjectId(id)
                }
            }, {
                '$addFields': {
                    '_id': {
                        '$toString': '$_id'
                    }
                }
            }, {
                '$project': {
                    'duration':1,
                    'date':1,   
                    'food_preference': 1,
                    'FollowUpNotes': 1, 
                    'MedicalConditionNotes':1,
                    'notes': 1, 
                    'goal': 1, 
                    'mobile': 1, 
                    '_id': 0
                }
            }, {
                '$lookup': {
                    'from': 'Appointments', 
                    'localField': 'mobile', 
                    'foreignField': 'mobile', 
                    'pipeline': [
                        {
                            '$match': {
                                'isDeleted': {
                                    '$ne': 1
                                }
                            }
                        }, {
                            '$addFields': {
                                'date1': {
                                    '$toDate': '$date'
                                }, 
                                'matchDate': {
                                    '$toDate': datetime.now().strftime("%Y-%m-%d")
                                },
                                '_id':{
                                    '$toString':'$_id'
                                }
                            }
                        }, {
                            '$match': {
                                '$expr': {
                                    '$gte': [
                                        '$date1', '$matchDate'
                                    ]
                                }
                            }
                        }
                    ], 
                    'as': 'appointment'
                }
            }, {
                '$unwind': {
                    'path': '$appointment', 
                    'preserveNullAndEmptyArrays': True
                }
            }, {
                '$project':{
                    'appointment.date1':0,
                    'appointment.matchDate':0,
                }
            }
        ]
        print(arra,'oijhtyjnwiguwgfywf')
        data = list(cmo.finding_aggregate("users",arra))
        print(data,'======ddddddddddd=======')
        return jsonify({'msg':'Data get Successfully','data':data})


        


@user.route('/card',methods=['GET','POST','PUT','PATCH',"DELETE"])
@user.route('/card/<id>',methods=["GET",'POST','PUT','PATCH',"DELETE"])   
def card(id=None):
         if request.method=='GET': 
            arra=[
                {
                    '$match':{'isDeleted':{'$ne':1}}  
                }, {
                    '$addFields': {
                        '_id': {
                            '$toString': '$_id'
                        }
                    }
                }
            ]
             
            data=list(cmo.finding_aggregate("users",arra))
            return jsonify({'users':data})


@user.route('/feedback',methods=['GET',"POST","PUT",'PATCH','DELETE'])
@user.route('/feedback/<id>',methods=['GET',"POST","PUT",'PATCH','DELETE'])
@token_required
def get_feedback(current_user,id=None):
    if request.method == 'GET':
        arra=[
            {
                '$match': {
                    'isDeleted': {'$ne': 1}
                }
            }, {
                '$addFields': {
                    '_id': {
                        '$toString': '$_id'
                    }
                }
            }, {
                '$lookup': {
                    'from': 'users', 
                    'localField': 'mobile', 
                    'foreignField': 'mobile', 
                    'pipeline': [
                        {
                            '$match': {
                                'isDeleted': {
                                    '$ne': 1
                                }
                            }
                        }
                    ], 
                    'as': 'result'
                }
            }, {
                '$unwind': {
                    'path': '$result', 
                    'preserveNullAndEmptyArrays': True
                }
            }, {
                '$addFields': {
                    'assignMemberId': {
                        '$toObjectId': '$result.assignMemberId'
                    }
                }
            }, {
                '$lookup': {
                    'from': 'users', 
                    'localField': 'assignMemberId', 
                    'foreignField': '_id', 
                    'as': 'result'
                }
            }, {
                '$unwind': {
                    'path': '$result', 
                    'preserveNullAndEmptyArrays': True
                }
            }, {
                '$addFields': {
                    'memberName': '$result.fullname', 
                    'email': '$result.email'
                }
            }, {
                '$addFields': {
                    'assignMemberId': {
                        '$toString': '$assignMemberId'
                    }
                }
            }, {
                '$project': {
                    'username': 1, 
                    'comment': 1, 
                    'rating': 1, 
                    'mobile': 1, 
                    'memberName': 1, 
                    'email': 1, 
                    'date': 1, 
                    'memberNote': 1,
                    'assignMemberId':1,
                }
            }
        ]
        if current_user['role'] == "MEMBER":
            arra = arra + [
                {
                    '$match':{
                        'assignMemberId':current_user['_id']
                    }
                }
            ]
        if request.args.get("rating") and request.args.get("rating")!= 'null':
            arra = arra + [
                {
                    '$match':{
                       'rating':int(request.args.get("rating")) 
                    }
                }
            ]
        arra = arra + [
            {
                "$sort":{"_id":-1}
            }
        ]
        if request.args.get("limit"):
            arra.append({
                "$limit":int(request.args.get("limit"))
            })
        arra = arra + [
            {
                '$facet': {
                    'outputFieldN': [
                        {
                            '$group': {
                                '_id': None, 
                                'count': {
                                    '$sum': 1
                                }
                            }
                        }
                    ], 
                    'outputFieldN1': []
                }
            }, {
                '$unwind': {
                    'path': '$outputFieldN1', 
                    'preserveNullAndEmptyArrays': True
                }
            }, {
                '$addFields': {
                    'totalCount': {
                        '$arrayElemAt': [
                            '$outputFieldN', 0
                        ]
                    }
                }
            }, {
                '$addFields': {
                    'totalCount': '$totalCount.count'
                }
            }, {
                '$addFields': {
                    'outputFieldN1.count': '$totalCount'
                }
            }, {
                '$replaceRoot': {
                    'newRoot': '$outputFieldN1'
                }
            }
        ]
        print(arra,"arra==============")
        data=list(cmo.finding_aggregate("feedback",arra))
        return jsonify({'feedback':data})
    
    if request.method=='POST':
        if current_user["role"] == "USER":
            username = current_user['fullname']
            comment = request.form.get('comment')
            rating = request.form.get('rating')
            if not rating:
                return jsonify({'msg':'please provide rating','status':'false','statusCode':404}),404
            if rating.isdigit():
                rating=int(rating)
            else:
                return jsonify({"msg":'please provide integer value for rating',"status":'false','statusCode':404}),404
            data={

                'username':username,
                'comment':comment,
                'rating':rating,
                'date':datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                'createdBy':current_user["_id"],
                'role':current_user['roleId'],
                'mobile':current_user['mobile'],
                'email':current_user['email'],
            }
            updateBy = {
                'createdBy':current_user["_id"]
            }
            cmo.update("feedback",updateBy,data,True)
            return jsonify({'msg':'User Feedback Submitted Successfully','status':'true','statusCode':201}),201
        else:
            return jsonify({'msg':'You are not allowed to add feedback on this','status':'false','statusCode':400}),400
        
    if request.method == 'PUT':
        if id!=None:
            notes=request.form.get('memberNote')
            print(notes,'notes')
            data={
                'memberNote':notes
            }
            updateBy={'_id':ObjectId(id)}
            print(updateBy,'===========')
            cmo.update("feedback",updateBy,data,False)
            return jsonify({'msg':'Data updated Successfully'}),200
        else:
            return jsonify({'msg':'Unsuccessfully Updated'}),400
        
        
    # if request.method == "DELETE":
    #     if id!=None:
    #         cmo.deleteStatus("feedback", id)
    #         return (jsonify({"msg": "Document deleted successfully"})),200
    #     else:
    #         return (jsonify({'msg':'Unsuccessfully Updated'})),400


########-----------------------by shobhit ------------------------------------------------
@user.route('/feedbackSuperAdmin/<id>',methods=['GET',"POST","PUT",'PATCH','DELETE'])
@user.route('/feedbackSuperAdmin',methods=['GET',"POST","PUT",'PATCH','DELETE'])
def feedbackSuperAdmin(id=None):
    print(id,'iiididididiididi')
    if request.method == 'GET':
        # print(request.get_json('id'),'nnnnpppllkkjh')
        if id is not None:
            agr=[
                    {
                        '$match': {
                            'isDeleted': {
                                '$ne': 1
                            }
                        }
                    }, {
                        '$addFields': {
                            '_id': {
                                '$toString': '$_id'
                            }
                        }
                    }, {
                        '$lookup': {
                            'from': 'users', 
                            'localField': 'mobile', 
                            'foreignField': 'mobile', 
                            'pipeline': [
                                {
                                    '$match': {
                                        'isDeleted': {
                                            '$ne': 1
                                        }
                                    }
                                }
                            ], 
                            'as': 'result'
                        }
                    }, {
                        '$unwind': {
                            'path': '$result', 
                            'preserveNullAndEmptyArrays': True
                        }
                    }, {
                        '$addFields': {
                            'assignMemberId': {
                                '$toObjectId': '$result.assignMemberId'
                            }
                        }
                    }, {
                        '$match': {
                            'assignMemberId':ObjectId(id)
                        }
                    }, {
                        '$project': {
                            '_id': 1, 
                            'username': 1, 
                            'rating': 1, 
                            'mobile': 1, 
                            'comment': 1, 
                            'date': 1
                        }
                    }
                ]
            data=list( cmo.finding_aggregate('feedback',agr))
            print(data,'ppppppppppppppppp')
            return jsonify({'feedbackPopup':data})
        
        if id is None:
            agrr=[
                        {
                            '$match': {
                                'isDeleted': {
                                    '$ne': 1
                                }
                            }
                        }, {
                            '$addFields': {
                                '_id': {
                                    '$toString': '$_id'
                                }
                            }
                        }, {
                            '$lookup': {
                                'from': 'users', 
                                'localField': 'mobile', 
                                'foreignField': 'mobile', 
                                'pipeline': [
                                    {
                                        '$match': {
                                            'isDeleted': {
                                                '$ne': 1
                                            }
                                        }
                                    }
                                ], 
                                'as': 'result'
                            }
                        }, {
                            '$unwind': {
                                'path': '$result', 
                                'preserveNullAndEmptyArrays': True
                            }
                        }, {
                            '$addFields': {
                                'assignMemberId': {
                                    '$toObjectId': '$result.assignMemberId'
                                }
                            }
                        }, {
                            '$lookup': {
                                'from': 'users', 
                                'localField': 'assignMemberId', 
                                'foreignField': '_id', 
                                'as': 'result'
                            }
                        }, {
                            '$unwind': {
                                'path': '$result', 
                                'preserveNullAndEmptyArrays': True
                            }
                        }, {
                            '$addFields': {
                                'memberName': '$result.fullname', 
                                'email': '$result.email'
                            }
                        }, {
                            '$addFields': {
                                'assignMemberId': {
                                    '$toString': '$assignMemberId'
                                }
                            }
                        }, {
                            '$group': {
                                '_id': '$assignMemberId', 
                                'rating': {
                                    '$sum': '$rating'
                                }, 
                                'uniqueUsernames': {
                                    '$addToSet': '$username'
                                }, 
                                'memberName': {
                                    '$first': '$memberName'
                                }, 
                                'email': {
                                    '$first': '$email'
                                }
                            }
                        }, {
                            '$project': {
                                '_id': 1, 
                                # 'rating': 1, 
                                'usernameCount': {
                                    '$size': '$uniqueUsernames'
                                }, 
                                'memberName': 1, 
                                'email': 1, 
                                'averageRating': {
                                    '$divide': [
                                        '$rating', {
                                            '$size': '$uniqueUsernames'
                                        }
                                    ]
                                }
                            }
                        }
                    ]
            data=list(cmo.finding_aggregate('feedback',agrr))
            return jsonify({'feedback':data})



@user.route("/getBlogs",methods=['GET'])
@token_required
def getBlogs(current_user):
    if request.method == "GET":
        arra=[
            {
                '$match':{'isDeleted':{
                    '$ne':1
                }}
            },
            {
        '$addFields': {
            '_id': {
                '$toString': '$_id'
            },

        }
            }]
        respond=list(cmo.finding_aggregate("blog",arra))
        return jsonify({"msg":"Data get Successfully","data":respond})
    return jsonify({"msg":"Please! Login First"})

@user.route("/makeAppointment",methods=["POST","GET","PUT","DELETE"])
@token_required
def make_Appointment(current_user):
    if request.method == "POST":
        fullname=current_user["fullname"]
        date=request.form.get("date")
        time=request.form.get("time")
        memberId=request.form.get("memberId")
        memberName=request.form.get("memberName")
        phone=request.form.get('phone')
        body={
            "fullname":fullname,
            "phone":phone,
            "date_and_time":{"date":date,
            "time":time,
            },
            "memberName":memberName,
            "memberId":memberId,
            "userId":current_user["_id"]
        }
        updateBy={'_id':ObjectId(memberId)}
        cmo.insertion("Appointments",body)
        respond=cmo.update("users",updateBy,{'appointments':body},False)
        return jsonify({'msg':'Appointment set Successfully'})
    else:
        return jsonify({"msg":"Error"}),400

@user.route("/allMembers",methods=["POST","GET"])
@token_required
def AllMembers(current_user):
    if request.method=="GET":
        arr=[
            {
                '$match': {
                    'role': getRole("MEMBER"), 
                    'isDeleted': {
                        '$ne': 1
                    }
                }
            }, {
                '$addFields': {
                    'memberId': {
                        '$toString': '$_id'
                    },
                    '_id':{'$toString':'$_id'}
                }
            }, {
                '$project': {
                    'memberId': 1, 
                    '_id': 1, 
                    'fullname': 1, 
                    'email': 1
                }
            }
        ]
        respond=list(cmo.finding_aggregate("users",arr,True))
        return respond



# @user.route("/deleteAccount",methods=["POST","GET","PUT"])
@user.route("/deleteAccount/<id>",methods=["POST","GET","PUT"])
@token_required
def Account(current_user,id=None):
    if request.method == "PUT": 
        if id is not None:
            print(id,'----id-------')
            userId = request.form.get("userId")
            email_subject = 'For Delete Account.'
            otp = random.randint(1000, 9999)
            print(otp, 'otp')
            updateBy = {'_id': ObjectId(id)}
            send_email('meyeta2789@fincainc.com', email_subject, str(otp))
            respond = cmo.update("users", updateBy, {'otp': str(otp)}, upst=False)
            return {'msg':'Otp send successfully!',"status":200},200

    if request.method == 'POST':
        if id is not None:
            otp=request.json.get('otp')
            updateBy = {'_id': ObjectId(id)}
            if otp:
                arra = [
                    {
                        '$match':{
                            '_id':ObjectId(id)
                        }
                    }
                ]
                response = list(cmo.finding_aggregate("users",arra))
                if (len(response)):
                    dbotp = response[0]['otp']
                    if int(otp) == int(dbotp):
                        updateData = {
                            'isDeleted':1
                        }
                        cmo.update("users",updateBy,updateData,False)
                        return jsonify({
                            "msg":'Data Deleted Successfully',
                            "status":200,

                        }),200
                    else:
                        return jsonify({
                            'msg':"otp is not match",
                            "status":400
                        }),400
                else:
                    return jsonify({
                        'msg':'unique Id is not Found'
                    }),400




        

            otp=request.form.get('otp')
            if not otp:
                return jsonify({"msg":'please enter otp',"status":'false'}),404
            if int(otp)==current_user["otp"]:
                respond=cmo.deleteStatus("users",id)
                return jsonify({'msg':'User Deleted Successfully','status':'true','statusCode':200}),200
            else:
                return jsonify({"msg":"Please enter a valid otp",'status':'false'}),404
        pass
        userId=request.form.get("userId")
        if not userId:
            return jsonify({"msg":"please enter userId","status":"false"}),404
        if current_user["_id"] == userId:
            otp=random.randint(1000, 9999)
            updateBy={'_id':ObjectId(userId)}
            respond=cmo.update("users",updateBy,{'otp':otp},False)
            arra = [
                {
                    '$match':{
                        'isDeleted':{'$ne':1},
                        '_id':ObjectId(userId)
                    }
                }, {
                    '$addFields':{
                        '_id':{
                            '$toString':'$_id'
                        }
                    }
                }
            ]
            data = list(cmo.finding_aggregate("users",arra))
            return jsonify({'msg':'Success','status':'true','otp':otp,'statusCode':200}),200
        else:
            return jsonify({"msg":"Please enter a valid userId",'status':'false','statusCode':404}),404
    else:
        return jsonify({'msg':'This method is not allowed','status':'false','statusCode':404}),404
    

@user.route("/reportBug",methods=['POST','GET'])
@user.route("/reportBug/<id>",methods=['POST','GET','PUT','PATCH','DELETE'])
@token_required
def reportBug(current_user,id=None):
    if request.method == 'GET':
        arr=[
            {
                '$addFields': {
                    '_id': {
                        '$toString': '$_id'
                    }
                }
            }, {
                '$addFields': {
                    'reportedBy': {
                        '$toObjectId': '$reportedBy'
                    }
                }
            }, {
                '$lookup': {
                    'from': 'users', 
                    'localField': 'reportedBy', 
                    'foreignField': '_id', 
                    'as': 'data'
                }
            }, {
                '$unwind': {
                    'path': '$data', 
                    'preserveNullAndEmptyArrays': True
                }
            }, {
                '$addFields': {
                    'fullname': '$data.fullname', 
                    'email': '$data.email', 
                    'mobile': '$data.mobile', 
                    'userId': '$data._id'
                }
            }, {
                '$addFields': {
                    'reportedBy': {
                        '$toString': '$reportedBy'
                    }, 
                    'userId': {
                        '$toString': '$userId'
                    }
                }
            }, {
                '$project': {
                    'data': 0
                }
            }
        ]
        respond=list(cmo.finding_aggregate("Bugs",arr))
        return jsonify({"msg":"Data get Successfully","data":respond,"status":"true"}),200
    if request.method == "POST":
        details=request.form.get('details')
        if not details:
            return jsonify({'msg':"please write your issues",'status':'false'}),404
        body={
            'details':details,
            'reportedBy':current_user['_id'],
        }
        respond=cmo.insertion('Bugs',body)
        return jsonify({'msg':'Bug reported successfully','status':'true'}),201

    


@user.route("/buyPlan",methods=["GET","POST"])
@user.route("/buyPlan/<id>",methods=["GET","POST","PUT",'PATCH','DELETE'])
@token_required
def buy_Plan(current_user,id=None): 
    if request.method == "POST":
        planName=request.form.get("planName")
        if not planName:
            return jsonify({"msg":'please enter planName','status':False}),404
        planDuration=request.form.get("planDuration")
        if not planDuration:
            return jsonify({"msg":'please enter planDuration','status':False}),404
        couponCode=request.form.get("couponCode")
        if couponCode:
            # return jsonify({"msg":'please enter couponCode','status':False}),404
            arr=[
                {
                    '$match': {
                        'status': 'true', 
                        'isDeleted': {
                            '$ne': 1
                        }, 
                        'couponCode': couponCode
                    }
                }, {
                    '$addFields': {
                        '_id': {
                            '$toString': '$_id'
                        }
                    }
                }
            ]
            coupons=list(cmo.finding_aggregate("coupons",arr))
            coupons = coupons[0]
            if len(coupons) == 0:
                return jsonify({"msg":'coupon is invalid','Status':False,"statusCode":404}),404
        arr2=[
            {
                '$match': {
                    'isDeleted': {
                        '$ne': 1
                    }, 
                    'planName': planName
                }
            }, {
                '$addFields': {
                    '_id': {
                        '$toString': '$_id'
                    }
                }
            }
        ]
        plans=list(cmo.finding_aggregate("plans",arr2))
        plans=plans[0]
        if couponCode and len(coupons)>0:
            finalPrice = int(plans['price'])*int(planDuration)
            finalAmount = finalPrice - (finalPrice*int(coupons['discount']))/100
            return jsonify({'msg':'success and with coupons','payment':finalAmount,'status':True}) 
        else:
            finalPrice = int(plans['price'])*int(planDuration)
            return jsonify({'msg':'success and withoutcoupons','payment':finalPrice,'status':True}) 
    



@user.route("/makePost",methods=["GET","POST"])
@token_required
def post(current_user):
    if request.method == "POST":
        image = request.files.get("img")
        if not image:
            return jsonify({'msg':'please upload a file','status':'false','statusCode':404}),404
        description=request.form.get("description")
        if image:
            print(image)
            print(image.filename)
            ext = str(image.filename).split(".")[-1]
            img_name = str(unique_timestamp()) + "." + ext
            path = os.path.join(UPLOAD_FOLDER, img_name)
            image.save(path)
            print(ext)
            print(img_name)
            print(path)
        
        data = {
            'img':path if image else None,
            'description':description,
            'role':current_user['role'],
            'fullname':current_user['fullname'],
            'createdBy':current_user['_id']
        }
        cmo.insertion("makePost", data)
        return jsonify({"msg": "post submitted successfully",'status':True,"statusCode":201}),201
    
# @user.route("/updateExcersize/<name>",methods=["GET","POST"])
# @token_required
# def excersize(current_user,name):
#     if request.method == "POST":
#         excersize = name
#         return jsonify({"msg":'excersize update is successfully'})

@user.route("/getPlan",methods=['GET','POST'])
@token_required
def getplan(current_user):
    if request.method == "GET":
        arra = [
            {
                '$match': {
                    'isDeleted': {
                        '$ne': 1
                    }
                }
            }, {
                '$addFields': {
                    '_id': {
                        '$toString': '$_id'
                    }
                }
            }, {
                '$project': {
                    '_id': 0, 
                    'createdAt': 0, 
                    'createdBy': 0
                }
            }, {
                '$sort': {
                    'price': 1
                }
            }
        ]
        allData = list(cmo.finding_aggregate('makePlan',arra))
        return jsonify({"msg":'data get successfully',"data":allData,'status':'true','statusCode':200}),200

@user.route("/history",methods=['GET','POST'])
@token_required
def history(current_user):
    if request.method == "GET":
        arra = [
            {
                '$match': {
                    'isDeleted': {
                        '$ne': 1
                    }, 
                    'userId': current_user['_id']
                }
            }, {
                '$addFields': {
                    '_id': {
                        '$toString': '$_id'
                    }
                }
            }
        ]
        allData = list(cmo.finding_aggregate("Appointments",arra))
        return jsonify({"msg":'data get successfuly','status':'true','data':allData,'statusCode':200}),200



@user.route("/updateExcersize",methods=['GET','POST'])
def updateexcersize():

    if request.method == "POST":

        excersize = request.form.get("excersize")
        uniqueId = request.form.get("userId")

        data = {
            'excersize':excersize
        }
        updateBy = {
            '_id':ObjectId(uniqueId)
        }

        response = cmo.update("users",updateBy,data)
        return jsonify({"msg":"Excersize updated successfully",'status':'true','statusCode':'200'}),200
    
     
    

    
    

@user.route("/updateDiet",methods=['GET','POST'])
def excersize():
    if request.method == "POST":

        diet = request.form.get("diet")
        uniqueId = request.form.get("userId")

        data = {
            'diet':diet
        }
        updateBy = {
            '_id':ObjectId(uniqueId)
        }

        response = cmo.update("users",updateBy,data)
        return jsonify({"msg":"Diet updated successfully",'status':'true','statusCode':'200'}),200
    
# print(unique_timestamp(),"unique_timestamp()unique_timestamp()unique_timestamp()")

@user.route("/attendance" , methods=['GET','POST','PUT'])
@token_required
def loginTime(current_user):
    # print(current_user,'current_usercurrent_usercurrent_user')

    if request.method == "POST":
        data = request.get_json()  
        action = data.get('action')
             
        unique_timestamp()
        if not action or action.lower()  not in ['login',"logout"]:
            print("========================")
            return jsonify({"Provide Valid Data"}),400
        data={
                'userId':ObjectId(current_user['_id']),
                "status": action.lower(),
                
            }
        

        aggr=[
                    {
                        '$addFields': {
                            'currentDay': {
                                '$toDate': unique_timestamp()
                            }, 
                            'dbDay': {
                                '$toDate': {
                                    '$toDouble': '$login'
                                }
                            }
                        }
                    }, {
                        '$addFields': {
                            'currentDay': {
                                '$dateToString': {
                                    'format': '%Y-%m-%d', 
                                    'date': {
                                        '$toDate': '$currentDay'
                                    }
                                }
                            }, 
                            'dbDay': {
                                '$dateToString': {
                                    'format': '%Y-%m-%d', 
                                    'date': {
                                        '$toDate': '$dbDay'
                                    }
                                }
                            }
                        }
                    }, {
                        '$match': {
                            'userId': ObjectId('6593e76018806c38b4accda3')
                        }
                    },
                    {
                        "$sort":{
                            "_id":-1
                        }
                    }
                ]
        print(aggr)
        loginData = list(cmo.finding_aggregate('Attendance',aggr))

        if data['status'] == 'login':  
            
            if len(loginData):
                if loginData[0].get("dbDay")==loginData[0].get("currentDay"):

                    return {
                        'msg':'You are already loged in!'
                    }
            data['login'] =unique_timestamp()
            
            insert_data=cmo.insertion('Attendance',data)
            print(insert_data,'---------idid-----------')
            return {
                'msg':'You are login successfully!','status':200
            }
        elif data['status'] =='logout':
            LOGOUT=loginData[0]['_id'] if len(loginData) else current_user['_id']
            if loginData[0].get("dbDay")==loginData[0].get("currentDay"):
                cmo.update('Attendance',{"_id":ObjectId(LOGOUT)},{"logout":unique_timestamp()})
                return {
                        'msg':'You are  logout!','status':200
                    }          
        # print('Received action:', action)
        return jsonify({"message": "Success"})
    
    if request.method == 'PUT':
        data = request.get_json() 
        print('fghjkjgfgjk',data['action']) 
        action = data.get('action')
        if action:
            day=action['days']
            starttime=action['starttime']
            endtime=action['endtime']
            data={
                'userId':ObjectId(current_user['_id']),
                'day':day,
                'starttime':starttime,
                'endtime':endtime
            }
            cmo.insertion('Attendance',data)         
            print('updated')
            return {'msg':'updated successfully!','status':200}
        else:
            return {'msg':'can not updated successfully!'}




    if request.method == "GET":
        agrr = [

            {
            '$sort': {'login': -1}  
        },
         {
        '$match': {
            'userId':ObjectId(current_user['_id'])
        }
    },
            {
                '$project': {
                    '_id': 0, 
                    'login': {
                        '$toDate': '$login'
                    }, 
                    'logout': {
                        '$toDate': '$logout'
                    },
                    'day':1,
                    'starttime':1,
                    'endtime':1
                }
            }
        ]
        try:
            data = list(cmo.finding_aggregate('Attendance', agrr))
            print("Data retrieved successfully:", data)
          
            return {'data':data,'status':200}
        except Exception as e:
            print("Error occurred while fetching data:", e)
            return {"error": str(e)}
    else:
        return {"error": "Unsupported method"}
    
# #dfghjkl; nm,ghjkh
# @user.route("/Notification",methods=["POST","GET"])
# @token_required
# def Notification(current_user):
#     if request.method=='GET':
#         agrr=[
#                 {
#                     '$match': {
#                         'assignMemberId':current_user['_id'], 
#                         'assignedstatus': {
#                             '$ne': False
#                         }
#                     }
#                 }, {
#                     '$project': {
#                         '_id': 0, 
#                         'assign': 1, 
#                         'fullname': 1
#                     }
#                 }
#             ]
#         findData=cmo.finding_aggregate('users',agrr)
#         return jsonify({'findData':list(findData),'status':200})
#         # return {'msg':'successfully get data!'}
#     else:
#         return {'msg':'Wrong Method!'}
    












@user.route("/downloadBlogApi/<id>", methods=["POST", "GET"])
@token_required
def downloadBlogApi(current_user, id):
    if request.method == "GET":
        if id is not None:
            arra = [
                {
                    '$match': {'isDeleted': {'$ne': 1}}
                },
                {
                    '$addFields': {
                        '_id': {
                            '$toString': '$_id'
                        },
                    }
                }
            ]
            respond = list(cmo.finding_aggregate("blog", arra))
            json_data = json.dumps(respond, indent=4)
            output = BytesIO()
            output.write(json_data.encode('utf-8'))
            output.seek(0)
            response = make_response(send_file(output, download_name="blog_data.json", as_attachment=True))
            response.headers["Content-Type"] = "application/json"
            return {"download":response}
        return jsonify({"msg": "Please! Login First"})


@user.route("/NotificationApi/<id>",methods=["POST","GET"])
@token_required
def NotificationApi(current_user,id): 
    # print(current_user,'----------current_user-------------')
    if request.method=='GET':
        curr_id=ObjectId(current_user['_id'])
        if id is not None:
            agrr=[
                        {
                            '$addFields': {
                                'role': {
                                    '$toObjectId': '$role'
                                }
                            }
                        }, {
                            '$lookup': {
                                'from': 'userRole', 
                                'localField': 'role', 
                                'foreignField': '_id', 
                                'pipeline': [
                                    {
                                        '$match': {
                                            'role': 'USER'
                                        }
                                    }
                                ], 
                                'as': 'result'
                            }
                        }, {
                            '$match': {
                                'result': {
                                    '$ne': []
                                }, 
                                '_id': curr_id
                            }
                        }, {
                            '$project': {
                                "_id":0,
                                'assign': 1
                            }
                        }
                    ]
            
            # +[
            #             {
            #                 '$match': {
            #                     'mobile': '9170336377', 
            #                     'userName': 'Shobhit Pal'
            #                 }
            #             }, {
            #                 '$addFields': {
            #                     'appointmentStatus': {
            #                         '$ifNull': [
            #                             '$completionStatus', ''
            #                         ]
            #                     }
            #                 }
            #             }, {
            #                 '$project': {
            #                     'userName': 1, 
            #                     'appointmentStatus': 1
            #                 }
            #             }
            #         ]
            findData=cmo.finding_aggregate('users',agrr)
            return jsonify({'findData':list(findData),'status':200})
            # return {'msg':'successfully get data!'}
        else:
            return {'msg':'Wrong Method!'}