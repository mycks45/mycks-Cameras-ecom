from django import forms
from store.models import product
from orders.models import Order


class NewProductForm(forms.ModelForm):
    class Meta:
        model = product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(NewProductForm, self).__init__(*args, **kwargs)
        self.fields['product_name'].widget.attrs['placeholder'] = 'Enter name of the product'
        self.fields['slug'].widget.attrs['placeholder'] = 'Enter slug name'
        self.fields['description'].widget.attrs['placeholder'] = 'Add discription'
        self.fields['price'].widget.attrs['placeholder'] = 'Price per unit'
        self.fields['stock'].widget.attrs['placeholder'] = 'Number of stock available'
        self.fields['brand'].widget.attrs['placeholder'] = 'Brand Name'
        self.fields['Images'].widget.attrs['onchange'] = 'readURL(this)'
        self.fields['Images11'].widget.attrs['onchange'] = 'readURL11(this)'
        self.fields['Images22'].widget.attrs['onchange'] = 'readURL22(this)'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
       