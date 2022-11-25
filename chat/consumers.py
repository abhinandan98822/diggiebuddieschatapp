import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatModel
from mainapp.models import User
from django.contrib.auth import get_user_model
from webpush import send_user_notification

User = get_user_model()

class PersonalChatConsumer(WebsocketConsumer):
    def connect(self):
        my_id = self.scope['user'].id
        user=User.objects.get(id=my_id)
        user.is_online=True
        user.save()
        other_user_id = self.scope['url_route']['kwargs']['id']
        if int(my_id) > int(other_user_id):
            self.room_name = f'{my_id}-{other_user_id}'
        else:
            self.room_name = f'{other_user_id}-{my_id}'

        self.room_group_name = 'chat_%s' % self.room_name

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        my_id = self.scope['user'].id
        sender=User.objects.get(id=my_id)
        
        message = data['message']
        username = data['username']
        file_type = data['file_type']
        
        reciever=User.objects.get(id=username)
        if reciever.is_online==False:
            payload = {"head": "New message", "body": sender.first_name + ' : ' + message,"url": "/chat/"+str(sender.first_name)}

            send_user_notification(user=reciever, payload=payload, ttl=1000)
        else:
            pass
       
        data_base = self.save_message(username, self.room_group_name, message,file_type)
        print("This is a database output", data_base)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'file_type':file_type
            }
        )
    def chat_message(self, event):
        message = event['message']
        user_id = event['username']
        file_type = event['file_type']
        user_obj = User.objects.get(id=user_id)
        self.send(text_data=json.dumps({
            'message': message,
            'username' : user_obj.email,
            'user_id': user_id,
            'file_type' : file_type
        }))
        print(f"{user_obj.email} : Messaage sent")

    def disconnect(self, code):
        my_id = self.scope['user'].id
        user=User.objects.get(id=my_id)
        user.is_online=False
        user.save()

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # @database_sync_to_async is used with asynchronous code
    def save_message(self, username, thread_name, message,file_type):
        print("Message going to saved")
        new_message = ChatModel.objects.create(
            sender=username, message=message, thread_name=thread_name,file_type = file_type)
        new_message.save()
        return "Succes"

