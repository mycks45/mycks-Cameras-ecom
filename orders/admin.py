from django.contrib import admin
from .models import Payment, Order, OrderProduct, codId

# Register your models here.

class OrderProductInline(admin.TabularInline):
    model = OrderProduct 
    fields = ('payment','product','product_price','quantity')
    readonly_fields = ('payment','product','product_price','quantity')
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number','full_name','phone','email','order_total','status','is_ordered','created_at']
    list_filter = ['status','is_ordered']
    search_fields = ['order_number','first_name','last_name','email']
    list_per_page = 20
    inlines = [OrderProductInline]


admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
admin.site.register(codId)