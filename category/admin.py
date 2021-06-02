from django.contrib import admin
from .models import category, CategoryAllOffer

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug')

admin.site.register(category, CategoryAdmin)
admin.site.register(CategoryAllOffer)