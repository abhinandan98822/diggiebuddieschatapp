
from django.shortcuts import render, redirect,HttpResponse
from .models import ApplyForJobModel, JobTypeModel, OTPModel, Payment, SellerProfileModel, SkillModel, User, BuyerProfileModel, JobCategoryModel, PostjobModel, BidAmountModel, SkillModel
from .models import ApplyForJobModel, JobTypeModel, NotificationCTA, OTPModel, SellerProfileModel, SkillModel, User, BuyerProfileModel, JobCategoryModel, PostjobModel, BidAmountModel, SkillModel
from .forms import PostJobForm, SellerForm, UserCreationForm, BuyerForm, PostJobForm, ApplyJobForm
import random
from django.contrib.auth import login,authenticate
from django.views.generic.edit import DeleteView
from django.contrib import messages
import razorpay
from django.conf import settings
from django.http import JsonResponse
from .filters import JobFilter,alljobfilter
from django.contrib.auth import  update_session_auth_hash
from django.db.models import F
from webpush import send_user_notification
from django.contrib.auth.decorators import user_passes_test
from .decorators import buyer_role_required,seller_role_required,authenticated_user
from notifications.signals import notify
import json
from notifications.utils import slug2id
from django.shortcuts import get_object_or_404
from swapper import load_model
from django.template import Library
from .ipaddress import get_client_ip
from .task import *

register = Library()
Notification = load_model('notifications', 'Notification')
# Create your views here.

#User Registration view
def user_register(request):

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            
            #create_user() need only first_name,email,password. last_name is saved after calling create_user()
            user = User.objects.create_user(first_name=first_name, email=email, password=password)
            user.last_name = last_name
            user.save()
            
            #otp generated and sent to user email for verification
            otp = random.randint(100000, 999999)
            otpmodel = OTPModel(user=user, otp=otp)
            otpmodel.save()
            send_otp_with_celery.delay(email,otp)
            # subject = "OTP Verification From Digibuddies"
            # message = f"Your OTP for Account Verification in Digibuddies is {otp}"
            
            # #send_mail() for sending mail to [email] with subject and messaage(that contains above generated #otp)
            # send_mail(subject, message, 'tu716599@gmail.com', [email], fail_silently=False)
            return redirect('verify')
        
        else:
            return render(request, 'mainapp/register.html', {'form': form})

    form = UserCreationForm()
    return render(request, 'mainapp/register.html', {'form': form})

#index or home page view 
def index(request):

    ip=get_client_ip(request)
    print(ip)
    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id)
         
        # dashboard for seller or client
        if user.is_seller:
            
            profile_type = 'seller'
            seller = SellerProfileModel.objects.get(user=user.id)
            
            try:
                posted_jobs = PostjobModel.objects.filter(seller=seller)

            except:
                posted_jobs = None

            bid_dict = {}
            
            for data in posted_jobs:
                bid_obj = BidAmountModel.objects.filter(job=data)
                bid_dict[data] = bid_obj

            return render(request, 'mainapp/index.html', {
                'bid_dict': bid_dict, 
                'profile_type': profile_type,
                'sellerlogo':seller,
                }
            )
        # Dashboard for the buyer or freelancer
        elif user.is_buyer:
            category_data,skills_data,jobtype_data=None,None,None

            if request.method == "POST":
                
                for data in request.POST:

                    if data == 'csrf':
                        break

                    key=data
                    value=request.POST[data]

                if key=="category":
                    category_data=JobCategoryModel.objects.filter(category_title__icontains=value).values_list('id')
                    
                else:
                    category_data=None

                if key=="job":
                    jobtype_data=JobTypeModel.objects.filter(job_type_title__icontains=value).values_list('id')

                else:
                    jobtype_data=None

                if key=="skills":
                    skills_data=SkillModel.objects.filter(skill_title__icontains=value).values_list('id')

                else:
                    skills_data=None
                    
            
            profile_type = 'buyer'
            buyer = BuyerProfileModel.objects.get(user=user)
            applied_by_user = ApplyForJobModel.objects.filter(buyer=buyer).values_list('applied_job_id', flat=True)
            accepted_jobs=[]
            applied_job = PostjobModel.objects.exclude(id__in=applied_by_user) 
          
            if category_data:
                applied_job=PostjobModel.objects.filter(category_type__in=category_data).exclude(id__in=applied_by_user) 

            elif jobtype_data:
                applied_job=PostjobModel.objects.filter(job_type__in=jobtype_data).exclude(id__in=applied_by_user)

            elif skills_data:
                applied_job=PostjobModel.objects.filter(skills__in=skills_data).exclude(id__in=applied_by_user)

            else:
                applied_job = PostjobModel.objects.exclude(id__in=applied_by_user)
            #if request.GET;

            for accepted_job in PostjobModel.objects.all():

                try:
                    bid=BidAmountModel.objects.get(job=accepted_job)
                
                    if bid.is_accepted:
                        accepted_jobs.append(accepted_job)

                    else:
                        continue

                except Exception as e:
                    pass
                
            
            # applied_job = PostjobModel.objects.exclude(id__in=applied_by_user) 
            jobs_applied = PostjobModel.objects.filter(id__in=applied_by_user)
            sellers = SellerProfileModel.objects.all()
            exclude_applied_job_dict = {}
            applied_job_dict = {}
          
            new_dict={}
            for alljob in PostjobModel.objects.all():

                try:
                    job =ApplyForJobModel.objects.get(applied_job=alljob)

                except:
                    job = None

                if job and job.buyer==buyer:
                    new_dict[alljob]='applied'
                else:
                    new_dict[alljob]="not applied"



            for data in applied_job:
                seller = SellerProfileModel.objects.get(id=data.seller.id)
                
                try:
                    exclude_applied_job_dict[seller].append(data)
                except:
                    exclude_applied_job_dict[seller] = list()
                    exclude_applied_job_dict[seller].append(data)
            
            for data in jobs_applied:
                seller = SellerProfileModel.objects.get(id=data.seller.id)
                applied_job_dict[seller] = data

            myt = PostjobModel.objects.filter()
            abc = JobFilter(request.GET,queryset=myt)
            
            prodo =   abc.qs
            
            return render(request, 'mainapp/index.html',
                          {
                            'exclude_applied_job': applied_job,
                            'accepted_jobs':accepted_jobs,
                            'jobs_applied': jobs_applied,
                            'profile_type': profile_type,
                            'sellers': sellers,
                            'applied_job': new_dict,
                            'exclude_applied_job_dict': exclude_applied_job_dict,
                            'categories': JobCategoryModel.objects.all(),
                            'jobtype': JobTypeModel.objects.all(),
                            'skills': SkillModel.objects.all(),
                            'prodo': prodo,
                            'myfilter':abc,
                            'applied_by_user':applied_by_user
                              
                          }
                        )
            

        else:
            return redirect('profiletype')

    return render(request, 'mainapp/index.html')

# view for sending the otp to the mail and verify it
def verify_email(request):
    
    if request.method == 'POST':
        otp = request.POST['otp']
        otpuser = OTPModel.objects.filter(otp=otp).first()
        
        if otpuser is not None:
            user = User.objects.get(pk=otpuser.user.id)
            user.is_verified = True
            user.save()
            otpuser.delete()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('profiletype')
    
    return render(request, 'mainapp/verify.html')

#view for the user which profile(client or freelancer) he/she wants
def profile_type(request):
    
    if request.method == 'POST':
        profiletype = request.POST['profiletype']
        login_user_id = request.user.id
        user = User.objects.get(pk=login_user_id)
        
        if profiletype == 'seller':
            return redirect('selleradd')
        
        elif profiletype == 'buyer':
            return redirect('buyeradd')
        
        else:
            return render(request, 'mainapp/profiletype.html', {'message': 'something went wrong please try again'})

    return render(request, 'mainapp/profiletype.html')

#view for the login account
def Login(request):
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
    
        if user is not None:
            user = User.objects.get(pk=user.id)
    
    
            if user.is_verified:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                if not(user.is_seller or user.is_buyer):
                    return redirect('profiletype')
                return redirect('/')
            
            else:
                userotp = OTPModel.objects.filter(user=user)
                if userotp:
                    userotp.delete()
                otp = random.randint(100000, 999999)
                otpmodel = OTPModel(user=user, otp=otp)
                otpmodel.save()
                send_otp_with_celery.delay(username,otp)
                # subject = "OTP Verification From Digibuddies"
                # message = f"Your OTP for Account Verification in Digibuddies is {otp}"
                # send_mail(subject, message, 'tu716599@gmail.com', [username], fail_silently=False)
                return redirect('verify')
        
        else:
            error = 'Please Check your email/password'
            return render(request, 'mainapp/login.html', {'error': error})

    return render(request, 'mainapp/login.html')


#view for registering the user as a buyer or freelancer
@authenticated_user
def buyer_form_view(request):
    
    if request.method == 'POST':
        
        if request.user.is_authenticated:
            form = BuyerForm(request.POST, request.FILES)
            
    
            if 'buyersave' in request.POST:
                
                if form.is_valid():
                    address = form.cleaned_data['address']
                    # skills=form.cleaned_data['skills']
                    profile_desc = form.cleaned_data['profile_desc']
                    linkedin_profile = form.cleaned_data['linkedin_profile']
                    github_profile = form.cleaned_data['github_profile']
                    profile_picture = form.cleaned_data['profile_picture']
                    resume = form.cleaned_data['resume']
                    city = form.cleaned_data['city']
                    state = form.cleaned_data['state']
                    country = form.cleaned_data['country']
                    gender = request.POST['gender']
                    skills = request.POST.getlist('skills')
                    long_description = form.cleaned_data['long_description']
                    user = request.user
                    buyer = BuyerProfileModel(user=user, address=address, profile_desc=profile_desc, linkedin_profile=linkedin_profile, github_profile=github_profile,
                                            city=city, state=state, country=country, profile_picture=profile_picture, resume=resume, gender=gender, long_description=long_description)
                    buyer.save()
                    user = User.objects.get(pk=request.user.id)
            
                    user.is_buyer = True
                    user.save()
                    buyer_skill_model = SkillModel.objects.filter(skill_title__in=skills)
                    # for data in job_type_obj:
                    buyer.skills.set(buyer_skill_model)
                    buyer.save()
                    return redirect('index')
                else:
                    pass

            if request.POST.get('skill_added'):
                form = BuyerForm()
                skilladd=SkillModel()
                skilltoadd=request.POST.get('skill_added')
                if not SkillModel.objects.filter(skill_title=skilltoadd):
                    skilladd.skill_title=skilltoadd
                    skilladd.skill_desc=skilltoadd
                    skilladd.save()
                else:
                    messages.success(request,"Its already Exists")
                skill_type = SkillModel.objects.all()
                return render(request, 'buyer/buyerform.html', {'form': form, 'skills': skill_type})
            
            else:
                print(form.errors)
    
    else:
        form = BuyerForm()
    
    skills = SkillModel.objects.all()
    return render(request, 'buyer/buyerform.html', {'form': form, 'skills': skills})



# view for seller or client for posting a new job
@authenticated_user
@seller_role_required
def post_job_view(request):
    
    if request.method == 'POST':
        form = PostJobForm(request.POST)
        user = User.objects.get(pk=request.user.id)
        seller = SellerProfileModel.objects.get(user=user)
        userstr=user.first_name
        
        if request.POST.get('skill_added'):
            form = PostJobForm()
            skilladd=SkillModel()
            skilltoadd=request.POST.get('skill_added')
            if not SkillModel.objects.filter(skill_title=skilltoadd):
                skilladd.skill_title=skilltoadd
                skilladd.skill_desc=skilltoadd
                skilladd.save()
            else:
                messages.success(request,"Its already Exists")
            job_type = JobTypeModel.objects.all()

            category_type = JobCategoryModel.objects.all()
            skill_type = SkillModel.objects.all()
            return render(request, 'seller/postjob.html', {'form': form, 'job_type': job_type, 'category_type': category_type, 'skill_type': skill_type})
    
        if request.POST.get('job_added'):
            form = PostJobForm()
            jobtypeadd=JobTypeModel()
            jobtoadd=request.POST.get('job_added')
            if not JobTypeModel.objects.filter(job_type_title=jobtoadd):
                jobtypeadd.job_type_title=jobtoadd
                jobtypeadd.job_type_desc=jobtoadd
                jobtypeadd.save()
            else:
                messages.success(request,"Its already Exists")
            job_type = JobTypeModel.objects.all()

            category_type = JobCategoryModel.objects.all()
            skill_type = SkillModel.objects.all()
            return render(request, 'seller/postjob.html', {'form': form, 'job_type': job_type, 'category_type': category_type, 'skill_type': skill_type})
    
        if request.POST.get('cat_added'):
            form = PostJobForm()
            categoryadd=JobCategoryModel()
            cattoadd=request.POST.get('cat_added')
            if not JobCategoryModel.objects.filter(category_title=cattoadd):
                categoryadd.category_title=cattoadd
                categoryadd.category_desc=cattoadd
                categoryadd.save()

            else:
                messages.success(request,"Its already Exists")
            job_type = JobTypeModel.objects.all()

            category_type = JobCategoryModel.objects.all()
            skill_type = SkillModel.objects.all()
            return render(request, 'seller/postjob.html', {'form': form, 'job_type': job_type, 'category_type': category_type, 'skill_type': skill_type})


    
        if form.is_valid():
            job_title = form.cleaned_data['job_title']
            short_desc = form.cleaned_data['short_desc']
            full_desc = form.cleaned_data['full_desc']
            skill_list = request.POST.getlist('skills')
            job_type_list = request.POST.getlist('job_type')
            category_type_list = request.POST.getlist('category_type')
            deadline = form.cleaned_data['deadline']
            askamount = form.cleaned_data['askamount']
            post_job = PostjobModel(seller=seller, job_title=job_title, short_desc=short_desc,
                                    full_desc=full_desc, deadline=deadline, askamount=askamount)
            post_job.save()

            skill_type_obj = SkillModel.objects.filter(skill_title__in=skill_list)
            post_job.skills.set(skill_type_obj)
            post_job.save()

            job_type_obj = JobTypeModel.objects.filter(job_type_title__in=job_type_list)
            post_job.job_type.set(job_type_obj)
            post_job.save()

            category_type_obj = JobCategoryModel.objects.filter(category_title__in=category_type_list)
            post_job.category_type.set(category_type_obj)
            post_job.save()
            
            send_postjob_with_celery.delay(userstr)
            # for buyer in buyerpush:
            #     send_user_notification(user=buyer.user, payload=payload, ttl=1000)
            return redirect('index')


        
    
    else:
        form = PostJobForm()
    
    job_type = JobTypeModel.objects.all()

    category_type = JobCategoryModel.objects.all()
    skill_type = SkillModel.objects.all()
    return render(request, 'seller/postjob.html', {'form': form, 'job_type': job_type, 'category_type': category_type, 'skill_type': skill_type})

# view for freelancer or buyer for viewing the list of all jobs
@authenticated_user
def apply_job_view(request):
    user = User.objects.get(pk=request.user.id)
    buyer = BuyerProfileModel.objects.get(user=user)
    alljob = PostjobModel.objects.all()
    
    
    accepted_jobs = BidAmountModel.objects.filter(is_accepted=True)
    
   
    alljoba = alljob.exclude(id__in=accepted_jobs.values('job_id'))
    
    
    return render(request, 'buyer/applyjob.html', {'applied_job': alljoba})


# view for freelancer or buyer for applying a job on apply form
@buyer_role_required
def apply_job_form_view(request, id=None,slug=None):
    
    if request.method == 'POST':
    
        if request.user.is_authenticated:
            form = ApplyJobForm(request.POST, request.FILES)
            if form.is_valid():
                pitch = form.cleaned_data['pitch']
                bidamount = form.cleaned_data['bidamount']
                applied_job = PostjobModel.objects.get(slug=slug)
                user = User.objects.get(pk=request.user.id)
                buyer = BuyerProfileModel.objects.get(user=user.id)
                seller = SellerProfileModel.objects.get(pk=applied_job.seller.id)
                job_application = ApplyForJobModel(buyer=buyer, seller=seller, pitch=pitch,
                                                   bidamount=bidamount, applied_job=applied_job)
                job_application.save()
                bid = BidAmountModel(job=applied_job, bidder=buyer, bid_amount=bidamount,pitch=pitch)
                bid.save()

                recipient = request.user
                link = '/seller/job_detail/' + applied_job.slug
        
                notify.send(recipient, recipient=seller.user, verb='Applied for your job',description='Someone Applied for your job' ,cta_link=link)
                payload = {"head": "Apply Bid", "body": user.first_name + " applied for your job","url":"/seller/job_detail/"+applied_job.slug}

                send_user_notification(user=seller.user, payload=payload, ttl=1000)
                return redirect('index')
            else:
                applied_job = PostjobModel.objects.get(slug=slug)
                skills = SkillModel.objects.all()
                return render(request, 'buyer/applyjobform.html', {'applied_job': applied_job, 'form': form, 'skills': skills})

    else:
        form = ApplyJobForm()
        applied_job = PostjobModel.objects.get(slug=slug)
        skills = SkillModel.objects.all()
    
    return render(request, 'buyer/applyjobform.html', {'applied_job': applied_job, 'form': form, 'skills': skills})

#view for seller for view the profile details of buyer or freelancer
@authenticated_user
def buyer_details_view(request, id):
    buyer_detail = BuyerProfileModel.objects.get(pk=id)

    return render(request, 'buyer/buyerdetail.html', {'buyer_detail': buyer_detail})

# view for seller to view or display the job he/she has posted
@authenticated_user
def listjobs(request):
    user = User.objects.get(pk=request.user.id)
    seller = SellerProfileModel.objects.get(user=user)
    
    try:
        posted_jobs = PostjobModel.objects.filter(seller=seller)
    except:
        posted_jobs = None
    
    bid_dict = {}
    
    for data in posted_jobs:
        bid_obj = BidAmountModel.objects.filter(job=data)
        bid_dict[data] = bid_obj
    

    return render(request, 'seller/listjobs.html', {'bid_dict': bid_dict})

# View for both freelancer(buyer ) and client(seller) for viewing the job details
@authenticated_user
def job_detail(request, slug=None):
    posted_job = PostjobModel.objects.get(slug=slug)
    bid_obj = BidAmountModel.objects.filter(job=posted_job)
    
   

    return render(request, 'seller/jobdetail.html', {'posted_job': posted_job, 'bid_details': bid_obj})
   
    

# view for the freelancer(buyer ) for view all the jobs he/she applied
@authenticated_user
def proposals_list(request):
    user = User.objects.get(pk=request.user.id)
    buyer = BuyerProfileModel.objects.get(user=user)
    applied_by_user = ApplyForJobModel.objects.filter(buyer=buyer)
    data_dict = {}
    accepted_jobs=[]

    for data in applied_by_user:
        job = PostjobModel.objects.get(id=data.applied_job.id)

        try:
            accepted=BidAmountModel.objects.get(job=job)

            if accepted.is_accepted:
                accepted_jobs.append(job)
            
        except:
            pass

        finally:
            data_dict[job] = ApplyForJobModel.objects.get(buyer=buyer,applied_job=job)
 

    return render(request, 'buyer/proposedserviceslist.html', {'applied_by_user': data_dict,'accepted_jobs':accepted_jobs})

# view for adding the seller (client) profile
@authenticated_user
def seller_form_view(request):
    if request.method == 'POST':
    
        if request.user.is_authenticated:

            form = SellerForm(request.POST, request.FILES)
    
            if form.is_valid():
                company_logo = form.cleaned_data['company_logo']
                company_name = form.cleaned_data['company_name']
                company_email = form.cleaned_data['company_email']
                company_address = form.cleaned_data['company_address']
                city_of_company = form.cleaned_data['city_of_company']
                country_of_company = form.cleaned_data['country_of_company']
                company_phone_number = form.cleaned_data['company_phone_number']
                company_desc = form.cleaned_data['company_desc']
                user = request.user
        
                seller = SellerProfileModel(user=user, company_logo=company_logo, company_name=company_name, company_address=company_address, city_of_company=city_of_company,
                                            country_of_company=country_of_company, company_email=company_email, company_phone_number=company_phone_number, company_desc=company_desc)
                seller.save()
        
                user = User.objects.get(pk=request.user.id)
                user.is_seller = True
                user.save()
                return redirect('index')

    else:
        form = SellerForm()
    
    return render(request, 'seller/sellerform.html', {'form': form})



# google login redirect view to the profile type
def google_user_redirect_view(request):
    
    if request.user.is_authenticated:
        login_user_id = request.user.id
        user = User.objects.get(pk=login_user_id)
        user.is_verified = True
        user.save()
    
        if request.user.is_seller or request.user.is_buyer:
            return redirect('index')
    
        else:
    
            if request.method == 'POST':
                profiletype = request.POST['profiletype']
    
                if profiletype == 'seller':
                    return redirect('selleradd')
    
                elif profiletype == 'buyer': 
                    return redirect('buyeradd')
    
                else:
                    return render(request, 'mainapp/profiletype.html', {'message': 'something went wrong please try again'})

    return render(request, 'mainapp/profiletype.html')

#client(seller) view to edit the job or update it
@authenticated_user
@seller_role_required

def seller_job_update_form(request,slug):
    job_update_detail=PostjobModel.objects.get(slug=slug)
    if request.method=="POST":
        form = PostJobForm(request.POST, instance=job_update_detail)
        user = User.objects.get(pk=request.user.id)
        seller = SellerProfileModel.objects.get(user=user)


        if request.POST.get('skill_added'):
            form = PostJobForm(instance=job_update_detail)
            skilladd=SkillModel()
            skilltoadd=request.POST.get('skill_added')
            if not SkillModel.objects.filter(skill_title=skilltoadd):
                skilladd.skill_title=skilltoadd
                skilladd.skill_desc=skilltoadd
                skilladd.save()
            else:
                messages.success(request,"Its already Exists")
            job_type = JobTypeModel.objects.all()

            
            category_type = JobCategoryModel.objects.all()
            skill_type = SkillModel.objects.all()
            return render(request, 'seller/sellerjobupdate.html', {'form': form, 'job_type': job_type, 'category_type': category_type, 'skills': skill_type,'selected_skills':job_update_detail.skills.all,'selected_jobs':job_update_detail.job_type.all,'selected_category':job_update_detail.category_type.all})
    
        if request.POST.get('job_added'):
            form = PostJobForm(instance=job_update_detail)
            jobtypeadd=JobTypeModel()
            jobtoadd=request.POST.get('job_added')
            if not JobTypeModel.objects.filter(job_type_title=jobtoadd):
                jobtypeadd.job_type_title=jobtoadd
                jobtypeadd.job_type_desc=jobtoadd
                jobtypeadd.save()
            else:
                messages.success(request,"Its already Exists")
            job_type = JobTypeModel.objects.all()

            
            category_type = JobCategoryModel.objects.all()
            skill_type = SkillModel.objects.all()
            return render(request, 'seller/sellerjobupdate.html', {'form': form, 'job_type': job_type, 'category_type': category_type, 'skills': skill_type,'selected_skills':job_update_detail.skills.all,'selected_jobs':job_update_detail.job_type.all,'selected_category':job_update_detail.category_type.all})
    
        if request.POST.get('cat_added'):
            form = PostJobForm(instance=job_update_detail)
            categoryadd=JobCategoryModel()
            cattoadd=request.POST.get('cat_added')
            if not JobCategoryModel.objects.filter(category_title=cattoadd):
                categoryadd.category_title=cattoadd
                categoryadd.category_desc=cattoadd
                categoryadd.save()

            else:
                messages.success(request,"Its already Exists")
            job_type = JobTypeModel.objects.all()

            category_type = JobCategoryModel.objects.all()
            skill_type = SkillModel.objects.all()
            return render(request, 'seller/sellerjobupdate.html', {'form': form, 'job_type': job_type, 'category_type': category_type, 'skills': skill_type,'selected_skills':job_update_detail.skills.all,'selected_jobs':job_update_detail.job_type.all,'selected_category':job_update_detail.category_type.all})

        if 'update_job_form' in request.POST:
            if form.is_valid():
                job_update_detail.job_title = form.cleaned_data['job_title']
                job_update_detail.short_desc = form.cleaned_data['short_desc']
                job_update_detail.full_desc = form.cleaned_data['full_desc']
                skill_list = request.POST.getlist('skills')
                job_type_list = request.POST.getlist('job_type')
                category_type_list = request.POST.getlist('category_type')
                job_update_detail.deadline = form.cleaned_data['deadline']
                job_update_detail.askamount = form.cleaned_data['askamount']

                job_update_detail.save()

                skill_type_obj = SkillModel.objects.filter(skill_title__in=skill_list)
                job_update_detail.skills.set(skill_type_obj)
                job_update_detail.save()

                job_type_obj = JobTypeModel.objects.filter(job_type_title__in=job_type_list)
                job_update_detail.job_type.set(job_type_obj)
                job_update_detail.save()

                category_type_obj = JobCategoryModel.objects.filter(category_title__in=category_type_list)
                job_update_detail.category_type.set(category_type_obj)
                job_update_detail.save()
                messages.success(request, "Your Job has been Updated.")
                job_type = JobTypeModel.objects.all()

                category_type = JobCategoryModel.objects.all()
                skill_type = SkillModel.objects.all()
                return render(request, 'seller/sellerjobupdate.html', {'form': form, 'job_type': job_type, 'category_type': category_type, 'skills': skill_type,'selected_skills':job_update_detail.skills.all,'selected_jobs':job_update_detail.job_type.all,'selected_category':job_update_detail.category_type.all})
            else:
                pass
    
    else:
        form = PostJobForm(instance=job_update_detail)
    
    job_type = JobTypeModel.objects.all()

    category_type = JobCategoryModel.objects.all()
    skill_type = SkillModel.objects.all()
    return render(request, 'seller/sellerjobupdate.html', {'form': form, 'job_type': job_type, 'category_type': category_type, 'skills': skill_type,'selected_skills':job_update_detail.skills.all,'selected_jobs':job_update_detail.job_type.all,'selected_category':job_update_detail.category_type.all})

#freelancer(buyer ) view for  updating the bid
@buyer_role_required
def apply_job_update_view(request,id=None,slug=None):
    applied_bid=ApplyForJobModel.objects.get(pk=id)
    if request.method == 'POST':

        if request.user.is_authenticated:
            form = ApplyJobForm(request.POST, request.FILES,instance=applied_bid)
    
            if form.is_valid():
                applied_bid.pitch = form.cleaned_data['pitch']
                applied_bid.bidamount = form.cleaned_data['bidamount']
                applied_job = PostjobModel.objects.get(slug=slug)
                user = User.objects.get(pk=request.user.id)
                buyer = BuyerProfileModel.objects.get(user=user.id)
                seller = SellerProfileModel.objects.get(pk=applied_job.seller.id)
                applied_bid.save()
                bid = BidAmountModel.objects.get(job=applied_job, bidder=buyer)
                bid.bid_amount=applied_bid.bidamount
                bid.save()
                recipient = request.user
                link = '/seller/job_detail/' + applied_job.slug
        
                notify.send(recipient, recipient=seller.user, verb='Updated his applied job',description='This job has been updated by the user' ,cta_link=link)


                payload = {"head": "Bid Updated", "body": user.first_name + " updated his bid","url":'/seller/job_detail/' + applied_job.slug}

                send_user_notification(user=seller.user, payload=payload, ttl=1000)
                messages.success(request, "Your Bid has been Updated.")
                form = ApplyJobForm(instance=applied_bid)

                applied_job = PostjobModel.objects.get(slug=slug)
                skills = SkillModel.objects.all()
    
                return render(request, 'buyer/updatebid.html', {"applied_job": applied_job, 'form': form, 'skills': skills})
                

    else:
        form = ApplyJobForm(instance=applied_bid)

        applied_job = PostjobModel.objects.get(slug=slug)
        skills = SkillModel.objects.all()
    
    return render(request, 'buyer/updatebid.html', {"applied_job": applied_job, 'form': form, 'skills': skills})

# view for seller(client ) for deleting a job
class delete_job(DeleteView):
    model=PostjobModel
    success_url=''
    template_name='seller/jobdelete.html'

# Static funtion  
def payment(request,bid_obj):
   
    
    try: 
        abcds = BidAmountModel.objects.filter(id=bid_obj)
        
        total_amount = abcds.values("bid_amount")[0]['bid_amount']
        
    
        client = razorpay.Client(auth=(settings.KEY,settings.SECRET) )
        payment =  client.order.create({'amount': int(total_amount) * 100, 'currency':'INR', "payment_capture":1 })

    except:
        payment = None

    return HttpResponse(json.dumps(payment))

def successd(request):
    if request.method == "POST": 
        data = request.POST
        buyer_id=data['bidder']
        buyer_model=BuyerProfileModel.objects.get(id=buyer_id)
        buyer_name=buyer_model.user
     
        
        user=request.user
    
        if data['check'] == "success":
            recipient = request.user
            link = '/buyer/proposals/'
            notify.send(recipient, recipient=buyer_name, verb='payed you',description='Your Job has been accepted and the user payed you ' ,cta_link=link)
            payload = {"head": "Payment to you", "body": user.first_name + " payed you","url":"/buyer/proposals/"}

            send_user_notification(user=buyer_name, payload=payload, ttl=1000)


        alldata=data.keys()
        if data['check'] == "success":

            payment_credationals = Payment.objects.create(seller_id = SellerProfileModel.objects.get(user=request.user).id,
                                                        bidder_id = int(data['bidder']),
                                                        order_id =str(data['order_id']),
                                                        payment_id = str(data['payement_id']),
                                                        payment_signature = str(data['signarture_id']),
                                                        amount = int(data['amount']),
                                                        job_id = int(data['job']))
            payment_credationals.save()
            return render(request,"seller/success.html")
        elif data['check'] == "failed":
            error = request.POST
           
            payment_error = Payment.objects.create(seller_id = SellerProfileModel.objects.get(user=request.user).id,
                                                        bidder_id = int(data['bidder']),
                                                        order_id =str(data['order_id']),
                                                        payment_id = str(data['payement_id']),
                                                        paymentReport = False,
                                                        amount = int(data['amount']),
                                                        job_id = int(data['job']))
            payment_error.save()

            return render(request,"seller/error.html")
            
    else:
        return render(request,"seller/success.html")


def Error(request):
    return render(request,"seller/error.html")

# seller(client)  view for accepting the bid(proposal ) make by buyer(freelancer)
@authenticated_user
def accept_proposal(request,id):
    accepted=BidAmountModel.objects.get(pk=id)
    accepted.is_accepted=True
    accepted.save()
    recipient = request.user
    notify.send(recipient, recipient=accepted.bidder.user, verb='Accepted Your Job proposal',description='Your Proposal is accepted by client' ,cta_link='/buyer/proposals/')
    payload = {"head": "Welcome!", "body": "Your Proposal has been Accepted","url":"/buyer/proposals/"}

    send_user_notification(user=accepted.bidder.user, payload=payload, ttl=1000)
    return redirect('index')

#exception page
def page_not_found_view(request, exception):
    return render(request, 'mainapp/404.html', status=404)

#buyer(Freelancer ) view to updating its profile 
@buyer_role_required
def buyer_profile_update_form(request):
    payment_record = Payment.objects.filter(bidder_id = BuyerProfileModel.objects.get(user=request.user))
    
    user = User.objects.get(pk=request.user.id)
    buyer = BuyerProfileModel.objects.get(user=user)

    if request.method == 'POST':
        form = BuyerForm(request.POST, request.FILES, instance=buyer)
        
       
        if 'profile_update' in request.POST:
            if form.is_valid():
                try:
                    buyer.profile_picture = form.cleaned_data['profile_picture']
                except:
                    pass

                try:
                    buyer.resume = form.cleaned_data['resume']
                except:
                    pass

                buyer.address = form.cleaned_data['address']
                buyer.profile_desc = form.cleaned_data['profile_desc']
                buyer.linkedin_profile = form.cleaned_data['linkedin_profile']
                buyer.github_profile = form.cleaned_data['github_profile']
                buyer.city = form.cleaned_data['city']
                buyer.state = form.cleaned_data['state']
                buyer.country = form.cleaned_data['country']
                buyer.gender = request.POST['gender']
                skills_list = request.POST.getlist('skills')
                buyer.long_description = form.cleaned_data['long_description']
                buyer.save()
                buyer_skill_model = SkillModel.objects.filter(skill_title__in=skills_list)
                buyer.skills.set(buyer_skill_model)
                buyer.save()
                messages.success(request, "Your Profile has been Updated.")
                skills = SkillModel.objects.all()
                return render(request, 'buyer/profile_description.html', {'form': form, 'profile_picture': buyer.profile_picture, 'resume': buyer.resume, 'selected_skills': buyer.skills.all, 'skills': skills})
            else:
                print(form.errors)


        if request.POST.get('skill_added'):
            form = BuyerForm(instance=buyer)
            skilladd=SkillModel()
            skilltoadd=request.POST.get('skill_added')
            if not SkillModel.objects.filter(skill_title=skilltoadd):
                skilladd.skill_title=skilltoadd
                skilladd.skill_desc=skilltoadd
                skilladd.save()
            else:
                messages.success(request,"Its already Exists")
            skills = SkillModel.objects.all()
            return render(request, 'buyer/profile_description.html', {'user':user,'form': form, 'profile_picture': buyer.profile_picture, 'resume': buyer.resume, 'selected_skills': buyer.skills.all, 'skills': skills})

        if 'pwd_upd' in request.POST:
            form = BuyerForm(instance=buyer)
            if request.POST['password']==request.POST['confirm']:
                u=request.user
                u.set_password(request.POST['password'])
                update_session_auth_hash(request, u)
                u.save()
                messages.success(request,"Your password has been updated")
            else:
                messages.error(request,"Password Doesn't match")
                
    
    else:
        form = BuyerForm(instance=buyer)
    
    skills = SkillModel.objects.all()
    return render(request, 'buyer/profile_description.html', {'user':user,'form': form, 'profile_picture': buyer.profile_picture, 'resume': buyer.resume, 'selected_skills': buyer.skills.all, 'skills': skills,"payment_record":payment_record})

# view for display all the payments
@seller_role_required
def All_Payments(request):
    data = Payment.objects.filter(seller_id = SellerProfileModel.objects.get(user=request.user))
    try:
        raw = data.values()
        print(raw[0],"---------")
        transfer_amount = 0
        for i in data:
            if i.paymentReport == True:
                transfer_amount += i.amount
        return render(request,"seller/payment_details.html",{"data":data,"transfer_amount":transfer_amount})
    except:
        return render(request,"seller/payment_details.html",{"data":data})
    
# seller(client ) view for updating its profile 
@seller_role_required
def seller_profile_update_form(request,slug=None):
    find_user = Payment.objects.filter(seller_id = SellerProfileModel.objects.get(user=request.user))
    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id)
        seller = SellerProfileModel.objects.get(user=user)
    
        if request.method == 'POST':
            if 'profile_update' in request.POST:
                form = SellerForm(request.POST, request.FILES, instance=seller)
        
                if form.is_valid():
        
                    if form.cleaned_data['company_logo']:
                        seller.company_logo = form.cleaned_data['company_logo']
                    seller.company_name = form.cleaned_data['company_name']
                    seller.company_email = form.cleaned_data['company_email']
                    seller.company_address = form.cleaned_data['company_address']
                    seller.city_of_company = form.cleaned_data['city_of_company']
                    seller.country_of_company = form.cleaned_data['country_of_company']
                    seller.company_phone_number = form.cleaned_data['company_phone_number']
                    seller.company_desc = form.cleaned_data['company_desc']
                    seller.save()
                    messages.success(request, "Your Profile has been Updated.")
                    return render(request, 'seller/profile_desc.html', {'form': form, 'company_logo': seller.company_logo})
        
                else:
                    print(form.errors)
            else:
                form = BuyerForm(instance=seller)
                if request.POST['password']==request.POST['confirm']:
                    u=request.user
                    u.set_password(request.POST['password'])
                    update_session_auth_hash(request, u)
                    u.save()
                    messages.success(request,"Your password has been updated")
                else:
                    messages.error(request,"Password Doesn't match")
    
        else:
            form = SellerForm(instance=seller)
        return render(request, 'seller/profile_desc.html', {'form': form, 'company_logo': seller.company_logo,"data":find_user})
    
    else:
        return redirect('login')

# notifications view for viewing the notifications for both buyer and seller 
def notifications(request):
    notified = NotificationCTA.objects.filter(notification__recipient=request.user)
    return render(request,'mainapp/notifications.html',{'notify':notified})

# view for notifications to set them as a read 
def mark_as_read(request, slug=None):
    notification_id = slug2id(slug)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id)
    notification.mark_as_read()
    return redirect('notifications')

# view for deleting the notifications for both buyer and seller 
def delete_notification(request, slug=None):
    notification_id = slug2id(slug)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id)
    notification.delete()

    return redirect('notifications')


#django channels for chat bw sender and reciever
# @authenticated_user
# def index_view(request):
#     return render(request, 'mainapp/chat.html', {
#         'rooms': Room.objects.all(),
#     })

# @authenticated_user
# def room_view(request, room_name):
#     chat_room, created = Room.objects.get_or_create(name=room_name)
#     prev_message=Message.objects.filter(room=chat_room).order_by('timestamp')
#     return render(request, 'mainapp/chatroom.html', {
#         'room': chat_room,
#         'prev_messages':prev_message
#     })

def onlyfilters(request):
    myt = PostjobModel.objects.filter()
    abc = alljobfilter(request.GET,queryset=myt)
            
    prodo =   abc.qs
    return render(request,'buyer/jobsfilter.html',{'formfilter':abc,'prodo':prodo})
# ------------------- code by rishi ----------

def custom_admin(request):
    if request.method == "GET":
        
        instance = BuyerProfileModel.objects.all()
        context = {
            "data":instance
        }
        return render(request,"seller/custom_admin.html",context)

def Block_Unblock(request):
    """ this function is used to block  and unblock user/client """
    if request.method == "GET":
        raw = request.GET['keyy']
        instance = User.objects.get(id = raw)
        if instance.is_active == True:
            instance.is_active = False
            instance.save()
            send_mail_wiht_celery.delay(instance.email,request.GET['msg'])
        elif instance.is_active == False:
            instance.is_active = True
            instance.save()
            send_mail_wiht_celery.delay(instance.email,request.GET['msg'])
            
            
        return JsonResponse({"status":"success"})
    
def aadmin(request):
    if request.method == "GET":
        instance = BuyerProfileModel.objects.all()
        context = {
            "data":instance
        }
        return render(request,"custom-admin/index.html",context)
from django.contrib.auth.decorators import user_passes_test  
@user_passes_test(lambda u: u.is_admin) 
def table(request):
    """ this function return freelancer data """
    if request.method == "GET":
        sid = request.user.id
        instance = User.objects.get(id = sid)
        if instance.is_admin == True:
            client_instance = SellerProfileModel.objects.exclude(user=instance)
            print(client_instance,"------------")
        
        freelancer_instance = BuyerProfileModel.objects.all()
        # client_instance = SellerProfileModel.objects.all()
        context = {
            "data":freelancer_instance,
            "client":client_instance
        }
        return render(request,"custom-admin/tables.html",context)
    
def All_jobs(request):
    """ This function show all jobs on  custom-admin page """
    if request.method == "GET":
        instance = PostjobModel.objects.all()
        context = {
            "jobs":instance
            }
        return render(request,"custom-admin/Jobs.html",context)
    
def custom_payment(request):
    """ This function fetch the all payment database """
    if request.method == "GET":
        instance = Payment.objects.all()
        context = {
            'all_payments':instance
        }
        return render(request,"custom-admin/payment.html",context)

def custom_biding_UI(request):
    """ this function return the bidding  """
    if request.method == "GET":
        instance = BidAmountModel.objects.all()
        context = {
            'all_bidings':instance
        }
        return render(request,"custom-admin/biding.html",context)


# def private_chat_home(request):
#     users = User.objects.exclude(email=request.user)
#     return render(request, 'mainapp/chatroom.html', context={'users': users})

# def chatPage(request, username):
#     user_obj = User.objects.get(first_name=username)
#     users = User.objects.exclude(email=request.user.email)
#     if request.method =="POST":
#         img = request.FILES.getlist('files[]',None)
#         fullfile=img[0]
#         strfullfile=str(fullfile)
#         # print(files,"======--------")
#         # img=request.FILES['file_upload']
#         print(strfullfile) 
#         ext = strfullfile.split('.')[-1]
#         a=''
#         if ext == 'jpeg' or ext =='png' or ext == "jpg" or ext =="img" :
#             a='image'
#         elif ext == 'mp4':
#             a='video'
#         else:
#             a='others'
#         print()
#         if request.user.id > user_obj.id:
#             thread_name = f'chat_{request.user.id}-{user_obj.id}'
#         else:
#             thread_name = f'chat_{user_obj.id}-{request.user.id}'
#         image_save=FileUpload(files_upload=img[0])
#         image_save.save()
#         return JsonResponse({'url':image_save.files_upload.url,'msgtype':a})


    
#     if request.user.is_authenticated:

#         if request.user.id > user_obj.id:
#             thread_name = f'chat_{request.user.id}-{user_obj.id}'
#         else:
#             thread_name = f'chat_{user_obj.id}-{request.user.id}'
#         message_objs = ChatModel.objects.filter(thread_name=thread_name)
#         print(message_objs)

#         return render(request, 'mainapp/chat.html', context={'user' : f"{user_obj.id}" ,'users': users, 'messages' : message_objs, 'username' : user_obj, 'count' : len(message_objs)})
#     else:
#         return render(request, 'mainapp/chatroom.html')



