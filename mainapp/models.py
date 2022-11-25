from email.policy import default
from platform import java_ver
from unicodedata import category
from django.db import models
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
import os
# Create your models here.
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify

from django.db import models
from notifications.models import notify_handler
from notifications.signals import notify
from notifications.models import Notification
from django_countries.fields import CountryField
from django.contrib.humanize.templatetags import humanize


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            first_name=first_name,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100,blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_seller=models.BooleanField(default=False)
    is_buyer=models.BooleanField(default=False)
    is_verified=models.BooleanField(default=False)
    is_online=models.BooleanField(default=False)


    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin



class NotificationCTA(models.Model):
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE)
    cta_link = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return str(self.cta_link)


def custom_notify_handler(*args, **kwargs):
    notifications = notify_handler(*args, **kwargs)
    cta_link = kwargs.get("cta_link", "")
    for notification in notifications:
        NotificationCTA.objects.create(notification=notification, cta_link=cta_link)
    return notifications


notify.disconnect(notify_handler, dispatch_uid='notifications.models.notification')
notify.connect(custom_notify_handler)  # , dispatch_uid='notifications.models.notification')

class OTPModel(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    otp=models.CharField(max_length=6)

    def __str__(self):
        return str(self.user)

class JobCategoryModel(models.Model):
    category_title=models.CharField(max_length=45)
    category_desc=models.CharField(max_length=1000)
    
    def __str__(self):
        return self.category_title

class JobTypeModel(models.Model):
    job_type_title=models.CharField(max_length=45)
    job_type_desc=models.CharField(max_length=1000)

    def __str__(self):
        return self.job_type_title

class SkillModel(models.Model):
    skill_title=models.CharField(max_length=45)
    skill_desc=models.CharField(max_length=100)
    
    def __str__(self):
        return self.skill_title

class SellerProfileModel(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    company_logo=models.ImageField(upload_to='seller/company/logos')
    company_address=models.CharField(max_length=100)
    city_of_company=models.CharField(max_length=100)
    country_of_company=CountryField()
    company_name=models.CharField(max_length=100,unique=True)
    company_email=models.EmailField(max_length=255,unique=True,blank=True,null=True)
    company_phone_number=models.CharField(max_length=20,blank=True,null=True,unique=True)
    #company_short_desc=models.CharField(max_length=100)
    company_desc=RichTextUploadingField() 

    def __str__(self):
        return self.company_name


class BuyerProfileModel(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    address=models.CharField(max_length=100)
    profile_desc=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    country=CountryField()
    state=models.CharField(max_length=100)
    gender=models.CharField(max_length=20)
    skills=models.ManyToManyField(SkillModel)
    linkedin_profile=models.URLField(max_length=255,blank=True,null=True)
    github_profile=models.URLField(max_length=255,blank=True,null=True)
    profile_picture=models.ImageField(upload_to='buyer/images/profile_pic')
    resume=models.FileField(upload_to='buyer/files/resumes')
    long_description=RichTextUploadingField()

    def __str__(self):
        return str(self.user)

class PostjobModel(models.Model):
    seller=models.ForeignKey(SellerProfileModel,on_delete=models.CASCADE)
    job_title=models.CharField(max_length=100)
    short_desc=models.CharField(max_length=2000)
    full_desc=RichTextUploadingField()
    skills=models.ManyToManyField(SkillModel)
    job_type=models.ManyToManyField(JobTypeModel,blank=True)
    category_type=models.ManyToManyField(JobCategoryModel,blank=True)
    deadline=models.DateTimeField()
    askamount=models.IntegerField()
    is_completed=models.BooleanField(default=False)
    slug = models.SlugField(unique=True,blank=True,null=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.job_title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.job_title

class BidAmountModel(models.Model):
    job=models.ForeignKey(PostjobModel,on_delete=models.CASCADE)
    bidder=models.ForeignKey(BuyerProfileModel,on_delete=models.CASCADE)
    bid_amount= models.IntegerField()
    is_accepted=models.BooleanField(default=False)
    pitch=models.CharField(max_length=2000,blank=True,null=True)
 
    def __str__(self):
        return str(self.bid_amount)+'bid for '+str(self.job)+' by '+str(self.bidder)
    

class ApplyForJobModel(models.Model):
    buyer=models.ForeignKey(BuyerProfileModel,on_delete=models.CASCADE)
    applied_job=models.ForeignKey(PostjobModel,on_delete=models.CASCADE)
    seller=models.ForeignKey(SellerProfileModel,on_delete=models.CASCADE)
    pitch=models.CharField(max_length=2000,blank=True,null=True)
    bidamount=models.IntegerField()

    def __str__(self):
        return str(self.applied_job)+' by '+str(self.buyer)+' for '+str(self.bidamount)

class Payment(models.Model):
    seller = models.ForeignKey(SellerProfileModel,on_delete=models.DO_NOTHING)
    bidder = models.ForeignKey(BuyerProfileModel,on_delete=models.DO_NOTHING,null=True)
    order_id =  models.CharField(max_length=100)
    payment_id = models.CharField(max_length=100)
    payment_signature = models.CharField(max_length=150,blank=True)
    amount = models.IntegerField()
    job = models.ForeignKey(PostjobModel,on_delete=models.DO_NOTHING)
    paymentReport = models.BooleanField(default=True,null=True)
    date_time = models.DateTimeField(auto_now_add=True, blank=True,null=True)

# Private chat app
# class ChatModel(models.Model):
#     sender = models.CharField(max_length=100, default=None,null=True,blank=True)
#     message = models.TextField(null=True, blank=True)
#     thread_name = models.CharField(null=True, blank=True, max_length=50)
#     timestamp = models.DateTimeField(auto_now_add=True)
#     file_type = models.CharField(null=True,blank=True,max_length=10)
    
    
    
#     def get_date(self):
#         return humanize.naturaltime(self.timestamp)

        
    
# class FileUpload(models.Model):
#     files_upload=models.FileField(null=True,upload_to='messagefiles',blank=True)