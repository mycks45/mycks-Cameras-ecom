from math import trunc
from typing import Text
from django.db import models
from django.db.models.aggregates import Avg
from django.db.models.deletion import CASCADE
from django.db.models.fields import FloatField, TextField
from category.models import category
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import Account
from django.db.models import Avg, Count
# Create your models here.


class product(models.Model):
    product_name    = models.CharField(max_length=200, null=True)
    slug            = models.SlugField(max_length=200, blank=True)
    description     = models.TextField(max_length=500, blank=True)
    price           = models.IntegerField()
    Images          = models.ImageField(upload_to='photos/products')
    Images11          = models.ImageField(upload_to='photos/products')
    Images22          = models.ImageField(upload_to='photos/products')
    stock           = models.IntegerField()
    brand           = models.CharField(max_length=50, null=True)
    is_available    = models.BooleanField(default=True)
    category        = models.ForeignKey(category, on_delete=models.CASCADE)
    offer_active    = models.BooleanField(default=False)
    offer_discount  = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    price_before_discount= models.IntegerField(default=0, blank=True)
    created_date    = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name

    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg
    
    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count


class ReviewRating(models.Model):
    product = models.ForeignKey(product, on_delete=CASCADE)
    user = models.ForeignKey(Account, on_delete=CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    update_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
