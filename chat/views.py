from django.shortcuts import render
from mainapp.models import User
from .models import FileUpload,ChatModel
from django.http import JsonResponse
# Create your views here.
def private_chat_home(request):
    users = User.objects.exclude(email=request.user)
    return render(request, 'chatroom.html', context={'users': users})

def chatPage(request, username):
    user_obj = User.objects.get(first_name=username)
    users = User.objects.exclude(email=request.user.email)
    if request.method =="POST":
        img = request.FILES.getlist('files[]',None)
        fullfile=img[0]
        strfullfile=str(fullfile)
        # print(files,"======--------")
        # img=request.FILES['file_upload']
        print(strfullfile)
        ext = strfullfile.split('.')[-1]
        a=''
        if ext == 'jpeg' or ext =='png' or ext == "jpg" or ext =="img" :
            a='image'
        elif ext == 'mp4':
            a='video'
        else:
            a='others'
        print()
        if request.user.id > user_obj.id:
            thread_name = f'chat_{request.user.id}-{user_obj.id}'
        else:
            thread_name = f'chat_{user_obj.id}-{request.user.id}'
        image_save=FileUpload(files_upload=img[0])
        image_save.save()
        return JsonResponse({'url':image_save.files_upload.url,'msgtype':a})


    
    if request.user.is_authenticated:

        if request.user.id > user_obj.id:
            thread_name = f'chat_{request.user.id}-{user_obj.id}'
        else:
            thread_name = f'chat_{user_obj.id}-{request.user.id}'
        message_objs = ChatModel.objects.filter(thread_name=thread_name)
        print(message_objs)

        return render(request, 'chat.html', context={'user' : f"{user_obj.id}" ,'users': users, 'messages' : message_objs, 'username' : user_obj, 'count' : len(message_objs)})
    else:
        return render(request, 'chatroom.html')