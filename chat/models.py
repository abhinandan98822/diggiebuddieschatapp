from django.db import models
from django.contrib.humanize.templatetags import humanize
# Create your models here.
class ChatModel(models.Model):
    sender = models.CharField(max_length=100, default=None,null=True,blank=True)
    message = models.TextField(null=True, blank=True)
    thread_name = models.CharField(null=True, blank=True, max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(null=True,blank=True,max_length=10)
    
    
    
    def get_date(self):
        return humanize.naturaltime(self.timestamp)

        
    
class FileUpload(models.Model):
    files_upload=models.FileField(null=True,upload_to='messagefiles',blank=True)