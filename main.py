from base import *
from blueprints_routes.auth import auth_blueprint
from blueprints_routes.memberDetails import member
from blueprints_routes.users import user
from common.mail import *
from blueprints_routes.admin import admin
from blueprints_routes.userSchedulePlan import userSchedule
from blueprints_routes.paymentDetails import paymentDetails

app=Flask(__name__)
#######     amar's changes      #####3
socketio = SocketIO(app, cors_allowed_origins="*")
########    Firebase     ######33
from firebase_admin import credentials, messaging
# Path to the downloaded service account key
cred = credentials.Certificate('./amar_midiets_private_key.json')
firebase_admin.initialize_app(cred)

CORS(app,supports_credentials=True)
app.register_blueprint(auth_blueprint)
app.register_blueprint(member)
app.register_blueprint(user)
app.register_blueprint(admin)
app.register_blueprint(userSchedule)
app.register_blueprint(paymentDetails)


# WebSocket event handlers
currentUserId = ''
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

@socketio.on('connect', namespace='/notifications')
def handle_connect():
    token = None
    args = request.args
    authorization = args.get('authorization')
    if authorization:
        try:
            token = authorization.split()[1].strip('"')
        except IndexError:
            print("Invalid authorization header format")
            return jsonify({"msg": "Invalid authorization header format", "status": 'false'}), 401
    else:
        print("Authorization token not found")
        return jsonify({"msg": "Authorization token not found", "status": 'false'}), 401
    
    if not token:
        print("Token is empty")
        return jsonify({"msg": "Token is empty", "status": 'false'}), 401

    try:
        data = tokenGenerate(token, False)
        
        aggr = [
            {"$match": {"_id": ObjectId(data["userId"])}},
            {"$addFields": {"role": {"$toObjectId": "$role"}}},
            {"$lookup": {"from": "userRole", "localField": "role", "foreignField": "_id", "as": "userRole"}},
            {"$addFields": {"roleId": {"$toString": "$role"}, "role": {"$arrayElemAt": ["$userRole.role", 0]}, "_id": {"$toString": "$_id"}}},
            {"$project": {"userRole": 0}},
        ]
        
        current_user = list(cmo.finding_aggregate("users", aggr))
        
        if not current_user:
            print("User not found")
            return jsonify({"msg": "User not found", "status": False}), 404
        
        current_user = current_user[0]
        print("asfdsafsafsadfasdfdsafasdf",current_user)
        # You can emit events to the client after successful validation
        global currentUserId
        currentUserId = current_user['_id']
        print("asfsafsadfsafsadfdsa",currentUserId)
        emit("connect_build", True)
        
    except Exception as e:
        print(f"Error validating token: {e}")
        return jsonify({"msg": "Error validating token", "status": False}), 401

    # Return a success message or data if needed
    return jsonify({"msg": "Connection established successfully", "status": True, "user": current_user})

@socketio.on('disconnect',namespace='/notifications' )
def handle_disconnect():
    print('Client disconnected')

def handle_request_notification():
    print("Request for notification received")
    agrr = [
        {
            '$match': {
                'assignMemberId': (currentUserId),
                'assignedstatus': {'$ne': False}
            }
        },
        {
            '$project': {
                '_id': 0,
                'assign': 1,
                'fullname': 1
            }
        }
    ]
    findData = cmo.finding_aggregate('users', agrr)
    # print("Notificationasfsadffasfdata:", list(findData))
    return list(findData) #{'findData': , 'status': 200}



@socketio.on('request_notification', namespace='/notifications')
def getNotifications():
    notisData = handle_request_notification()
    print("afasdfsadfdsasafdsafsafdsaff",notisData)
    emit('notification', {'findData':notisData, 'status': 200},namespace='/notifications')
 
####### firebase API
def send_fcm_notification(token, title, body):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
        )

        response = messaging.send(message)
        print('Successfully sent message:', response)
    except firebase_admin.exceptions.FirebaseError as e:
        print(f"Error sending message: {e}")

# Example usage: Sending notification on request_notification event
@socketio.on('request_notification', namespace='/notifications')
def getNotifications():
    notisData = handle_request_notification()
    print("afasdfsadfdsasafdsafsafdsaff", notisData)
    emit('notification', {'findData': notisData, 'status': 200}, namespace='/notifications')
    
    # Extract notification details from notisData
    for noti in notisData:
        title = "Notification Title"  # Replace with actual title if available in notisData
        body = json.dumps(noti)  # Convert notification data to string

        # Example FCM token - replace with actual token from your data source
        android_token = 'eXFFVLD2bkSQn4N1HauXrG:APA91bEvIfR5Y6YaOBLWdjvkyaUeD90DQWSAKc4aV75XcC4DfMDKdNJYb6-GfMgEtFd89hFWJXnsPIz8s4bQejhRfckTd3PBCZBch7EwwE5NkaRmaNWzr_ydzs9pf_GzUlui6wSRiykA'  
        if android_token:
            send_fcm_notification(android_token, title, body)
        else:
            print("FCM token is not valid")
    
@app.route('/forget_password',methods=["GET","POST"])
def forgotPassword():
    if request.method == 'POST':
        body=request.get_json()
        email=body['email']
        Aggre = [
        {
            '$match': {
                'email':email,
            }
        },
        ]
        userRole=cmo.finding_aggregate("users",Aggre)
        userRole=list(userRole)
        if (len(userRole) > 0):
            random_number=random.randint(2000,9999)
            new_user_email = email
            email_subject = 'To reset Password'
            email_message = f"Hello your one time password to reset password is {random_number}"
            send_email(new_user_email, email_subject, email_message)
            cmo.update("users",{'email':new_user_email},{'otp':random_number},True)
            return "OTP Sent successfully"
        else:
            return "No User Found with this Email"
    else:
        return "Enter Details"
    
@app.route('/verify_code',methods=["GET","POST"])
def setPassword():
    body=request.get_json()
    email=body["email"]
    otp=body['otp']
    if request.method == 'POST':
        mangerAggre = [
        {
            '$match': {
                'isDeleted': {
                    '$ne': 1
                },
                'email':email,
            }
        },
        ]
        userRole=list(cmo.finding_aggregate("users",mangerAggre,sort=False))
        if len(userRole):
            if (userRole[0]['otp']) == otp:
                return jsonify({'msg':"OTP Match  Successfully"})
            else:
                return ("Wrong Otp!")
        else:
            return("enter Valid  Details")
    else:
        return ("enter details")
    
@app.route('/reset_password',methods=["GET","POST"])
def resetPassword():
    body=request.get_json()
    if request.method == 'POST':
        mangerAggre = [
        {
            '$match': {
                'isDeleted': {
                    '$ne': 1
                },
                'email':body['email'],    
            }
        },
        ]
        userRole=cmo.finding_aggregate("users",mangerAggre,sort=True)
        userRole=list(userRole)
        if body['new_password'] == body['newPassword'] :
            cmo.update("users",{'email':body['email']},{'password':body['new_password']},True)
            return jsonify({'msg':"Paasword Reset Successfully"})
        else:
            return jsonify({'msg':"Password doesn't match "})
    else:
        return jsonify({'msg':'Invalid Request'})
    

@app.route("/")
def index():
     return "<h1>Welcome to MI-DIET Backend Server...</h1>"





if __name__ == "__main__":
    # app.run(debug=True,port=9898,host='0.0.0.0')
    socketio.run(app, debug=False,port=9898,host='0.0.0.0')