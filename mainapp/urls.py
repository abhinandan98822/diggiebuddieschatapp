from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.urls import re_path



urlpatterns = [
    path('account/register/',views.user_register,name='register'),
    path('',views.index,name="index"),
    path('verification',views.verify_email,name='verify'),
    path('profiletype',views.profile_type,name='profiletype'),
    path('account/login/',views.Login,name='login'),
    path('account/logout/',LogoutView.as_view(next_page='login'),name='logout'),
    path('seller/add/',views.seller_form_view,name='selleradd'),
    path('buyer/add/',views.buyer_form_view,name='buyeradd'),
    path('seller/postjob/',views.post_job_view,name='sellerpostjob'),
    path('buyer/applyjob/',views.apply_job_view,name='buyerapplyjob'),
    path('buyer/applyjobform/<slug:slug>/',views.apply_job_form_view,name='buyerapplyjobform'),
    path('seller/listjobs/',views.listjobs,name='listjobs'),
    path('seller/job_detail/<slug:slug>/',views.job_detail,name='job_detail'),
    path('buyer/details/<int:id>/',views.buyer_details_view,name='buyerdetails'),
    path('buyer/proposals/',views.proposals_list,name='proposals'),
    path('accounts/profile/',views.google_user_redirect_view,name='google_seller_buyer'),
    path('seller/job_update_form/<slug:slug>',views.seller_job_update_form,name='seller_job_update_form'),
    path('buyer/bid_update_form/<int:id>/<slug:slug>',views.apply_job_update_view,name='bid_job_update_form'),
    path('delete/<slug:slug>/',views.delete_job.as_view(),name='delete_job'),
    path('successd',views.successd,name="successd"),
    path('error',views.Error,name='error'),
    path('accept_proposal/<int:id>',views.accept_proposal,name='acceptprop'),
    path('buyer_profile/',views.buyer_profile_update_form,name='profile_update'),
    path('payments/',views.All_Payments,name='pay'),
    path('seller_profile/',views.seller_profile_update_form,name='seller_update'),
    path('notifications',views.notifications,name='notifications'),
    path('paymentfetch/<int:bid_obj>',views.payment,name='paymentfetch'),
    path('notification/markasread/<str:slug>',views.mark_as_read,name='notification_mark_read'),
    path('notification/delete/<str:slug>',views.delete_notification,name='notification_delete'),
    path('jobfilters/',views.onlyfilters,name='jobfilter'),

    #django channels
    
    # new code on custom Admin
    path('custom-admin',views.custom_admin,name='admin_page'),
    path('dd',views.Block_Unblock,name='testt'),
    path("test",views.aadmin,name='aadmin'),
    path("tables",views.table,name='tab'),
    path("client-jobs",views.All_jobs,name='jobs'),
    path("payment-page",views.custom_payment,name = 'pay'),
    path("biddings",views.custom_biding_UI,name = 'bid'),
    # path('chat/', views.index_view, name='chat-index'),
    # path('chat/<str:room_name>/', views.room_view, name='chat-room'),
    # path('chat/', views.private_chat_home, name='chat-index'),
    # path('chat/<str:username>/', views.chatPage, name='chat-room'),
    # path('image/send/',views.Image,name='imageupload')

]


 