
from twilio.rest import Client

def send_sms(to_msg="",body=""):    
    from_msg="+18563176794"
    # to_msg="+918130368188"
    account_sid = 'ACbe0bd62f43a97d82ef03690fe3803bb3'
    auth_token = '2d4dc5840653c4a09a56acd79e7e4753'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_=from_msg,
        body=body,
        to=to_msg
    )

    print(message.sid)
    
    print("sms_sender")