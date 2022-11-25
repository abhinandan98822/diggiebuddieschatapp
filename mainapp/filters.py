
from django.forms.widgets import TextInput,Select,DateTimeInput,NullBooleanSelect
from django_filters.widgets import RangeWidget
import django_filters





from django_filters import DateFilter, CharFilter,ChoiceFilter,RangeFilter,DateRangeFilter,DateTimeFromToRangeFilter,BooleanFilter

from .models import *





typechoice = JobTypeModel.objects.all().order_by('-id').values_list('id','job_type_title')

typechoice_list=[]

for item in typechoice:

    typechoice_list.append(item)

catchoice = JobCategoryModel.objects.all().order_by('-id').values_list('id','category_title')

catchoices_list=[]

for item in catchoice:

    catchoices_list.append(item)


skillchoice = SkillModel.objects.all().order_by('-id').values_list('id','skill_title')

skillchoices_list=[]

for item in skillchoice:

    skillchoices_list.append(item)





class JobFilter(django_filters.FilterSet):

    job_title = CharFilter(field_name='job_title', label='Job', lookup_expr='icontains', widget=TextInput(attrs={'class': 'form-control','placeholder':'Search Here'}))

    find_job_title = CharFilter(field_name='job_title', label='Job', lookup_expr='icontains', widget=TextInput(attrs={'class': 'form-control'}))
    
    job_type = ChoiceFilter(field_name='job_type', choices=typechoice_list, label='SELECT Job Type', empty_label='All Job types',widget=Select(attrs={'class': 'form-control'}))

    job_category = ChoiceFilter(field_name='category_type', choices=catchoices_list, label='SELECT category', empty_label='All Category',widget=Select(attrs={'class': 'form-control'}))

    skills = ChoiceFilter(field_name='skills', choices=skillchoices_list, label='SELECT Skills', empty_label='All Skills',widget=Select(attrs={'class': 'form-control'}))

    #weight = CharFilter(field_name='weight', label='designNumber', lookup_expr='exact')

    deadline = DateRangeFilter(field_name='deadline',lookup_expr='exact',empty_label='Date',widget=Select(attrs={'class': 'form-control'}))

    #deadline = DateTimeFromToRangeFilter(field_name='deadline',lookup_expr='exact')

    #dateee = DateFilter(field_name='date',lookup_expr='exact')


    class Meta:

        model = PostjobModel

        fields = ['job_title','job_category','deadline','is_completed','job_type','find_job_title','skills']

class MyRangeWidget(RangeWidget):
    def __init__(self, from_attrs=None, to_attrs=None, attrs=None):
        super(MyRangeWidget, self).__init__(attrs)

        if from_attrs:
            self.widgets[0].attrs.update(from_attrs)
        if to_attrs:
            self.widgets[1].attrs.update(to_attrs)

class alljobfilter(django_filters.FilterSet):
    job_title = CharFilter(field_name='job_title', label='Job', lookup_expr='icontains', widget=TextInput(attrs={'placeholder':'Search Here','id':'namesearch'}))
    job_type = ChoiceFilter(field_name='job_type', choices=typechoice_list, label='SELECT Job Type', empty_label='All Job types',widget=Select(attrs={'id':'namesearch'}))
    job_category = ChoiceFilter(field_name='category_type', choices=catchoices_list, label='SELECT category', empty_label='All Category',widget=Select(attrs={'id':'namesearch'}))
    skills = ChoiceFilter(field_name='skills', choices=skillchoices_list, label='SELECT Skills', empty_label='All Skills',widget=Select(attrs={'id':'namesearch'}))
    datefilter=RangeFilter(field_name='askamount',widget=MyRangeWidget(from_attrs={'placeholder':'from'},
    to_attrs={'placeholder':'to'},))

    class Meta:

        model = PostjobModel

        fields = ['job_title','job_category','job_type','datefilter']
