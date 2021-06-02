
# from accounts.views import referral
import datetime
from math import trunc
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.fields import BLANK_CHOICE_DASH, CharField, DateField

#otp...................................
from django.core.validators import RegexValidator
from django.db.models import Q
from django.db.models.signals import pre_save, post_save

from django.dispatch import receiver
# from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save


import random
import os
from django.forms.fields import DateTimeField
import requests
from .utils import generate_ref_code
#..........................................

# Create your models here.

#custom user model
class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must enter email address')
        
        if not username:
            raise ValueError('User must have a username')
        
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name, 
            last_name = last_name,
        )
        user.is_active = True
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, first_name, last_name, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,
        )
        user.is_active = True
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    first_name      = models.CharField(max_length=50)
    last_name       = models.CharField(max_length=50)
    username        = models.CharField(max_length=50, unique=True)
    email           = models.EmailField(max_length=150, unique=True)
    profile_picture = models.ImageField(blank=True, upload_to='userprofile')
    phone_regex = RegexValidator( regex = r'^\+?1?\d{9,10}$', message ="Phone number must be entered in the format +919999999999. Up to 10 digits allowed.")
    phone_number       = models.CharField('Phone',validators =[phone_regex], max_length=17, null=True,unique = True)
    referral_count = models.IntegerField(blank=True, null=True)
    
    #required
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False) 
    is_staff = models.BooleanField(default=False) 
    is_active = models.BooleanField(default=False) 
    is_superuser = models.BooleanField(default=False) 

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS =['username','first_name','last_name']

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def  has_perm(self, perm, obj=None):
        return self.is_active

    def has_module_perms(self, add_label):
        return True
    
    

class UserProfile(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    address_line_1 = models.CharField(blank=True, max_length=150)
    address_line_2 = models.CharField(blank=True, max_length=150)
    pin_code = models.CharField(blank=True, max_length=6)
    city = models.CharField(blank=True, max_length=30)
    state = models.CharField(blank=True, max_length=30)
    country = models.CharField(blank=True, max_length=30)
    
    
    def __str__(self):
        return self.user.first_name
    
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'



class ProfileReferral(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    code = models.CharField(max_length=7, blank=True)
    recommended_by = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True, related_name='ref_by')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name}-{self.code}"

    def get_recommended_profiles(self):
        pass

    def save(self, *args, **kwargs):
        if self.code =="":
            code = generate_ref_code()
            self.code = code
        super().save(*args, **kwargs)



