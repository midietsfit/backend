from base import *

userSchedule = Blueprint("userSchedule", __name__)

days = {
    
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
    7: "Sunday",
}


@userSchedule.route("/setMeal", methods=["POST", "GET", "PUT", "DELETE"])
@userSchedule.route("/setMeal/<userId>", methods=["POST", "GET", "PUT", "DELETE"])
@token_required
def SetMeal(current_user=None, userId=None):

    if request.method == "POST":
        data = request.get_json()





        # if not all([data.get("planId"), data.get("day")]):
        #     return jsonify({"msg": "Provide Plan Id and day"}), 400
        # if data["day"] > 0 and data["day"] >= 8:
        #     return jsonify({"msg": "please select valid day"}), 400

        # findBy = [
        #     {
        #         "$match": {
        #             "primaryId": current_user["_id"],
        #             "planId": data["planId"],
        #             "isDeleted": 0,
        #             "dayCount": data["day"],
        #         }
        #     },
        #     {"$sort": {"day": -1}},
        # ]
        # fetchData = list(cmo.finding_aggregate("meals", findBy,sort=False))
        # daySet = 1
        # if len(fetchData):
        #     return jsonify({"msg": "already set by you please check meal plan"}), 400

        newData = {

            "isDeleted": 0,
            "dayCount": data["day"],
            "date": data["date"],
            "food": data["food"],
            "meal": data["meal"],
            "memberId": current_user["_id"],
            'primaryId':data['primaryId'],
        }
        data.update(newData)
        id = cmo.insertion("meals", data)
        # newData = {"isDeleted": 0, "mealId": id, "primaryId": current_user["_id"]}
        # cmo.insertion("mealPlan", newData)
        return jsonify({"msg": "Data added"})

    if request.method == "GET":
        # aggr = [
        #     {
        #         "$match": {
        #             "primaryId": str(userId),
        #             "isDeleted": {'$ne':1}
        #         }
        #     }, {
        #         "$lookup": {
        #             "from": "mealPlan",
        #             "localField": "_id",
        #             "foreignField": "mealId",
        #             "pipeline": [
        #                 {
        #                     '$match':{
        #                         'isDeleted':{'$ne':1}
        #                     }
        #                 }, {
        #                     "$lookup": {
        #                         "from": "mealFoods",
        #                         "localField": "_id",
        #                         "foreignField": "mealPlanId",
        #                         "pipeline": [
        #                             {
        #                                 '$match':{
        #                                     'isDeleted':{'$ne':1}
        #                                 }
        #                             }, {
        #                                 "$addFields": {
        #                                     "mealPlanId": {"$toString": "$mealPlanId"},
        #                                     "_id": {"$toString": "$_id"},
        #                                 }
        #                             }
        #                         ],
        #                         "as": "result",
        #                     }
        #                 }, {
        #                     "$addFields": {
        #                         "mealId": {"$toString": "$mealId"},
        #                         "_id": {"$toString": "$_id"},
        #                     }
        #                 },
        #             ],
        #             "as": "mealPlan",
        #         }
        #     }, {
        #         "$addFields": {
        #             "_id": {
        #                 "$toString": "$_id"
        #             }
        #         }
        #     }, {
        #         '$sort': {
        #             'dayCount': 1
        #         }
        #     }
        # ]
        # fetchData = list(cmo.finding_aggregate("meals", aggr,sort=False))
        # if len(fetchData):
        #     return jsonify({"msg": "Data get Successfully", "data": fetchData})
        # else:
        #     return jsonify({"msg": "No data found", "data": []})

        arra = [
            {
                '$match': {
                    'primaryId': userId
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
                    'meal': {
                        '$first': '$meal'
                    }
                }
            }, {
                '$group': {
                    '_id': '$_id.date', 
                    'data': {
                        '$push': '$$ROOT'
                    }
                }
            }
        ]
        fetchData = list(cmo.finding_aggregate("meals", arra))
        print(fetchData,'fetchDatafetchDatafetchDatafetchData')
        return jsonify({"msg": "Data get Successfully", "data": fetchData})
        
    if request.method == "PUT":
        if userId!=None:
            body=request.get_json()
            updateBy={'_id':ObjectId(userId)}
            cmo.update("meals",updateBy,body,False)
            return jsonify({'msg':'Successfully Updated'})
        else:
            return jsonify({'msg':'Unsuccessfully Updated'})
    
    if request.method == "DELETE":
        if userId!=None:
            respond=cmo.deleteStatus("meals",userId)
            return jsonify({'msg':'Successfully Deleted'})
        else:
            return jsonify({'msg':'Unsuccessfully Updated'})
    else:
        return jsonify ({'msg':'No method user'})

@userSchedule.route("/setMealPlan", methods=["POST", "GET", "DELETE"])
@token_required
def setMealPlan(current_user):
    
    if request.method == "POST":
        data = request.get_json()
        if not all([data.get("mealId")]):
            return jsonify({"msg": "provide meal plan id"}), 400
        updateBy = {"_id": ObjectId(data.get("mealId"))}
        newData = {"primaryId": current_user["_id"], "mealId": ObjectId(data["mealId"])}
        del data["mealId"]
        data.update(newData)
        insertedId=cmo.insertion("mealPlan", data)
        # cmo.update("mealPlan",updateBy, {"$push": {"mealArray": newData}})
        return jsonify({"msg": "Data added "})
    
    if request.method == "DELETE":
        data = request.get_json()
        if not all([data.get("mealPlanId")]):
            return jsonify({"msg": "provid meal plan id"}), 400
        updateBy = {"_id": ObjectId(data.get("mealPlanId"))}
        del data["mealPlanId"]

        for key, value in data.items():
            data[key] = ""
        cmo.update("mealPlan", updateBy, data)
        return jsonify({"msg": "Data deleted"})


@userSchedule.route("/setMealFood", methods=["POST", "GET","PUT", "DELETE"])
@userSchedule.route("/setMealFood/<id>", methods=["POST", "GET","PUT", "DELETE"])
@token_required
def setMealFood(current_user,id=None):
    if request.method == "POST":
        data = request.get_json()
        print(data)
        if not all([data.get("mealPlanId")]):
            return jsonify({"msg": "Provide meal plan id"}), 400

        # updateBy = {"_id": ObjectId(data.get("mealPlanId"))}
        newData = {
            "primaryId": current_user["_id"],
            "mealPlanId": ObjectId(data["mealPlanId"]),
        }
        data.update(newData)
        cmo.insertion("mealFoods", data)
        return jsonify({"msg": "Data added"}), 200
        # return jsonify({"msg": "Failed to add data"}), 500

    # else:
    #     return jsonify({"msg": "Invalid method"}), 405
    
    if request.method == "PUT":
        if id!=None:
            body=request.get_json()
            print(body)
            print(id)
            updateBy={'_id':ObjectId(id)}
            cmo.update("meals",updateBy,body,False)
            return jsonify({'msg':'Successfully Updated'})
        else:
            return jsonify({'msg':'Unsuccessfully Updated'})
        
    if request.method == "DELETE":
        if id!=None:
            cmo.deleteStatus("mealFoods", id)
            return (jsonify({"msg": "Document deleted successfully"})),200
        else:
            return (jsonify({'msg':'Unsuccessfully Updated'})),400
        

@userSchedule.route("/getMeal", methods=["GET"])
@token_required
def getMeal(current_user):
    if request.method == "GET":
        arra = [
            {
                '$match': {
                    'primaryId': current_user["_id"],
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
                    'meal': {
                        '$first': '$meal'
                    }
                }
            }, {
                '$group': {
                    '_id': '$_id.date', 
                    'data': {
                        '$push': '$$ROOT'
                    }
                }
            }, {
                '$addFields': {
                    'date': '$_id'
                }
            }, {
                '$project': {
                    '_id': 0
                }
            }
        ]
        fetchData = list(cmo.finding_aggregate("meals", arra))
        return jsonify({"msg": "Data get Successfully", "data": fetchData})
