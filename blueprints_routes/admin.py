from base import *
import os
UPLOAD_FOLDER = os.path.join("uploads", "image") 
from common.mongoDb_operation import unique_timestamp
admin=Blueprint("admin_data",__name__)

@admin.route("/uploads/<subDir>/<fileName>")
def send_file_route(subDir, fileName):
    try:
        file_path = os.path.join(os.getcwd(),"uploads", subDir, fileName)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return "File not found", 404
    except Exception as e:
        return f"Error: {str(e)}", 500

@admin.route("/notification",methods=["GET","POST",])
@admin.route("/notification/<id>",methods=["GET","POST","PUT","DELETE"])
@token_required
def manage_notification(current_user,id=None):
    if request.method == "GET":
        arra=[
            {
                '$match':{
                    'isDeleted':{'$ne':1}
                }
            }, {
                '$addFields':{
                    '_id':{'$toString':'$_id'},
                    'date': {
                        '$dateToString': {
                            'format': '%d-%m-%Y', 
                            'date': {
                                '$toDate': '$date'
                            }
                        }
                    }
                }
            }
        ]
        respond=list(cmo.finding_aggregate("notification",arra))
        return jsonify({'data':respond,'status':'true','statusCode':200}),200
    if request.method == "POST":

        member = request.form.getlist("member")
        image = request.files.get("img")
        newnotification = request.form.get("newnotification")
        date = request.form.get('date')
        user = request.form.getlist("user")

        if image:
            ext = str(image.filename).split(".")[-1]
            img_name = str(unique_timestamp()) + "." + ext
            path = os.path.join(UPLOAD_FOLDER, img_name)
            image.save(path)

        body = {
            'img':path if image else None,
            'newnotification':newnotification,
            'date':date,
        }
        if member and member!='none':
            body['member'] = member
        if user and user !='none':
            body['user'] = user

        Response=cmo.insertion("notification",body)
        return jsonify({'msg':"Successfully inserted data",'status':'true','statusCode':201}),201
    
    if request.method == "PUT":
        if id!=None:
            member = request.form.get("member")
            membername = request.form.get("membername")
            image = request.files.get("img")
            newnotification = request.form.get("newnotification")

            if image:
                ext = str(image.filename).split(".")[-1]
                img_name = str(unique_timestamp()) + "." + ext
                path = os.path.join(UPLOAD_FOLDER, img_name)
                image.save(path)


            body = {
                'member':member,
                'membername':membername,
                'img':path if image else None,
                'newnotification':newnotification,
            }
            
            updateBy={'_id':ObjectId(id)}
            cmo.update("notification",updateBy,body,False)
            return jsonify({'msg':'data successfully updated','status':'true','statusCode':200}),200
        else:
            return jsonify({'msg':'Unsuccessfully Updated','status':'false','statusCode':404}),404
    if request.method == "DELETE":
        if id!=None:
            respond=cmo.deleteStatus("notification",id)
            return jsonify({'msg':'Successfully Deleted','status':'true','statusCode':200}),200
        else:
            return jsonify({'msg':'Unsuccessfully Updated','status':'false','statusCode':404}),404

# @admin.route("/restrictUsers",methods=["GET","POST"])
# @token_required
# def restrictUsers(current_user):
#     arr=[
#     {
#         '$match': {
#             'verified': False,
#             'role':{
#                     '$eq':getRole("USER")
#                 },
#             'isDeleted':{
#                 '$ne':1
#             }
#         }
#     },
#     {
#         '$addFields': {
#             '_id': {
#                 '$toString': '$_id'
#             },
#         }
#     }
#     ]
#  
#     respond=list(cmo.finding_aggregate("users",arr))
#     return respond

@admin.route("/restrictUser",methods=["GET","POST","PUT","DELETE"])
@admin.route("/restrictUser/<id>",methods=["GET","POST","PUT","DELETE"])
@token_required
def restrictUser(current_user,id=None):
    try:
        if request.method == "GET":
            arr=[
                {
                    '$match': {
                        'status': False
                        , 
                        'role': getRole("USER"), 
                        'isDeleted': {
                            '$ne': 1
                        }
                    }
                }, {
                    '$addFields': {
                        '_id': {
                            '$toString': '$_id'
                        },
                    }
                },
                {
                    '$project': {
                        '_id':0,
                    }
                }
                
            ]
            respond=list(cmo.finding_aggregate("users",arr))
            return respond
        # if request.method == "POST":
        #     body = request.get_json()
        #     body["status"] = True
        #     #body.setdefault('status', True)
        #     cmo.insertion("users", body)
        #     return jsonify({'msg': 'Data added Successfully'})

        if request.method == "PUT":
            if id is not None:
                try:
                    body = request.get_json()
                    update_by = {'_id': ObjectId(id)}
                    cmo.update("users", update_by, body, False)
                    return jsonify({'msg': 'Updated Successfully'})
                except Exception as e:
                    return jsonify({'errordddd': str(e)}), 500
            else:
                return jsonify({'msg': 'Invalid Id'})
    except Exception as e:
        return jsonify({'errorsssss': str(e)}), 500        
        

@admin.route("/restrictMembers",methods=["GET","POST","PUT","DELETE"])
@admin.route("/restrictMembers/<id>",methods=["GET","POST","PUT","DELETE"])
@token_required
def restrictMembers(current_user,id=None):
    try:
        if request.method == "GET":
            arr=[
                {
                    '$match': {
                        'status': {'$eq': False},
                        'isDeleted': {'$ne': 1},
                         'role': {'$eq':getRole("MEMBER")}, 
                    }
                }
            ]
            # if (request.args.get('q') == "Member"):
                # arra = arra + [
                #     {
                #         '$match':{
                #             'role': {'$eq':getRole("MEMBER")}, 
                #         }
                #     }
                # ]
            # if (request.args.get('q') == "User"):
            #     arra = arra + [
            #         {
            #             '$match':{
            #                 'role': {'$eq':getRole("USER")}, 
            #             }
            #         }
            #     ]
            arr = arr + [
                {
                    '$addFields': {
                        '_id': {
                            '$toString': '$_id'
                        },
                    }
                }, {
                    '$project': {
                        'current_target': 1, 
                        'left_target': 1, 
                        'fullname': 1, 
                        'email': 1, 
                        'password': 1, 
                        'status': 1, 
                        'target':1,
                    }
                }
            ]
            respond=list(cmo.finding_aggregate("users",arr))
            return respond
        
        if request.method == "POST":
            body = request.get_json()
            body["status"] = True
            #body.setdefault('status', True)
            cmo.insertion("users", body)
            return jsonify({'msg': 'Data added Successfully'})

        if request.method == "PUT":
    
            if id is not None:
                try:
                    body = request.get_json()
                    update_by = {'_id': ObjectId(id)}
                    cmo.update("users", update_by, body, False)
                    return jsonify({'msg': 'Updated Successfully'})
                except Exception as e:
                    return jsonify({'errordddd': str(e)}), 500
            else:
                return jsonify({'msg': 'Invalid Id'})
    except Exception as e:
        return jsonify({'errorsssss': str(e)}), 500        

@admin.route("/cardDetail",methods=["GET"])
@token_required
def cardDetails(current_user):
    if request.method == "GET":
        arr=[
            {
                '$match': {
                    'isDeleted': {
                        '$ne': 1
                    }, 
                    'memberId': current_user['_id']
                }
            }
        ]
        arr2=[
            {
                '$match': {
                    'isDeleted': {
                        '$ne': 1
                    }, 
                    'role': getRole("USER")
                }
            }
        ]
        if current_user['role'] == "MEMBER":
            arr2 = arr2 + [
                {
                    '$match':{
                        'assignMemberId':current_user['_id']
                    }
                }
            ]
        arr3=[
            {
                '$match': {
                    'isDeleted': {
                        '$ne': 1
                    }, 
                    # 'roleId': current_user['roleId']
                }
            }
        ]
        arr4=[
            {
                '$match':{
                    'isDeleted':{'$ne':1}
                }
            }
        ]
        arra=[
            {
                '$match': {
                    'role': 'MEMBER', 
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
                    'localField': '_id', 
                    'foreignField': 'role',
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
            }
        ]
        Total_member=list(cmo.finding_aggregate("userRole",arra))
        Total_appointments=list(cmo.finding_aggregate("Appointments",arr))
        Total_users=list(cmo.finding_aggregate("users",arr2))
        Total_blogs=list(cmo.finding_aggregate("blog",arr3))
        Total_payment=list(cmo.finding_aggregate("payment",arr4))
        body={
            'Total_Appointments':len(Total_appointments),
            'Total_Users':len(Total_users),
            'Total_Blogs':len(Total_blogs),
            'Total_Payment':len(Total_payment),
            'Total_Member':len(Total_member)
        }
        return jsonify({'msg':'success','total':body})
    



@admin.route("/coupons",methods=["GET","POST"])
@admin.route("/coupons/<id>",methods=["GET","POST","PUT","PATCH","DELETE"])
@token_required
def coupons(current_role,id=None):
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
                    'validFrom': {
                        '$dateToString': {
                            'format': '%d-%m-%Y', 
                            'date': {
                                '$toDate': '$validFrom'
                            }
                        }
                    }, 
                    'validTo': {
                        '$dateToString': {
                            'format': '%d-%m-%Y', 
                            'date': {
                                '$toDate': '$validTo'
                            }
                        }
                    }
                }
            }
        ]
        respond=list(cmo.finding_aggregate("coupons",arra))
        return jsonify({'data':respond,'msg':'Data get Successfully'}),200
    
    if request.method == "POST":
        body=request.get_json()

        body['createdBy']=current_role['_id']
        body['role']=current_role['role']
        Response=cmo.insertion("coupons",body)
        return jsonify({'msg':"Successfully inserted data"}),200
    
    if request.method == "PUT":
        if id!=None:
            body=request.get_json()
            updateBy={'_id':ObjectId(id)}
            cmo.update("coupons",updateBy,body,False)
            return jsonify({'msg':'Successfully Updated'}),200
        else:
            return jsonify({'msg':'Unsuccessfully Updated'}),404
        
    if request.method == "DELETE":
        if id!=None:
            respond=cmo.deleteStatus("coupons",id)
            return jsonify({'msg':'Successfully Deleted'}),200
        else:
            return jsonify({'msg':'Unsuccessfully Updated'}),404

@admin.route("/appUpdate",methods=["GET","POST"])
@admin.route("/appUpdate/<id>",methods=["GET","POST","PUT","DELETE"])
def app_update(id=None):
    if request.method == "GET":
        arr=[
            {
                '$match':{
                    'isDeleted':{'$ne':1}
                }
            }, {
                '$addFields': {
                    '_id': {'$toString': '$_id'},
                    'date': {
                        '$dateToString': {
                            'format': '%d-%m-%Y', 
                            'date': {
                                '$toDate': '$date'
                            }
                        }
                    }
                }
            }
        ]
        respond=list(cmo.finding_aggregate("appUpdate",arr))
        return jsonify({'msg':'Data Get Successfully','data':respond,'statusCode':200,'status':'true'}),200
    
    if request.method == "POST":
        version=request.form.get("version")
        type=request.form.get("type")
        link=request.form.get("link")
        forceUpdate=request.form.get("forceUpdate")
        date=request.form.get("date")
        data={
        "version":version,
        "type":type,
        "link":link,
        "date":date,
        "forceUpdate":forceUpdate,
        }
        respond=cmo.insertion("appUpdate",data)
        return jsonify({"msg":"New Version added successfully",'status':'true','statusCode':201}),201
    if request.method == "PUT":
        if id!=None:
            version=request.form.get("version")
            type=request.form.get("type")
            link=request.form.get("link")
            forceUpdate=request.form.get("forceUpdate")
            date=request.form.get("date")
            data={

                "version":version,
                "type":type,
                "link":link,
                "date":date,
                "forceUpdate":forceUpdate,
            }
            updateBy={'_id':ObjectId(id)}
            respond=cmo.update("appUpdate",updateBy,data,False)
            return jsonify({'msg':'Successfully Updated','data':respond,'status':'true','statusCode':200})
        else:
            return jsonify({'msg':'Unsuccessfully Updated','status':'false','statusCode':404}),404    
    if request.method == "DELETE":
        if id!=None:
            respond=cmo.deleteStatus("appUpdate",id)
            return jsonify({'msg':'Successfully Deleted','status':'true','statusCode':200}),200
        else:
            return jsonify({'msg':'Unsuccessfully Updated','status':'false','statusCode':404}),404
        
        
# @admin.route('/FoodItems',methods=["GET","POST"])
# @admin.route('/FoodItems/<id>',methods=['GET',"POST",'PUT','PATCH','DELETE'])
# @token_required
# def Food_Items(current_user,id=None):
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
#             }
#             ,
#             {
#         '$project': {
#             'username': 0, 
#             'createdBy': 0, 
#             'createdAt': 0, 
#             'username': 0
#         }
#     }]
#   
#         data=list(cmo.finding_aggregate("foodItems",arra))
#       
#         return jsonify({'data':data})
#     if request.method == "POST":
#         foodName = request.form.get("foodName")
#         receipe = request.form.get("receipe")
#         image = request.files.get("img")
#         calories=request.form.get("calories")
#         data = {
#             "foodName":foodName,
#             "receipe":receipe,
#             "calories":calories,
#             "username":current_user['fullname'],
#             "createdBy":current_user['_id']
#         }
#         if image:
#             ext = str(image.filename).split(".")[-1]
#             img_name = str(unique_timestamp()) + "." + ext
#             path = os.path.join(UPLOAD_FOLDER, img_name)
#         
#             image.save(path)
#             data["img"]=path
        
#       
#         respond=cmo.insertion("foodItems", data)
#         # aggr = [{"$addFields": {"_id": {"$toString": "$_id"}}},]
#         # location = list(cmo.finding_aggregate("foodItems", aggr))
#     
#         return jsonify({"msg": "FoodItem submitted successfully"}), 201
#     if request.method == "PUT":
#         if id!=None:
#                 foodName = request.form.get("foodName")
#                 receipe = request.form.get("receipe")
#                 image = request.files.get("img")
#                 calories=request.form.get("calories")
#                 path = None 
#                 if image:
#                     ext = str(image.filename).split(".")[-1]
#                     img_name = str(unique_timestamp()) + "." + ext
#                     path = os.path.join(UPLOAD_FOLDER, img_name)
#                     image.save(path)

#                 data = {
#                     "foodName":foodName,
#                     "receipe":receipe,
#                     "img":path,
#                     "calories":calories,
#                     # "username":current_user['fullname'],
#                     # "createdBy":current_user['_id'],
#                 }
#                 updateBy={'_id':ObjectId(id)}
#                 MSG = cmo.update("foodItems", updateBy, data, False)
#                 return (jsonify({"msg": "blog data is updated successfully"}))
#         else:
#             return jsonify({'msg':'Please use a valid user Id'})
#     if request.method == "DELETE":
#         if id!=None:
#             cmo.deleteStatus("foodItems", id)
#             return (jsonify({"msg": "Document deleted successfully"}))
#         else:
#             return (jsonify({'msg':'Unsuccessfully Updated'}))
        
@admin.route('/FoodItems',methods=["GET","POST"])
@admin.route('/FoodItems/<id>',methods=['GET',"POST",'PUT','PATCH','DELETE'])
@token_required
def Food_Items(current_user,id=None):
    
    if request.method == "GET":
        print('ppppppppppppppppppppppppppppppppppppppppppppppppppppppppp')
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
            }, {
                '$project': {
                    'username': 0, 
                    'createdBy': 0, 
                    'createdAt': 0, 
                    'username': 0
                }
            }
        ]
        print(arra,'arraarraarra')
        data=list(cmo.finding_aggregate("foodItems",arra))
        return jsonify({'data':data}),200
    
    if request.method == "POST":
        formData = request.form
        for i in formData:
            print(i)
        foodName = request.form.get("foodName")
        receipe = request.form.get("receipe")
        image = request.files.get("img")
        calories=request.form.get("calories")
        calories = calories if calories else 'N/A'
        data = {
            "foodName":foodName,
            "receipe":receipe,
            "calories":calories,
            "username":current_user['fullname'],
            "createdBy":current_user['_id']
        }
        if image:
            ext = str(image.filename).split(".")[-1]
            img_name = str(unique_timestamp()) + "." + ext
            path = os.path.join(UPLOAD_FOLDER, img_name)
            image.save(path)
            data["img"]=path
        
        respond=cmo.insertion("foodItems", data)
        return jsonify({"msg": "FoodItem submitted successfully"}),201
    if request.method == "PUT":
        if id!=None: 
                foodName = request.form.get("foodName")
                receipe = request.form.get("receipe")
                image = request.files.get("img")
                calories=request.form.get("calories")
                calories = calories if calories else 'N/A'
                
                data = {
                    'username':current_user['fullname'],
                    "createdBy":current_user['_id']
                }
                if foodName:
                    data['foodName']=foodName
                if receipe:
                    data['receipe']=receipe
                if calories:
                    data['calories']=calories
                if image:
                    ext = str(image.filename).split(".")[-1]
                    img_name = str(unique_timestamp()) + "." + ext
                    path = os.path.join(UPLOAD_FOLDER, img_name)
                    image.save(path)
                    data['img']=path
                updateBy={'_id':ObjectId(id)}
                MSG = cmo.update("foodItems", updateBy, data, False)
                return (jsonify({"msg": "blog data is updated successfully"})),200
        else:
            return jsonify({'msg':'Please use a valid user Id'}),404
        
    if request.method == "DELETE":
        if id!=None:
            cmo.deleteStatus("foodItems", id)
            return (jsonify({"msg": "Document deleted successfully"})),200
        else:
            return (jsonify({'msg':'Unsuccessfully Updated'})),404


@admin.route('/makePlan',methods=["GET","POST"])
@admin.route('/makePlan/<id>',methods=["PUT","POST",'DELETE'])
@token_required
def makePlanAdmin(current_user,id=None):
    if request.method == "GET":
        arra = [
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
            }
        ]
        if request.args.get('plan')  and request.args.get('plan') != "undefined":
            arra = arra + [
                {
                    '$match':{
                        'planType':request.args.get('plan')
                    }
                }
            ]
        allData = list(cmo.finding_aggregate("makePlan",arra))
        return jsonify({"msg":'Data get successfully','data':allData,"status":'true','statusCode':200}),200
    if request.method == "POST":
        planType = request.form.get("planType")
        price = int(request.form.get("price"))
        data = {

            'planType':planType,
            'price':price,
            'createdAt':unique_timestamp(),
            'createdBy':current_user['roleId'],
            'role':current_user['role'],
            'uniqueId':current_user['_id']
        }
        cmo.insertion("makePlan",data)
        return jsonify({"msg":'plan is successfully created',"status":'true','statusCode':'201'}),201
    
    if request.method == "PUT":
        if id!=None:
            planType = request.form.get("planType")
            price = int(request.form.get("price"))
            data = {
                'planType':planType,
                'price':price,
            }
            updateBy = {
                '_id':ObjectId(id)
            }
            cmo.update('makePlan',updateBy,data,False)
            return jsonify({"msg":'data updated successfully','status':'true','statusCode':200}),200
        else:
            return jsonify({"msg":'please provide valid userId',"msg":'false','statusCode':404}),404
        
    if request.method == "DELETE":
        if id!=None:
            cmo.deleteStatus("makePlan",id)
            return jsonify({'msg':'Data deleted successfully','status':'true','statusCode':200}),200
        else:
            return jsonify({"msg":'please provide valid userId',"msg":'false','statusCode':404}),404

@admin.route('/discount',methods=["GET","POST"])
@admin.route('/discount/<id>',methods=["GET","POST",'PUT','DELETE'])
@token_required
def discounttouser(current_user,id=None):
    if request.method == "GET":
        arra = [
            {
                '$match':{
                    'isDeleted':{'$ne':1}
                }
            }, {
                '$addFields':{
                    '_id':{
                        '$toString':'$_id'
                    }
                }
            }, {
                '$sort':{
                    'discount':1
                }
            }
        ]
        respond = list(cmo.finding_aggregate('discount',arra,sort=False))
        return jsonify({'msg':'Data get Successfully','data':respond}),200
    
    if request.method == "POST":
        discount = int(request.form.get('discount'))
        if not discount:
            return jsonify({'msg':'please provide discount'}),404
        data = {
            'discount':discount
        }
        cmo.insertion("discount",data)
        return jsonify({'msg':'data insert successfully'}),201
    
    if request.method == "PUT":
        if id!=None:
            discount = int(request.form.get('discount'))
            if not discount:
                return jsonify({'msg':'please provide discount'}),404
            data = {
                'discount':discount
            }
            updateBy = {
                '_id':ObjectId(id)
            }
            cmo.update("discount",updateBy,data,False)
            return jsonify({'msg':'data updated successfully'}),200
        else:
            return jsonify({'msg':'please provide valid unique id'}),404
        
    if request.method == "DELETE":
        if id!=None:
            cmo.deleteStatus("discount",id)
            return jsonify({'msg':'Data deleted successfully','status':'true','statusCode':200}),200
        else:
            return jsonify({"msg":'please provide valid userId',"msg":'false','statusCode':404}),404

        



