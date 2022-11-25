from django.contrib import admin
from .models import ChatModel
# Register your models here.
@admin.register(ChatModel)
class ChatModelAdmin(admin.ModelAdmin):
    list_display=['sender']