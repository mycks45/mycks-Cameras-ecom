from django.contrib import admin
from .models import product, ReviewRating

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name','price','stock','category','modified_date','is_available','offer_active')
    prepopulated_fields ={'slug':('product_name',)}


admin.site.register(product, ProductAdmin)
admin.site.register(ReviewRating)