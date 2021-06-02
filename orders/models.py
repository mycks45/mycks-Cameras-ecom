from django.db import models
from store.models import product
from accounts.models import Account

# Create your models here.


class Payment(models.Model):
    
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=20)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.payment_id
    
    
class Order(models.Model):
    STATUS = (
        ('Pending','Pending'),
        ('Accepted','Accepted'),
        ('Shipped','Shipped'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
    )
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=16)
    email = models.EmailField(max_length=50)
    address_line_1 =models.CharField(max_length=100)
    address_line_2 =models.CharField(max_length=100)
    pin_code = models.CharField(max_length=6)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS, default='Pending')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'
    
    
    def __str__(self):
        return self.first_name
    

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(product, on_delete=models.CASCADE)
    quantity =models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.product.product_name
    
    
class codId(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    cod_id = models.CharField(max_length=20)
    
    def __str__(self):
        return self.cod_id