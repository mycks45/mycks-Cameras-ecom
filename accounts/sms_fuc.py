

def send_sms(body,to_):
    import twilio 
    from twilio.rest import Client
    account_sid = 'ACe7dd118113ace03f3575904f029a16fd'
    auth_token = 'd5fe7c3374f47031b7c9b47cee9d46e1'
    client = Client(account_sid, auth_token)
    massage = client.messages.create(
        body=body,
        from_ = '+16105462107', 
        to ='+91'+to_
    )

def gen_otp():
    import math,random
    digits= '0123456789'
    OTP =''
    for i in range(6):
        OTP += digits[math.floor(random.random()*10)]
    return OTP