from pymongo import MongoClient
from dotenv import load_dotenv
import os
from base import *
from datetime import datetime ,timedelta
from bson.objectid import ObjectId
import pytz

env_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path=env_path)
client = MongoClient(os.environ.get("MONGODB_URL"))
db = client["MiDiet"]

def unique_timestamp():
    gmt_plus_5_5 = pytz.timezone("Asia/Kolkata")
    current_time = datetime.now(gmt_plus_5_5)
    timeStamp = int(current_time.timestamp() * 1000)
    return str(timeStamp)

def finding_aggregate(dbname, aggr ,sort=True):
    col = db[dbname]
    if(sort):
        aggr = [{"$match": {"isDeleted": {"$ne": 1}}}] + aggr+[{"$sort": {"_id": -1}}]
    else:
        aggr = [{"$match": {"isDeleted": {"$ne": 1}}}] + aggr
        
    # print("xadxasdasa",aggr)

    findData=col.aggregate(aggr)

    return findData

def finding_aggregateWithArchive(dbname, aggr ,sort=True):
    col = db[dbname]
    if(sort):
        aggr = [{"$match": {"isDeleted": {"$ne": 1}}}] + aggr+[{"$sort": {"_id": -1}}]
    else:
        aggr = [{"$match": {"isDeleted": {"$ne": 1}}}] + aggr
        
    findData =col.aggregate(aggr)

    return findData

def finding(dbname):
    col = db[dbname]
    findData = col.aggregate(
        [
            {"$addFields": {"_id": {"$toString": "$_id"}}},
            {"$match": {"isDeleted": {"$ne": 1}}},
        ]
    )
    return findData

def simpleFinding(dbname,cond):
    col =db[dbname]
    # print("csdbcjvhkakwcvhkweghf", [ 
    #          {"$match": {**cond,"isDeleted": {"$ne": 1}}},
    #     ])
    data =col.aggregate(
       [ 
             {"$match": {**cond,"isDeleted": {"$ne": 1}}},
        ]
    )
    
    return list(data)

def finding_one_with_id(dbname, data):
    aggr = [
        {"$match": {"_id": ObjectId(data),"isDeleted": {"$ne": 1}}},
        {"$addFields": {"_id": {"$toString": "$_id"}}},
        # {"isDeleted": {"$ne": 1}},
    ]
    col = db[dbname]
    findData = col.aggregate(aggr)
    return findData

def finding_one_with_email(dbname, data):
    # aggr = [
    #     {"$match": {"email":data}},
    #     {"$addFields": {"_id": {"$toString": "$_id"}}},
    # ]
    col = db[dbname]
    findData = col.find_one({"email": data})
    return findData

def insertion(dbname, data):
    col = db[dbname]
    data["createdAt"]=unique_timestamp()
    success_data = col.insert_one(data)
    return success_data.inserted_id

def insertion_many(dbnane, data):
    col = db[dbnane]
    for i in data:
        i["createdAt"]=unique_timestamp()
    col.insert_many(data)
    return "Updated"

def insertion_many_Adv(dbnane, data):
    col = db[dbnane]
    for i in data:
        i["createdAt"]=unique_timestamp()
    resp=col.insert_many(data)
    return resp

def deletion(dbname, data):
    col = db[dbname]
    col.delete_one(data)
    return "Deleted"

def deleteStatus(dbname, id,key="_id"):
    col = db[dbname]
    newData = {"isDeleted": 1}
    col.update_one({key: ObjectId(id)}, {"$set": newData})
    return "Delete Status Updated"

def update(dbnane, filter1, newData,upst=False):
    col = db[dbnane]
    result=col.update_one(filter1, {"$set": newData},upsert=upst)
    return result.matched_count

def updateToggleKey(dbnane, filter1, newData,upst=False):
    col = db[dbnane]
    result=col.update_one(filter1, [{"$set": newData}],upsert=upst)
    return result.matched_count

def updateMany(dbnane, filter1, newData,upst=False):
    col = db[dbnane]
    result=col.update_many(filter1, {"$set": newData},upsert=upst)
    status={"matched_count": result.matched_count, "modified_count": result.modified_count}
    return status

def universalUpdate(dbnane, oldData, newData):
    col = db[dbnane]
    col.update_one(oldData,newData)
    return "Updated"

def deleteKeyFromDocument(dbname,filter,data):
    col =db[dbname]
    col.update_many(filter,{"$unset":data})

def update_push(dbnane, oldData, newData):
    col = db[dbnane]
    col.update_one(oldData, newData)
    return "Updated"

def updateWithPush(dbnane, findData, newData,upst=False):
    col = db[dbnane]
    col.update_one(findData,{"$push": newData},upsert=upst)
    return "Updated"

def updateWithPull(dbnane, findData,dbKey,position ,upst=False):
    col = db[dbnane]
    aggr={
                "$pop": {
                    dbKey: -1
                }
        }
    aggr={
        "$pull": {
            dbKey: {"$position": 0},  # Additional conditions if needed
        }
    }
   
    col.update_one(findData,aggr,upsert=upst)
    return "Updated"

def unique_timestamp():
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist)
    delayed_time = current_time + timedelta(hours=5, minutes=30)
    timestamp = int(int(delayed_time.timestamp() * 1000))
    
    return timestamp


# def insertion(dbname,data):
#     status={}
#     try:
#         col=db[dbname]
#         resp=col.insert_one(data)
#         print(resp.inserted_id)
#         common_status_log_adder(dbname,{"_id":resp.inserted_id})
#         status["state"]=1
#         status["operation_id"]=resp.inserted_id
#         status["data"]=[]
#         status["msg"]="Data Added Successfully"


#     except errors.DuplicateKeyError as dke:

#         print(dke.details["keyValue"])
#         col=db[dbname]
#         dictdata=dke.details["keyValue"]
#         dictdata["isDeleted"]=1
#         finsDatadps=list(col.find(dictdata))
#         removeThis={
#             "deleated_at":unique_timestamp(),
#             "isDeleted":1
#         }
#         if(len(finsDatadps)>0):
#             resp=col.update_one(dke.details["keyValue"],{'$unset':removeThis})
#             print(finsDatadps[0]["_id"])
#             status["state"]=1
#             status["operation_id"]=finsDatadps[0]["_id"]
#             status["data"]=[]
#             status["msg"]="Data Added Successfully"
#         else:
#             print(finsDatadps,"finsDatadps")
#             # if()
#             msg=dke.details["keyPattern"].keys()
#             print(msg)
#             status["state"]=2
#             status["data"]=[]
#             status["msg"]=list(msg)[0]+" Already Exist"

#     except errors.WriteError as we:
#         print(we.details)
#         msg=""
#         for i in we.details["errInfo"]["details"]["schemaRulesNotSatisfied"]:
#             print(i,"i")

#             if("propertiesNotSatisfied" in i):
#                 for j in i["propertiesNotSatisfied"]:
#                     for k in j["details"]:
#                         msg=msg+str(j["description"])+","

#             if("missingProperties" in i):
#                 for j in i["missingProperties"]:
#                     msg=msg+str(j)+" is missing"+","

#         status["state"]=3
#         status["data"]=[]
#         status["msg"]=msg

#     return status











# import os
# from pymongo import MongoClient,errors
# from dotenv import load_dotenv
# import bson
# from bson import json_util
# from jsonschema import validate
# from jsonschema.exceptions import ValidationError
# import json
# from bson.objectid import ObjectId
# from common.config import unique_timestamp,timestamp,mdy_timestamp
# from bson.objectid import ObjectId
# from datetime import datetime,timedelta,date
# from flask import  jsonify
# env_file_name = ".env"
# env_path = os.path.join(os.getcwd(),env_file_name)
# load_dotenv(dotenv_path=env_path)

# # mongo_client = MongoClient(host=os.environ.get("MONGODB_HOST"),port=int(os.environ.get("MONGODB_PORT")),connect=bool(os.environ.get("MONGODB_connect")))
# # mongo_client.server_info()
# # db = mongo_client[os.environ.get("MONGODB_DATABASE")]
# mongo_client =MongoClient('localhost', 27017)
# mongo_client.server_info()
# db = mongo_client["EMS"]
# status={"state":True,"msg":"","data":[]}

# def timestamp():
#     return '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())

# def status_log_adder(database,log_inset):
#     log_inset["log_add_date"]=timestamp()
#     log_inset["log_add_timestamp"]=unique_timestamp()
#     log_insert=insertion("log_"+database,log_inset)    
#     return "ok"

# def common_status_log_adder(database,logjson):
#     logdata=finding(database,logjson)["data"][0]
#     logdata["parent_id"]=logdata["_id"]["$oid"]
#     logdata["currentTimeStampLog"]=timestamp()
#     logdata["maindata"]=database
#     del logdata["_id"]
#     col=db["log_"+database]
#     resp=col.insert_one(logdata)
#     # status_log_adder(database,logdata)
#     return logdata

# def insertion(dbname,data):
#     try:
#         col=db[dbname]
#         resp=col.insert_one(data)
#         print(resp.inserted_id)
#         common_status_log_adder(dbname,{"_id":resp.inserted_id})
#         status["state"]=1
#         status["operation_id"]=resp.inserted_id
#         status["data"]=[]
#         status["msg"]="Data Added Successfully"
#     except errors.DuplicateKeyError as dke:
#         msg=dke.details["keyPattern"].keys()
#         status["state"]=2
#         status["data"]=[]
#         status["msg"]=list(msg)[0]+" Already Exist"
    
#     except errors.WriteError as we:
#         print(we.details)
#         msg=""
#         for i in we.details["errInfo"]["details"]["schemaRulesNotSatisfied"]:
#             print(i,"i")
#             if("propertiesNotSatisfied" in i):
#                 for j in i["propertiesNotSatisfied"]:
#                     for k in j["details"]:
#                         msg=msg+str(j["description"])+","
#             if("missingProperties" in i):
#                 for j in i["missingProperties"]:
#                     msg=msg+str(j)+" is missing"+","
#         status["state"]=3
#         status["data"]=[]
#         status["msg"]=msg
#     return status

# def insertion_all(dbname,data):
#     try:
#         col=db[dbname]
#         resp=col.insert_many(data)
#         print(resp)
#         status["state"]=1
#         status["data"]=[]
#         status["msg"]="Data Added Successfully"
#     except errors.DuplicateKeyError as dke:
#         msg=dke.details["keyPattern"].keys()
#         status["state"]=2
#         status["data"]=[]
#         status["msg"]=list(msg)[0]+" Already Exist"
#     except errors.WriteError as we:
#         print(we.details)
#         msg=""
#         for i in we.details["errInfo"]["details"]["schemaRulesNotSatisfied"]:
#             if("propertiesNotSatisfied" in i):
#                 for j in i["propertiesNotSatisfied"]:
#                     for k in j["details"]:
#                         msg=msg+str(j["description"])+","
#             if("missingProperties" in i):
#                 for j in i["missingProperties"]:
#                     msg=msg+str(j)+" is missing, "
#         status["state"]=3
#         status["data"]=[]
#         status["msg"]=msg
#     return status

# def finding(dbname,data,data1=None):
#     col=db[dbname]
#     datafetch=[]
#     if(data!=None):
#         if(data1!=None):
#             datafetch=list(col.find(data,data1))
#         else:
#             datafetch=list(col.find(data))
#     else:
#         if(data1!=None):
#             datafetch=list(col.find(data1))
#         else:
#             datafetch=list(col.find())
#     # print(datafetch)
#     status["state"]=4
#     status["msg"]=""
#     status["data"]=json.loads(json_util.dumps(datafetch))
    
#     return status



# def object_id_validate(dbname,data):
#     try:
#         print("object_id_validate",dbname,data)
#         col=db[dbname]
#         datafetch=list(col.find({"_id":ObjectId(data)}))
#         if(len(datafetch)>0):
#             return ("Data Exist",1)
#         else:
#             return ("ObjectId Not Exist",2)
#     except Exception as e:
#         error=str(e)
#         return (error,3)


# def get_object_id(dbname,data):
#     print("object_id_data",dbname,data)
#     col=db[dbname]
#     datafetch=list(col.find(data))
#     status={}
#     status["state"]=4
#     status["msg"]=""
#     status["data"]=json.loads(json_util.dumps(datafetch))
    
#     return status


# def keyRemover(dbname,data,removeThis):
#     try:
#         col=db[dbname]
#         lookdata={"_id":ObjectId(data)}
#         setdata={
#             "deleated_at":unique_timestamp(),
#             "deleteStatus":1
#         }
#         print(lookdata,{"$set":setdata})
#         col.update_one(lookdata,{'$unset':removeThis})
#         status["state"]=1
#         status["msg"]=""
#         status["data"]=[]
#     except Exception as e:
#         print(e)


    

# def keyRemoverWithUpdate(dbname,lookdata,data,removeThis):
#     try:
#         status={}
#         col=db[dbname]
#         print(lookdata,{"$set":data},{'$unset':removeThis},"keyRemoverWithUpdate")
#         col.update_one(lookdata,{"$set":data,'$unset':removeThis},True)
#         status["state"]=1
#         status["msg"]=""
#         status["data"]=[]

#         return status
#     except Exception as e:
#         print(e)


# def object_id_data(dbname,data):
#     print("object_id_data",dbname,data)
#     col=db[dbname]
#     datafetch=list(col.find({"_id":ObjectId(data)}))
#     status={}
#     status["state"]=4
#     status["msg"]=""
#     status["data"]=json.loads(json_util.dumps(datafetch))
    
#     return status

# def findAllUniqueKeys(dbname):
#     col=db[dbname]
#     first_doc = col.find_one()
#     if(first_doc):
#         resp=list(first_doc.keys())
#         print("jdbckhfebsfvhjfdbsvuehg=",resp)
#         dataFetech=col.distinct(resp)

#         return jsonify(dataFetech)

# def finding_aggregate(dbname,data):
#     status={}
#     col=db[dbname]
#     data.append({"$match":{"deleteStatus":{"$ne":1}}})

#     # print(data,"finding_aggregatedata")
#     datafetch=list(col.aggregate(data))
    
#     # print(datafetch)
#     status["state"]=4
#     status["msg"]=""
#     status["data"]=json.loads(bson.json_util.dumps(datafetch))
    
#     return status
    
# def updating(dbname,lookdata,setdata,upse):
#     try:
#         col=db[dbname]
#         print(lookdata,{"$set":setdata})
#         resp=col.update_one(lookdata,{"$set":setdata},upsert=upse)
#         print(resp)
#         common_status_log_adder(dbname,lookdata)
#         status["state"]=1
#         status["msg"]=""
#         status["data"]=[]
#     except Exception as e:
#         print(e)
#     return status

# def addToSetupdating(dbname,lookdata,setdata,upse):
#     try:
#         col=db[dbname]
#         # print(lookdata,{"$set":setdata})
#         # arrayOuter=[
#         #     {"subscribedPlants.$.id":setdata["plant"]}
#         # ]
#         # resp=col.update_one(lookdata,{
#         #     "$addToSet":{
#         #         # "subscribedPlants.1":setdata["plant"],
#         #         "subscribedPlants.1.subscribedSensors":setdata["subscribedSensors"],
#         #     }    
#         # },array_filters=arrayOuter
#         # )
#         # print(resp)

#         filter = lookdata

#         print(lookdata)
#         update = {
#             "$addToSet": {"nested_array": {
#             "subscribedPlants":setdata["plant"],
#             "subscribedSensors":setdata["subscribedSensors"]
#         }}}

#         # Perform the update
#         col.update_one(filter, update)



#         # common_status_log_adder(dbname,lookdata)
#         status["state"]=1
#         status["msg"]=""
#         status["data"]=[]
#     except Exception as e:
#         print(e)
#     return status




# def addToSetupdatingnew(dbname,filter,update,upse):
#     try:
#         col=db[dbname]
#         # print(lookdata,{"$set":setdata})
#         # arrayOuter=[
#         #     {"subscribedPlants.id":setdata["plant"]}
#         # ]
#         # resp=col.update_one(lookdata,{
#         #     "$addToSet":{
#         #         # "subscribedPlants.1":setdata["plant"],
#         #         "subscribedPlants.1.subscribedSensors":setdata["subscribedSensors"],
#         #     }    
#         # },array_filters=arrayOuter
#         # )
#         # print(resp)

        

#         # Perform the update
#         col.update_one(filter, update)



#         # common_status_log_adder(dbname,lookdata)
#         status["state"]=1
#         status["msg"]=""
#         status["data"]=[]
#     except Exception as e:
#         print(e)
#     return status

# # def addToSetupdatingnew(dbname,lookdata,filtering,setdata,upse):
# #     try:
# #         col=db[dbname]
# #         arrayOuter=[
# #             {"subscribedPlants":setdata["plant"]}
# #         ]
# #         updation={
# #             "$addToSet":{
# #                 # "subscribedPlants.1":setdata["plant"],
# #                 "nested_array.$[subscribedPlants].subscribedSensors":setdata["subscribedSensors"],
# #             }    
# #         }
# #         print(lookdata,arrayOuter,updation)
# #         print(lookdata,{"$set":setdata})
        

# #         resp=col.update_one(lookdata,updation,array_filters=arrayOuter
# #         )
# #         # print(resp)

        

# #         # Perform the update
# #         # col.update_one(filter, update)



# #         # common_status_log_adder(dbname,lookdata)
# #         status["state"]=1
# #         status["msg"]=""
# #         status["data"]=[]
# #     except Exception as e:
# #         print(e)
# #     return status
# # def addToPush(dbname,lookdata,setdata,upse):
# #     try:
# #         col=db[dbname]
# #         print(lookdata,{"$set":setdata})
# #         resp=col.update_one(lookdata,{"$addToSet":setdata},upsert=upse)
# #         print(resp)
# #         common_status_log_adder(dbname,lookdata)
# #         status["state"]=1
# #         status["msg"]=""
# #         status["data"]=[]
# #     except Exception as e:
# #         print(e)
# #     return status
# # def olddeleting(dbname,id):
# #     try:
# #         col=db[dbname]
# #         lookdata={"_id":ObjectId(id)}
# #         setdata={
# #             "deleated_at":unique_timestamp(),
# #             "deleteStatus":1
# #         }
# #         print(lookdata,{"$set":setdata})
# #         col.update_one(lookdata,{"$set":setdata},upsert=False)
# #         status["state"]=1
# #         status["msg"]=""
# #         status["data"]=[]
# #     except Exception as e:
# #         print(e)
# #     return status

# # def deleting(dbname,id):
# #     try:
# #         col=db[dbname]
# #         lookdata={"_id":ObjectId(id)}

# #         all_data=list(col.find(lookdata))
# #         print(all_data,"all_data")
# #         # insertion_all("deleted_data",all_data)
          
# #         # col.delete_one(lookdata)
        

# #         col.update_one(lookdata,{"$set":setdata},upsert=False)
# #         status["state"]=1
# #         status["msg"]=""
# #         status["data"]=[]
# #     except Exception as e:
# #         print(e)
# #     return status

# def deleting(dbname,id):
#     try:
#         col=db[dbname]
#         lookdata={"_id":ObjectId(id)}
#         setdata={
#             "deleated_at":unique_timestamp(),
#             "deleteStatus":1
#         }
#         print(lookdata,{"$set":setdata})
#         col.update_one(lookdata,{"$set":setdata},upsert=False)
#         status["state"]=1
#         status["msg"]=""
#         status["data"]=[]
#     except Exception as e:
#         print(e)
#     return status

# def real_deleting(dbname,id):
#     try:
#         col=db[dbname]
#         lookdata={"_id":ObjectId(id)}
#         col.delete_one(lookdata)
#         status["state"]=1
#         status["msg"]=""
#         status["data"]=[]
#     except Exception as e:
#         print(e)
#     return status

# def real_bulk_deleting(dbname,looker):
#     try:
#         col=db[dbname]
#         col.delete_many(looker)
#         status["state"]=1
#         status["msg"]=""
#         status["data"]=[]
#     except Exception as e:
#         print(e)
#     return status

# def updating_more(dbname,lookdata,setdata,upse):
#     col=db[dbname]
#     print(lookdata,{"$set":setdata})
#     resp=col.update_one(lookdata,{"$set":setdata},upsert=upse)
#     common_status_log_adder(dbname,lookdata)
#     print(resp)
#     return True

# def real_deletingWithOutId(dbname,aggr):  
#     status={}
#     try:
#         col=db[dbname]
#         lookdata=aggr
#         col.delete_one(lookdata)
#         status["state"]=1
#         status["msg"]=""
#         status["data"]=[]
#     except Exception as e:
#         print(e)
#     return status

# def updatingArray(dbname,lookdata,arrayOperator,setdata,upse):
#     try:
#         col=db[dbname]
#         print(lookdata,{"$set":setdata})
#         resp=col.update_one(lookdata,{arrayOperator:setdata},upsert=upse)
#         status["state"]=1
#         status["msg"]=""
#         status["data"]=[]
#     except Exception as e:
#         print(e)
#     return status


# def finding_aggregate_without_code(dbname,data):
#     status={}
#     col=db[dbname]
#     data.append({"$match":{"deleteStatus":{"$ne":1}}})
#     datafetch=list(col.aggregate(data))
#     return datafetch
    



