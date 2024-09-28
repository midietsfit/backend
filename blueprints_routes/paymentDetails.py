from base import *
import hmac
import hashlib  
import os
import jwt
import razorpay
from common.mongoDb_operation import unique_timestamp
from datetime import datetime
from dotenv import load_dotenv
import urllib.parse

paymentDetails=Blueprint("paymentDetails",__name__)

load_dotenv()

RAZORPAY_API_KEY = os.getenv('RAZORPAY_API_KEY')
RAZORPAY_API_SECRET = os.getenv('RAZORPAY_API_SECRET')
RAZORPAY_WEBHOOK_SECRET = os.getenv('RAZORPAY_WEBHOOK_SECRET')
client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET))


# @paymentDetails.route("/payment", methods=["POST"])
# def create_payment_link():
#     print("afasfdasdfasfsafaa_added_payment")
#     data = request.get_json()
#     print("asfsafsafasafafa",data)
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

#     callback_url = data.get("callback_url", "http://localhost:9898/paymentCallBack")
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



# @paymentDetails.route("/paymentCallBack", methods=["GET"])
# def paymentCallBack():
#     # print(request.args)

#     data=request.args

#     cmo.insertion("paymentLogs",data)
#     return request.args



# @paymentDetails.route("/payment", methods=["POST"])
# def create_order():
#     data = request.get_json()
#     print("fdsafsaasfasafa",data)
#     amount = int(data.get('amount')) * 100 # Amount in paise
#     print("afdafasfasfasfd",amount)
#     currency = 'INR'
    
#     payment_order = client.order.create(dict(amount=amount, currency=currency, payment_capture='1'))
    
#     return jsonify(payment_order)


@paymentDetails.route('/payment_verification', methods=['POST'])
def payment_verification():
    try:
        data = request.get_json()
        print("asfsafsaffdasfdsafsadf____dfagfa",data)
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')

        body = razorpay_order_id + "|" + razorpay_payment_id
        expected_signature = hmac.new(
            RAZORPAY_API_SECRET.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        print("asfsafdsafsafasfsafafd__expected_sign",expected_signature)
        print("asdfsafasfsafasfdasfd__razorpay_signature",expected_signature)

        is_authentic = (expected_signature == razorpay_signature)
        print("asfasfsafasfsafd___true__false",is_authentic)
        if is_authentic:
            # Save the payment info to the database
            print("dsafsafsafasfasfasasfd__authentic")
            payment_info = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature,
                'status': 'successful'
            }
            cmo.insertion('payment',payment_info)
            return jsonify({
                'success':True,
                'message':"Payment Successful"
            }),200
        else:
            return jsonify({'success': False, 'message': 'Invalid signature'}), 400
    except Exception as e:
        print(f"Error in payment verification: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@paymentDetails.route('/create_payment_link', methods=['POST'])
@token_required
def create_payment_link(current_user):
    try:
        print("asfsafsafsadsadffdasd_current_user",current_user)
        data = request.get_json()
        print("afdasfasfasdfaf___data_in_Link",data)
        
        # data["payDetailsObj"]["planName"]
        
        # data["payDetailsObj"]["planDiscount"]
        disc=[
                {
                    '$match': {
                        'discount': int(data["discount"])
                    }
                }
            ]
        dataDisc = cmo.finding_aggregate("discount",disc)
        planN=[
                {
                    '$match': {
                        'planType': data["planName"]
                    }
                }
            ]
        dataplanN = list(cmo.finding_aggregate("makePlan",planN))
        
        # return jsonify({'success': True,}), 200
        # exit()
        finaldiscount = int(data["discount"]) if len(list(dataDisc))>0 else 0
        
        finalduration = int(data["duration"]) if data["duration"] else 0
        
        finalDbPrice  = 0
        if(len(dataplanN)>0):
            
            finalDbPrice = dataplanN[0]["price"]
            
        else:
            return jsonify({'success': False, 'error': str("e")}), 500
        
    
        
        
        total = finalduration * finalDbPrice - (finalduration * finalDbPrice * finaldiscount / 100)
        
        # amount =int(data.get('amount'))* 100  # amount in paise
        amount = total * 100  # amount in paise
        
        usersN=[
                {
                    '$match': {
                        '_id': ObjectId(data["userId"])
                    }
                }
            ]
        usersDN = list(cmo.finding_aggregate("users",usersN))
        
        
        if(len(usersDN)==0):
            return jsonify({'success': False, 'error': str("e")}), 500
        
        
            
        print(usersDN[0],"usersDNusersDNusersDN")
        
        customer_name = usersDN[0]["fullname"] if "fullname" in usersDN[0] else ""
        customer_email = usersDN[0]["email"] if "email" in usersDN[0] else ""
        customer_contact = usersDN[0]["mobile"] if "mobile" in usersDN[0] else ""
        
        
        payName = data.get('payName')
        # customer_email = data.get('email')
        # customer_contact = data.get('contact')
        if(current_user['role'] != 'SUPER_ADMIN'):
            data['memberName']=current_user['fullname'] 
            data['member_id'] = current_user['_id']
        else:
            memberName = data['memberName']
            print("safdasfdasfasfdsafafds__memberName",memberName)
            aggr= [
                    {
                        '$match': {
                            'role': '657bedcb65749a0ef718848e',
                            'fullname': memberName
                        }
                    },
                    {
                        '$project': {
                            '_id': { '$toString': '$_id' }
                        }
                    }
                ]
           
            result_cursor =  cmo.finding_aggregate('users',aggr,False)
            print(result_cursor,"rssssss")
            memberId = None
            for doc in result_cursor:
                memberId = doc.get('_id')
                break 

            data['member_id'] = memberId
            print("asdfsafasdfsafasfdasdfdsaf______memberId", memberId)
    
        payment_link_data = {
            "amount": amount,
            "currency": "INR",
            "accept_partial": False,
            "description": payName,
            "customer": {
                "name": customer_name,
                "email": customer_email,
                "contact": customer_contact
            },
            "notify": {
                "sms": True,
                "email": True,
                "whatsapp": True,
            },
            "reminder_enable": True,
            "callback_url": "https://api.midiets.com/webhookCall",
            # "callback_url": "http://127.0.0.1:9898/webhook",
            "callback_method": "get"
        }
        
        
        print(payment_link_data,"payment_link_datapayment_link_datapayment_link_data")
        payment_link = client.payment_link.create(payment_link_data)
        print("afasfsadfdsafasfddsafdsfafds__payment_link",payment_link,payment_link_data)
        data['razorpay_payment_link_id'] = payment_link['id']
        data['payment_link'] = payment_link['short_url']
        data['paymentApprovedStatus']='pending'
        
        insertion_id = cmo.insertion('payment',data)
        print("fdsadfsadfafdsfdafdaf__id",insertion_id)
        
        return jsonify({'success': True, 'payment_link': payment_link['short_url']}), 200
    except Exception as e:
        print(f"Error in creating payment link: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
@paymentDetails.route("/webhookCallSuccess", methods=["GET"])
def webhookCallSuccess():
        return render_template("pay.html")
@paymentDetails.route("/webhookCall", methods=["GET"])
def webhookCall():
    try:
        razorpay_signature = request.args.get('razorpay_signature')
        print("afasffdsafd__received_signature",razorpay_signature)
        razorpay_payment_id = request.args.get('razorpay_payment_id')
        print("afasffdsafd__razorpay_payment_id",razorpay_payment_id)
        razorpay_payment_link_id = request.args.get('razorpay_payment_link_id')
        print("afasffdsafd__razorpay_payment_link_id",razorpay_payment_link_id)
        razorpay_payment_link_status = request.args.get('razorpay_payment_link_status')
        print("afasffdsafd__razorpay_payment_link_status",razorpay_payment_link_status)
        razorpay_payment_link_reference_id = request.args.get('razorpay_payment_link_reference_id')
        print("afasffdsafd__razorpay_payment_link_status",razorpay_payment_link_reference_id)
        
        if not razorpay_signature:
            return jsonify({'status': 'error', 'message': 'Missing razorpay_signature parameter'}), 400
        
        
        
        new_data = {
                'razorpay_payment_id': razorpay_payment_id,
                'paymentStatus': razorpay_payment_link_status
            }
        
        update_result = cmo.update('payment', {'razorpay_payment_link_id': razorpay_payment_link_id}, new_data,True)
        if update_result:
            return redirect("/webhookCallSuccess")
            
        else:
            return jsonify({'status': 'error', 'message': 'Update failed'}), 500
        
        
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@paymentDetails.route("/payment", methods=["GET"])
@paymentDetails.route('/payment/<id>',methods=["GET","POST","DELETE","PATCH","PUT"])
@token_required
def create_order(current_user, id=None):
    if request.method=='GET':
        print("asfdsafasfasfsafdasfafd___current_user",current_user)
        # function to get all details
        if(current_user['role']=='SUPER_ADMIN'):
            aggr = [
                        {
                            '$match': {
                                'isDeleted':0
                            }
                        },
                        {
                            '$addFields': {
                                '_id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                    ]
        else:
            aggr = [
                        {
                            '$match': {
                                'isDeleted':0
                            }
                        },
                        {
                            '$addFields': {
                                '_id': {
                                    '$toString': '$_id'
                                }
                            }
                        },
                        {
                            '$match':{
                                'member_id':current_user['_id']
                            }
                        }
                    ]
        paymentData = list(cmo.finding_aggregate('payment',aggr,False))
        print("afsafsafdsafasfasdf",paymentData)
        return jsonify(paymentData)
    if request.method == "PUT":
        if id!= None:
            data = request.get_json()
            respond=cmo.update("payment",{"_id":ObjectId(id)},data,True)
            return jsonify({'msg':'Successfully Updated'})
    if request.method == "DELETE":
        if id!=None:           
            respond=cmo.deleteStatus("payment",id)
            return jsonify({'msg':'Successfully Deleted'})
        else:
            return jsonify({'msg':'Unsuccessfully Updated'})
    
    # return jsonify(payment_order)

@paymentDetails.route('/webhook', methods=['GET','POST'])
def webhook():
    if request.method=='GET':
        print(request.args)
    
    if request.method=='POST':
        
        data=request.get_json()
        print(data)
        
        cmo.insertion("payementEventLogs",data)
        return jsonify({'status': 'success'}), 200
        
    # try:
    #     razorpay_signature = request.args.get('razorpay_signature')
    #     print("afasffdsafd__received_signature",razorpay_signature)
    #     razorpay_payment_id = request.args.get('razorpay_payment_id')
    #     print("afasffdsafd__razorpay_payment_id",razorpay_payment_id)
    #     razorpay_payment_link_id = request.args.get('razorpay_payment_link_id')
    #     print("afasffdsafd__razorpay_payment_link_id",razorpay_payment_link_id)
    #     razorpay_payment_link_status = request.args.get('razorpay_payment_link_status')
    #     print("afasffdsafd__razorpay_payment_link_status",razorpay_payment_link_status)
    #     razorpay_payment_link_reference_id = request.args.get('razorpay_payment_link_reference_id')
    #     print("afasffdsafd__razorpay_payment_link_status",razorpay_payment_link_reference_id)
        
    #     if not razorpay_signature:
    #         return jsonify({'status': 'error', 'message': 'Missing razorpay_signature parameter'}), 400
        
    #     new_data = {
    #             'razorpay_payment_id': razorpay_payment_id,
    #             'paymentStatus': razorpay_payment_link_status
    #         }
        
    #     update_result = cmo.update('payment', {'razorpay_payment_link_id': razorpay_payment_link_id}, new_data,True)
    #     if update_result:
    # return jsonify({'status': 'success'}), 200
    #     else:
    #         return jsonify({'status': 'error', 'message': 'Update failed'}), 500
        
        
    # except Exception as e:
    #     print(f"Error processing webhook: {e}")
    #     return jsonify({'status': 'error', 'message': str(e)}), 500



@paymentDetails.route('/payment_status/<payment_id>', methods=['GET'])
def payment_status(payment_id):
    try:
        payment = client.payment.fetch(payment_id)
        status = payment['status']
        return jsonify({'status': status}), 200
    except Exception as e:
        print(f"Error fetching payment status: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
