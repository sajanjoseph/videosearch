from django.db import models
from django import forms
from django.contrib.auth.models import User
from datetime import datetime
# Create your models here.


class UserFileNameMap(models.Model):
    fuser = models.ForeignKey(User)
    filename = models.CharField(max_length=200,null=True,blank=True)
    
class FileAccessTime(models.Model):
    filename = models.CharField(max_length=200)
    accessTime = models.DateTimeField(default=datetime.now) 

    class Meta:
        verbose_name_plural="UserFileNameMaps"
