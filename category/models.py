from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50,unique=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    
    def get_url(self):
        return reverse('product_by_category', args=[self.slug])


    def __str__(self):
        return self.category_name



class CategoryAllOffer(models.Model):
    offer_name= models.CharField(max_length=20)
    category = models.ForeignKey(category, on_delete=models.CASCADE)
    offer_discount = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(99)])
    cat_valid_from = models.DateTimeField()
    cat_valid_to = models.DateTimeField()
    is_active = models.BooleanField()

    def __str__(self):
        return self.category.category_name
