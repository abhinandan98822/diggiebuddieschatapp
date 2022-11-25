from celery import shared_task
from time import sleep 

from django.core.mail import send_mail 
from .models import BuyerProfileModel,User
from django.conf import settings
from webpush import send_user_notification

# @shared_task
# def sleepy(duariton):
#     sleep(duariton)
#     return None

@shared_task
def send_mail_wiht_celery(user,msg):
    subject = 'Admin Message! '
    message = msg
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user]
    send_mail( subject, message, email_from, recipient_list )
    
    return None

@shared_task
def send_otp_with_celery(user,otp):
    subject = 'OTP Verification From Digibuddies '
    message = f"Your OTP for Account Verification in Digibuddies is {otp}"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user]
    send_mail( subject, message, email_from, recipient_list )
    
    return None

@shared_task
def send_postjob_with_celery(user):
    print("donenenjnrjfnjsdnfjsdjfnsdjfnjsdnfjsdn")
    buyerpush= BuyerProfileModel.objects.filter()
    payload = {"head": "New job posted", "body": user + " posted a new job"}
    for buyer in buyerpush:
        send_user_notification(user=buyer.user, payload=payload, ttl=1000)
    return None
    
    
    
