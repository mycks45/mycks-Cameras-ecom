from django import forms
from django import forms
from .models import Coupon
from category.models import CategoryAllOffer


class CouponApplyForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code']
    def __init__(self, *args, **kwargs):
        super(CouponApplyForm, self).__init__(*args, **kwargs)
        self.fields['code'].widget.attrs['placeholder'] = 'Coupon code'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control coupon'


class CouponApplyAdminForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = '__all__'
        widgets = {
        'valid_from': forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control', 'placeholder':'Select a date from this coupon is valid', 'type':'date'}),
        'valid_to': forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control', 'placeholder':'Select a date upto this coupon is valid', 'type':'date'}),
        }
    def __init__(self, *args, **kwargs):
        super(CouponApplyAdminForm, self).__init__(*args, **kwargs)
        self.fields['code'].widget.attrs['placeholder'] = 'Coupon code'
        self.fields['discount'].widget.attrs['placeholder'] = 'Discount amount max 5000'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control coupon'


class CategoryOfferApplyAdminForm(forms.ModelForm):
    class Meta:
        model = CategoryAllOffer
        fields = '__all__'
        widgets = {
        'cat_valid_from': forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control', 'placeholder':'Select a date from this offer is valid', 'type':'date'}),
        'cat_valid_to': forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control', 'placeholder':'Select a date upto this offer is valid', 'type':'date'}),
        }
    def __init__(self, *args, **kwargs):
        super(CategoryOfferApplyAdminForm, self).__init__(*args, **kwargs)
        self.fields['offer_discount'].widget.attrs['placeholder'] = 'Discount amount max 99'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'