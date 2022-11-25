from .models import BuyerProfileModel, User,SellerProfileModel
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.shortcuts import render


def buyer_role_required(func):
    def wrapper_func(request,*args,**kwargs):
        user=User.objects.get(id=request.user.id)
        try:
            buyer=BuyerProfileModel.objects.get(user=user)
            return func(request,*args,**kwargs)
        except:
            return redirect('index')
    return wrapper_func

def seller_role_required(func):
    def wrapper_func(request,*args,**kwargs):
        user=User.objects.get(id=request.user.id)
        if user.is_seller:
            # seller=SellerProfileModel.objects.get(user=user)
            return func(request,*args,**kwargs)
        else:
            return redirect('index')
    return wrapper_func

from django.shortcuts import redirect


def authenticated_user(view_func) :
    def wrapper_func(request, *args, **kwargs):

        if request.user.is_authenticated :
    
            return view_func(request, *args, **kwargs)

        else : 

            return redirect('login')

    return wrapper_func