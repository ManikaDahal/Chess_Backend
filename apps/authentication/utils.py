from twilio.rest import Client
from django.conf import settings
import random


def send_sms(to_phone: str, message: str):
    try:
        client = Client(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)
        msg = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE,
            to=to_phone
        )
        print(f"SMS sent: SID={msg.sid}")  # This will print in your Django terminal
    except Exception as e:
        print(f"Twilio Error: {str(e)}")
        raise
