from django import forms
from django.core.exceptions import ValidationError
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import User,SellerProfileModel,BuyerProfileModel,ApplyForJobModel,PostjobModel
from django_countries.widgets import CountrySelectWidget

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class':'form-control','id':'password1','placeholder':'Enter your password'}))
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput(attrs={'class':'form-control','id':'password2','placeholder':'Confirm your password'}))

    class Meta:
        model = User
        fields = ('email', 'first_name','last_name')
        widgets = {
            'email':forms.EmailInput(attrs={'class':'form-control','id':'email','placeholder':'Enter your email'}),
            'first_name':forms.TextInput(attrs={'class':'form-control','id':'first_name','placeholder':'Enter your first name'}),
            'last_name':forms.TextInput(attrs={'class':'form-control','id':'last_name','placeholder':'Enter your last name'}),
        }

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    
class SellerForm(forms.ModelForm):
    class Meta:
        model=SellerProfileModel
        fields=['company_name','company_logo','city_of_company','country_of_company','company_email','company_address','company_phone_number','company_desc']
        widgets={
            'company_email':forms.EmailInput(attrs={'class':'form-control','id':'company_email','placeholder':"Enter your Company's email"}),
            'company_logo':forms.FileInput(attrs={
                'class':'form-control','id':'company_logo'
            }),
             'city_of_company':forms.TextInput(attrs={'class':'form-control','id':'city_of_company','placeholder':"Enter your Company's City"}),
              'country_of_company':CountrySelectWidget(),
            'company_name':forms.TextInput(attrs={'class':'form-control','id':'company_name','placeholder':"Enter your Company's name"}),
            'company_address':forms.TextInput(attrs={'class':'form-control','id':'company_address','placeholder':"Enter your Company's address"}),
            'company_phone_number':forms.TextInput(attrs={'class':'form-control','id':'company_phone_number','placeholder':"Enter your Company's phone number name"}),
            'company_desc':CKEditorUploadingWidget(attrs={'class':'form-control','id':'company_desc','placeholder':"Enter a detailed description about your company"}),
        }
    
    def clean_company_phone_number(self):
        company_phone_number=self.cleaned_data['company_phone_number']
        if len(company_phone_number) != 10:
            raise ValidationError('Phone Number must be of 10 digits')
        return company_phone_number

class BuyerForm(forms.ModelForm):
    class Meta:
        model=BuyerProfileModel
        fields=['address','city','country','state','profile_desc','linkedin_profile','github_profile','profile_picture','resume','long_description']
        widgets={
            'address':forms.TextInput(attrs={'class':'form-control','id':'address','placeholder':"Enter your address"}),
            'city':forms.TextInput(attrs={'class':'form-control','id':'city','placeholder':"Enter your city"}),
            'country':CountrySelectWidget(),
            'state':forms.TextInput(attrs={'class':'form-control','id':'state','placeholder':"Enter your state"}),
            'profile_desc':forms.TextInput(attrs={'class':'form-control','id':'profile_desc','placeholder':"profile description"}),
            'linkedin_profile':forms.TextInput(attrs={'class':'form-control','id':'linkedin_profile','placeholder':"Enter your linkedin profile"}),
            'github_profile':forms.TextInput(attrs={'class':'form-control','id':'github_profile','placeholder':"Enter your github profile"}),
            'profile_picture':forms.FileInput(attrs={'class':'form-control','id':'profile_picture'}),
            'resume':forms.FileInput(attrs={'class':'form-control','id':'resume'}),
            'long_description':CKEditorUploadingWidget(attrs={'class':'form-control','id':'long_description','placeholder':"Enter a detailed description about yourself",'style':'width: 100%'}),
        }

class PostJobForm(forms.ModelForm):
    class Meta:
        model=PostjobModel
        fields=['job_title','short_desc','full_desc','deadline','askamount']
        widgets={
            'job_title':forms.TextInput(attrs={'class':'form-control','id':'job_title','placeholder':"Enter your job title"}),
            'short_desc':forms.TextInput(attrs={'class':'form-control','id':'short_desc','placeholder':"Enter short description for your job"}),
            'full_desc':CKEditorUploadingWidget(attrs={'class':'form-control','id':'full_desc','placeholder':"Enter long description for your job"}),
            'deadline':forms.DateTimeInput(attrs={'class':'form-control','id':'deadline','type': 'datetime-local','placeholder':"Enter Deadline for the job"}),
            'askamount':forms.TextInput(attrs={
                'class':'form-control','id':'askamount','placeholder':"Enter your Asking Amount"
            })
            
        }
  

class ApplyJobForm(forms.ModelForm):
    class Meta:
        model=ApplyForJobModel
        fields=['pitch','bidamount']
        widgets={
            'bidamount':forms.TextInput(attrs={'class':'form-control','id':'bidamount','placeholder':'Enter Your Proposal Amount'}),
            'pitch':forms.Textarea(attrs={'class':'form-control','id':'pitch','placeholder':'Enter Your Proposal'}),

        }



