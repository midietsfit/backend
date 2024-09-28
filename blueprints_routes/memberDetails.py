from base import *
import os
import jwt
import razorpay
from common.mongoDb_operation import unique_timestamp
from datetime import datetime, timedelta
member=Blueprint("member_data",__name__)
UPLOAD_FOLDER = os.path.join("uploads", "image")   

@member.route("/uploads/<subDir>/<fileName>")
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

@member.route("/test")
@token_required
def testing(current_user):
    return jsonify({"Hello token testing":current_user})

@member.route('/member',methods=['GET','POST','PUT','PATCH',"DELETE"])
@member.route('/member/<id>',methods=["GET",'POST','PUT','PATCH',"DELETE"])
def memberDetails(id=None):
    if request.method == 'GET':
        # arra=[
        #     {
        #         '$match': {
        #             'isDeleted': {
        #                 '$ne': 1
        #             }, 
        #             'role': {
        #                 '$eq':getRole("MEMBER")
        #             }  
        #         }
        #     }, {
        #         '$addFields': {
        #             '_id': {
        #                 '$toString': '$_id'
        #             },
        #             'memberId':{
        #                 '$toString': '$_id'
        #             }
        #         }
        #     }, {
        #         '$lookup': {
        #             'from': 'feedback', 
        #             'localField': '_id', 
        #             'foreignField': 'memberId', 
        #             'pipeline': [
        #                 {
        #                     '$addFields': {
        #                         '_id': {
        #                             '$toString': '$_id'
        #                         }
        #                     }
        #                 }, {
        #                     '$group': {
        #                         '_id': None, 
        #                         'users': {
        #                             '$sum': 1
        #                         }, 
        #                         'rating': {
        #                             '$sum': {
        #                                 '$toInt': '$rating'
        #                             }
        #                         }
        #                     }
        #                 }, {
        #                     '$addFields': {
        #                         'totalRating': {
        #                             '$multiply': [
        #                                 '$users', 10
        #                             ]
        #                         }
        #                     }
        #                 }, {
        #                     '$addFields': {
        #                         'avg': {
        #                             '$multiply': [
        #                                 {
        #                                     '$divide': [
        #                                         '$rating', '$totalRating'
        #                                     ]
        #                                 }, 10
        #                             ]
        #                         }
        #                     }
        #                 }
        #             ], 
        #             'as': 'user_rating'
        #         }
        #     }, {
        #         '$project': {
        #             'appointments': 0
        #         }
        #     }
        # ]


        arra=[
            {
                '$match': {
                    'isDeleted': {
                        '$ne': 1
                    }, 
                    'role': {
                        '$eq':getRole("MEMBER")
                    }  
                }
            }, {
                '$addFields': {
                    '_id': {
                        '$toString': '$_id'
                    }, 
                    'memberId': {
                        '$toString': '$_id'
                    }
                }
            }, {
                '$lookup': {
                    'from': 'feedback', 
                    'localField': '_id', 
                    'foreignField': 'memberId', 
                    'pipeline': [
                        {
                            '$addFields': {
                                '_id': {
                                    '$toString': '$_id'
                                }
                            }
                        }, {
                            '$group': {
                                '_id': None, 
                                'users': {
                                    '$sum': 1
                                }, 
                                'rating': {
                                    '$sum': {
                                        '$toInt': '$rating'
                                    }
                                }
                            }
                        }, {
                            '$addFields': {
                                'totalRating': {
                                    '$multiply': [
                                        '$users', 10
                                    ]
                                }
                            }
                        }, {
                            '$addFields': {
                                'avg': {
                                    '$multiply': [
                                        {
                                            '$divide': [
                                                '$rating', '$totalRating'
                                            ]
                                        }, 10
                                    ]
                                }
                            }
                        }
                    ], 
                    'as': 'user_rating'
                }
            }, {
                '$project': {
                    'appointments': 0
                }
            }, {
                '$lookup': {
                    'from': 'meals', 
                    'let': {
                        'uId': {
                            '$toString': '$_id'
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


        print(arra,"arraarra")

        data=list(cmo.finding_aggregate("users",arra))
        return jsonify({"data":data}),200
    
    if request.method == 'POST':
        body=request.get_json()
        arr=[
            {
                '$match': {
                    'isDeleted': {'$ne': 1}, 
                    'role': {'$eq':getRole("MEMBER")},
                    'email':{'$eq':body['email']}, 
                }
            }, {
                '$addFields': {
                    '_id': {'$toString': '$_id'},
                }
            }
        ]
        data=list(cmo.finding_aggregate("users",arr))
        if len(data):
            return jsonify({"msg":"This Email is Already exist, Use Another Email",}),404
        else:
            body['role'] = getRole("MEMBER")
            body.setdefault('status',True)
            respond=(cmo.insertion("users",body))
            return jsonify({'msg':'Data Added Successfully'}),201
        
    if request.method == "PUT":
        if id!=None:
            body=request.get_json()
            updateBy={'_id':ObjectId(id)}
            respond=cmo.update("users",updateBy,body,False)
            return jsonify({'msg':'Updated Successfully'}),200
        else:
            return jsonify({'msg':'Unsuccessfully Updated'}),404
        
    if request.method == "DELETE":
        if id!=None:
            respond=cmo.deleteStatus("users",id)
            return jsonify({'msg':'Successfully Deleted'}),200
        else:
            return jsonify({'msg':'Unsuccessfully Updated'}),404
        

# @member.route('/spice/update_publish', methods=['PATCH'])
# def update_published():
#     if request.method == "PATCH":
#         request_data = request.json
#         publish = request_data.get('publish')
#         id = request_data.get('id')

#         if publish is not None:

#             product = cmo.updating("Dishes", {"_id": ObjectId(id)}, {"publish": publish}, False)

#             return respond(product)

#     return respond({'state': -1, 'msg': 'Invalid request', 'data': []})


@member.route("/Plans",methods=["GET","POST"])
@member.route("/Plans/<id>",methods=["GET","POST","PUT","DELETE"])
@token_required
def plans(current_user,id=None):
    if request.method == "GET":
        arr=[{
                    '$match':{'isDeleted':{
                        '$ne':1
                    },
                    }
                },
                {
            '$addFields': {
                '_id': {
                    '$toString': '$_id'
                }
            }
        }]

        Response=list(cmo.finding_aggregate("plans",arr))
        return ({'data':Response})
    if request.method == "POST":
        planName=request.form.get("planName")
        arr=[
    {
        '$match': {
            'isDeleted': {
                '$ne': 1
            }, 
            'planName': {
                '$eq':planName
            }
        }
    }, {
        '$addFields': {
            '_id': {
                '$toString': '$_id'
            }
        }
    }
]
        Response=list(cmo.finding_aggregate("plans",arr))
        datas={
            'planName':planName,
            "createdBy":current_user['_id']
        }
        if len(Response):
            return jsonify({'msg':'Plan Name Aready exists'})
        else:
            respond=cmo.insertion("plans",datas)
            return jsonify({'msg':'Plan created Successfully'})
        
    if request.method == "PUT":
        if id!=None:
            planName=request.form.get('planName')
            updateBy={'_id':ObjectId(id)}

            respond=cmo.update("plans",updateBy,{'planName':planName},False)
            return jsonify({'msg':'Updated Successfully'})
        else:
            return jsonify({'msg':'Unsuccessfully Updated'})
    if request.method == "DELETE":
        if id!=None:
            respond=cmo.deleteStatus("plans",id)
            return jsonify({'msg':'Successfully Deleted'})
        else:
            return jsonify({'msg':'Unsuccessfully Updated'})
        


@member.route("/BuyPlans",methods=["GET","POST"])   
def BuyPlans(id=None):
    if request.method=='GET':
        arra=[
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
            }, 
        
            {
                '$lookup': {
                    'from': 'plans', 
                    'localField': 'planName',
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
                    'Nameplan': '$result.planName'
                }
            }, {
                '$project': {
                    '_id': 0, 
                    'Nameplan': 1
                }
            }
        ]
        data=list(cmo.finding_aggregate("plansBuy",arra))
        return jsonify({'data':data})
    


# @member.route("/BuyPlans",methods=["GET","POST"])   
# @member.route("/BuyPlans/<planName>",methods=["GET","POST"])   
# def BuyPlan(id=None,planName=None):
#     if request.method=='GET':
#         arr2=[{
#         '$match': {
#             'isDeleted': {
#                 '$ne': 1
#             },
#             'planName':planName
#         }
#         }, {
#         '$addFields': {
#             '_id': {
#                 '$toString': '$_id'
#             }
#         }
#             }]
#         plans=list(cmo.finding_aggregate("plans",arr2))
#      
#         return jsonify({'plans':plans})
     
        
@member.route('/dropdownPlan',methods=["GET","POST"])
@member.route('/dropdownPlan/<id>',methods=["GET","POST","DELETE","PATCH","PUT"])        
# @token_required
def dropdownPlan(id=None):
    if request.method=="GET":
        arra=[
    {
        '$addFields': {
            '_id': {
                '$toString': '$_id'
            }
        }
    }, {
        '$project': {
            '_id': 0, 
            'planName': 1
        }
    }
]
        data=list(cmo.finding_aggregate("plans",arra))
    
        return jsonify({'data':data})


@member.route('/createPlan',methods=["GET","POST"])
@member.route('/createPlan/<id>',methods=["GET","POST","DELETE","PATCH","PUT"])
@token_required
def createPlan(current_user,id=None):
    if request.method == 'GET':
        arra=[
            {
                '$match': {
                    'isDeleted': {'$ne': 1}, 
                    'createdBy': current_user['_id'],
                }
            }, {
                '$addFields': {
                    '_id': {
                        '$toString': '$_id'
                    }
                }
            }
        ]
        data=list(cmo.finding_aggregate("plans",arra))
        return jsonify({'data':data})
    
    if request.method == "POST":
        username=current_user["fullname"]
        email=current_user['email']
        planName=request.form.get("planName")
        duration=int(request.form.get("duration"))
        price=int(request.form.get("price"))
        discount=int(request.form.get("discount"))
        currentDatetime = str(datetime.now())
        parsed_datetime = datetime.fromisoformat(currentDatetime.replace('Z', '+00:00'))
        formatted_date = parsed_datetime.strftime("%d-%b-%Y")
        formatted_time = parsed_datetime.strftime("%H:%M")
        timeDate=(formatted_date + " " + formatted_time)
        totalPrice = price*duration
        finalAmount = (totalPrice - (totalPrice * discount * 0.01))
        finalAmount = round(finalAmount)
        body={
            "username":username,
            'email':email,
            "planName":planName,
            "duration":duration,
            "price":price,
            "discount":discount,
            "finalAmount":finalAmount,
            "timeDate":timeDate,
            "createdBy":current_user['_id'],
        }
        Response=cmo.insertion("plans",body)
        return jsonify({'msg':"Successfully inserted data"})
    
    if request.method == "PUT":
        if id!=None:
            username=current_user["fullname"]
            planName=request.form.get("planName")
            duration=request.form.get("duration")
            price=request.form.get("price")
            discount=request.form.get("discount")
            totalPrice = int(price)*int(duration)
            finalAmount= (totalPrice- (totalPrice * int(discount) / 100))
            body={
            "username":username,
            "planName":planName,
            "duration":duration,
            "price":price,
            "discount":discount,
            "finalAmount":finalAmount,
            }
            updateBy={'_id':ObjectId(id)}
            cmo.update("plans",updateBy,body,False)
            return jsonify({'msg':"Successfully updated data"})
        else:
            return jsonify({'msg':'Unsuccessfully Updated'})
        
    if request.method == "DELETE":

        if id!=None:           
            respond=cmo.deleteStatus("plans",id)
            return jsonify({'msg':'Successfully Deleted'})
        else:
            return jsonify({'msg':'Unsuccessfully Updated'})

# @member.route('/Blogs',methods=["GET","POST"])
# @member.route('/Blogs/<id>',methods=['GET',"POST",'PUT','PATCH','DELETE'])
# @token_required
# def Blogs(current_user,id=None):
#     if request.method == "GET":
#         arra=[
#             {
#                 '$match':{'isDeleted':{
#                     '$ne':1
#                 }}
#             },
#             {
#         '$addFields': {
#             '_id': {
#                 '$toString': '$_id'
#             }
#         }
#             }]
# 
#         data=list(cmo.finding_aggregate("blog",arra))
#   
#         return jsonify({'data':data})
#     if request.method == "POST":
#         username=current_user['fullname']
#         blogTitle = request.form.get("blogTitle")
#         description = request.form.get("description")
#         Share = request.form.get("Share")
#         date = request.form.get("date")
#         image = request.files.get("img")
#         if image:
#             ext = str(image.filename).split(".")[-1]
#             img_name = str(unique_timestamp()) + "." + ext
#             path = os.path.join(UPLOAD_FOLDER, img_name)
#      
#             image.save(path)
#         data = {
#             "blogTitle": blogTitle,
#             "description": description,
#             "img": path,
#             "date": date,
#             "Share": Share,
#         }
#     
#         cmo.insertion("blog", data)
#         aggr = [{"$addFields": {"_id": {"$toString": "$_id"}}},]
#         location = list(cmo.finding_aggregate("blog", aggr))
#     
#         return jsonify({"msg": "blog submitted successfully", "data": location}), 201
#     if request.method == "PUT":
#         blogTitle = request.form.get("blogTitle")
#         description = request.form.get("description")
#         date = request.form.get("date")
#         Share = request.form.get("Share")
#         feedback = request.form.get("feedback")
#         image = request.files.get("img")
#         path = None 
#         if image:
#             ext = str(image.filename).split(".")[-1]
#             img_name = str(unique_timestamp()) + "." + ext
#             path = os.path.join(UPLOAD_FOLDER, img_name)
#             image.save(path)

#         data = {
#             "blogTitle": blogTitle,
#             "description": description,
#             "date": date,
#             "img": path,
#             "Share": Share,
#         }
#         updateBy={'_id':ObjectId(id)}
#         MSG = cmo.update("blog", updateBy, data, False)
#         return (jsonify({"msg": "blog data is updated successfully"}))
#     if request.method == "DELETE":
#         if id!=None:
#             cmo.deleteStatus("blog", id)
#             return (jsonify({"msg": "Document deleted successfully"}))
#         else:
#             return (jsonify({'msg':'Unsuccessfully Updated'}))
        
@member.route('/Blogs',methods=["GET","POST"])
@member.route('/Blogs/<id>',methods=['GET',"POST",'PUT','PATCH','DELETE'])
@token_required
def Blogs(current_user,id=None):
    if request.method == "GET":
        arra=[
            {
                '$match': {
                    'isDeleted': {
                        '$ne': 1
                    }, 
                }
            }, {
                '$addFields': {
                    '_id': {'$toString': '$_id'},
                }
            }
        ]
        data=list(cmo.finding_aggregate("blog",arra))
        return jsonify({'data':data})
    
    if request.method == "POST":
        blogTitle = request.form.get("blogTitle")
        description = request.form.get("description")
        image = request.files.get("img")
        print(image,'imageimageimageimageimage')

        if image:
            ext = str(image.filename).split(".")[-1]
            img_name = str(unique_timestamp()) + "." + ext
            path = os.path.join(UPLOAD_FOLDER, img_name)
            image.save(path)
            # print(path,'----------path------------')

        data = {
            "blogTitle": blogTitle,
            "description": description,
            "img": path if image else None,
            'date':datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            'roleId':current_user['roleId'],
            'role':current_user['role'],
            'createdBy':current_user['_id'],
            'fullname':current_user['fullname'],
            'mobile':current_user['mobile'],
            'email':current_user['email'],
        }
        data=cmo.insertion("blog", data)
        print(data,'ddadadadadaddadadadadad')
        return jsonify({"msg": "blog submitted successfully",'status':'true'}),201


    if request.method == "PUT":
        blogTitle = request.form.get("blogTitle")
        description = request.form.get("description")
        image = request.files.get("img")
        date = request.form.get("date")
        Share = request.form.get("Share")
        feedback = request.form.get("feedback")

        data = {}
        if blogTitle:
            data['blogTitle']=blogTitle
        if description:
            data['description']=description
        if date:
            data['date']=date
        if Share:
            data['Share']=Share
        if feedback:
            data['feedback']=feedback
        if image:
            ext = str(image.filename).split(".")[-1]
            img_name = str(unique_timestamp()) + "." + ext
            path = os.path.join(UPLOAD_FOLDER, img_name)
            image.save(path)
            data['img']=path
        updateBy={'_id':ObjectId(id)}
        MSG = cmo.update("blog", updateBy, data, False)
        return (jsonify({"msg": "blog data is updated successfully"}))
    if request.method == "DELETE":
        if id!=None:
            cmo.deleteStatus("blog", id)
            return (jsonify({"msg": "Document deleted successfully"}))
        else:
            return (jsonify({'msg':'Unsuccessfully Updated'}))
        

@member.route("/appointments",methods=["GET","POST",'PUT','POST','DELETE'])
@member.route("/appointments/<id>",methods=["GET","POST",'PUT','POST','DELETE'])
@token_required
def Appointments(current_user,id=None):
    if request.method == "GET":
        arra=[
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
                    }, 
                    'sortdate': {
                        '$dateFromString': {
                            'dateString': '$date'
                        }
                    }, 
                    'date': {
                        '$dateToString': {
                            'format': '%d-%m-%Y', 
                            'date': {
                                '$toDate': '$date'
                            }
                        }
                    }
                }
            }, {
                '$sort': {
                    'sortdate': -1
                }
            }, {
                '$project': {
                    'sortdate': 0
                }
            }
        ]
        if current_user['role'] == "MEMBER":
            arra = arra + [
                {
                    '$match':{
                        'memberId':current_user['_id']
                    }
                }
            ]
        if current_user['role'] == "USER":  
            arra = arra + [
                {
                    '$match':{
                        'mobile':current_user['mobile']
                    }
                }
            ]
        respond=list(cmo.finding_aggregate("Appointments",arra,sort=False))
        return jsonify({"data":respond})
    

    if request.method == "POST":
        

        if current_user['role'] == "MEMBER":
            data1 = request.form.get("fullname")
            data2 = request.form.get('datetime')
            data1 = data1.split("||")
            data2 = data2.split("T")
            fullname = data1[0]
            mobile = data1[1]
            date = data2[0]
            time = data2[1]
            # print(fullname,"fullname")
            # print(mobile,"mobile")
            # print(date,"date")
            # print(time,"time")
            data = {
                'userName':fullname,
                'mobile':mobile,
                'memberName':current_user['fullname'],
                'memberEmail':current_user['email'],
                'date':date,
                'time':time,
                'memberId':current_user["_id"]
            }
            # updateBy = {
            #     'mobile':mobile,
            #     'memberEmail':current_user['email']
            # }
            # cmo.update("Appointments",updateBy,data,True)
            cmo.insertion("Appointments",data)
            return jsonify({'msg':'Data Added Successfully'}),201
        
        if current_user['role'] == "SUPER_ADMIN":
            user = request.form.get('fullname')
            member = request.form.get("member")
            data = request.form.get("datetime")
            user = user.split("||")
            member = member.split("||")
            data = data.split("T")
            fullname = user[0].strip()
            mobile = user[1].strip()
            memberName = member[0].strip()
            memberEmail = member[1].strip()
            memberId = member[2].strip()
            date = data[0]
            time = data[1]
            data = {
                'userName':fullname,
                'mobile':mobile,
                'memberName':memberName,
                'memberEmail':memberEmail,
                'date':date,
                'time':time,
                'memberId':memberId
            }
            cmo.insertion("Appointments",data)
            return jsonify({'msg':'Data Added Successfully'}),201
        
    if request.method == "PUT":
        if id!=None:
            updateBy = {
                    '_id':ObjectId(id)
                }
            data = request.json
            completion_status = data.get('completionStatus', '') 
            # completion_status = request.args.get('completion')
            if len(completion_status)>0:
                if completion_status == 'Done':
                    data={
                        'completionStatus':completion_status
                    }
                    response=cmo.update("Appointments",updateBy,data,False)
                    return {'response':response}
        
            if current_user['role'] == "SUPER_ADMIN":
                user = request.form.get('fullname')
                member = request.form.get("member")
                data = request.form.get("datetime")
                user = user.split("||")
                member = member.split("||")
                data = data.split("T")
                fullname = user[0].strip()
                mobile = user[1].strip()
                memberName = member[0].strip()
                memberEmail = member[1].strip()
                memberId = member[2].strip()
                date = data[0]
                time = data[1]
                data = {
                    'userName':fullname,
                    'mobile':mobile,
                    'memberName':memberName,
                    'memberEmail':memberEmail,
                    'date':date,
                    'time':time,
                    'memberId':memberId
                }
                updateBy = {
                    '_id':ObjectId(id)
                }
                response=cmo.update("Appointments",updateBy,data,False)
                return jsonify({'msg':'Data Updated Successfully','data':response}),200

            if current_user['role'] == "MEMBER":
                data2 = request.form.get('datetime')
                data2 = data2.split("T")
                date = data2[0]
                time = data2[1]
            
                data = {
                    'date':date,
                    'time':time,
                }
                updateBy = {
                    '_id':ObjectId(id)
                }
                response=cmo.update("Appointments",updateBy,data,False)
                return jsonify({'msg':'Data Updated Successfully','data':response}),200
            
            


            


        
    if request.method == "DELETE":
        if id!=None:
            cmo.deleteStatus("Appointments",id)
            return (jsonify({"msg": "Document deleted successfully"}))
        else:
            return (jsonify({'msg':'Unsuccessfully Updated'}))
        





# client = razorpay.Client(auth=("rzp_test_xNI1GqYlRGFoZ8", "z3a4Vy43smmw0bpjsSsF16Ih"))
# @member.route("/payment", methods=["POST"])
# def create_payment_link():
#     data = request.get_json()

#     amount = data.get("amount")
#     currency = data.get("currency", "INR")
#     accept_partial = data.get("accept_partial", False)
#     first_min_partial_amount = data.get("first_min_partial_amount", 100)
#     description = data.get("description", "")
    
#     customer = {
#         "name": data.get("customer_name", ""),
#         "email": data.get("customer_email", ""),
#         "contact": data.get("customer_contact", "")
#     }

#     notify_sms = data.get("notify_sms", True)
#     notify_email = data.get("notify_email", True)
    
#     reminder_enable = data.get("reminder_enable", True)

#     notes = {
#         "policy_name": data.get("policy_name", "")
#     }

#     callback_url = data.get("callback_url", "")
#     callback_method = data.get("callback_method", "get")

#     payment_link_data = {
#         "amount": amount,
#         "currency": currency,
#         "accept_partial": accept_partial,
#         "first_min_partial_amount": first_min_partial_amount,
#         "description": description,
#         "customer": customer,
#         "notify": {
#             "sms": notify_sms,
#             "email": notify_email
#         },
#         "reminder_enable": reminder_enable,
#         "notes": notes,
#         "callback_url": callback_url,
#         "callback_method": callback_method
#     }

#     payment_link_response = client.payment_link.create(payment_link_data)

#     return jsonify(payment_link_response)


# @member.route("/genrateToken", methods=["GET", "POST"])
# @token_required
# def genrateToken():
#     token = None
#     if "Authorization" in request.headers:
#             token = request.headers["Authorization"]
#     if not token:
#             return (jsonify({"msg": "a valid token is missing"}),)
#     data = jwt.decode(
#                 token.split(" ")[-1],
#                 algorithms="HS512",
#                 key="sandeep",
#             )
#     access_token = jwt.encode(
#                         {"userDetails": data["userDetails"], "userId": data["userId"],'exp': time.time()+ 86400000},
#                         key="sandeep",
#                         algorithm="HS512",
#                     )
#     return jsonify({"token":access_token}),200