from twilio.rest import Client
from django.conf import settings
import random


def send_sms(to_phone:str,message:str):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=to_phone
    )