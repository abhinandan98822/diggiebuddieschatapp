#!  download image for OS
FROM python:3.10.7   

#!create working directory
RUN mkdir /Diggie_buddies_chatapp

#! copy the dat
WORKDIR /digibuddies/

#!ADD data to directory
ADD . /digibuddies 

#! install dependencies  
RUN pip install --upgrade pip  

#! run this command to install all dependencies  
RUN pip install -r requirements.txt  

#! port where the Django app runs  
EXPOSE 8000  

#! start server  
CMD python manage.py runserver 0:8000



