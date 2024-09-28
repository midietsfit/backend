

from base import *
def send_email(to_email, subject, message):
    print("asdfasfsafsafsafasdf_asfdadsfa___preparing_mail")
    sender_email = 'amar.nath@fourbrick.com'
    sender_password = 'nngb agqd htsa uzzz'
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        
        
# new_user_email = 'recipient@example.com'
# email_subject = 'New User Created'
# email_message = 'A new user has been created in your application.'
# send_email(new_user_email, email_subject, email_message)
# print("send_mail_successfully>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")



