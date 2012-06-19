from django.db import models
from django import forms
from django.contrib.auth.models import User
# Create your models here.


class UserFileNameMap(models.Model):
    fuser = models.ForeignKey(User)
    filename = models.CharField(max_length=200,null=True,blank=True)
    
    class Meta:
        verbose_name_plural="UserFileNameMaps"
