from django.utils.translation import deactivate
from category.models import category, CategoryAllOffer
from django.http import request
from django.shortcuts import redirect, render
from .models import Coupon
from django.views.decorators.http import require_POST
from .forms import CouponApplyForm, CategoryOfferApplyAdminForm
from django.utils import timezone
from store.models import product


# Create your views here

# this here add the coupon to the session in cart
@require_POST
def coupon_apply(request):
    now = timezone.now()
    # form = CouponApplyForm(request.POST)
    print(2)
    code = request.POST['code']
    if code:
        print(code)
        try:
            coupon = Coupon.objects.get(code__iexact=code, valid_from__lte=now, valid_to__gte=now, active=True)
            request.session['coupon_id']=coupon.id
            print(request.session['coupon_id'])
        except Coupon.DoesNotExist:
            request.session['coupon_id']= None
    return redirect('cart')


#here the offer on category and update the offer if the that category have existiong offer
def add_category_offer(request):
    form = CategoryOfferApplyAdminForm(request.POST)
    now = timezone.now()
    if request.method == 'POST':
        
        if form.is_valid():
            cat_category = form.cleaned_data['category']
            cat_name = form.cleaned_data['offer_name']
            cat_offer_discount = form.cleaned_data['offer_discount']
            cat_vaild_from = form.cleaned_data['cat_valid_from']
            cat_vaild_to = form.cleaned_data['cat_valid_to']
            active = False
            category_off = CategoryAllOffer.objects.filter(category=cat_category).exists()
            if category_off:
                category_offer = CategoryAllOffer.objects.get(category=cat_category)
                category_offer.category= cat_category
                category_offer.offer_name = cat_name
                category_offer.offer_discount = cat_offer_discount
                category_offer.cat_valid_from = cat_vaild_from
                category_offer.cat_valid_to = cat_vaild_to
                category_offer.is_active= active
                category_offer.save()
            else:
                form.save()
            return redirect('coupons_mgt')
        else:
            return redirect('add_category_offer')
    context ={
        'form':form
    }
    return render(request, 'adminPanel/catagoryOfferAddForm.html', context)


# here the created category offer is activated and deactivated while changing the price of product
def activate_cat_offer(request, cat_id):
    now = timezone.now()
    cat_offer = CategoryAllOffer.objects.get(id=cat_id, cat_valid_from__lte=now, cat_valid_to__gte=now)
    cate = cat_offer.category
    cat_off_percentage = cat_offer.offer_discount
    active=True
    deactivate = False
    if cat_offer.is_active == True:
        prod= product.objects.filter(category=cate)
        for item in prod:
            item.price = item.price_before_discount
            item.offer_active = False
            item.offer_discount = 0
            item.save()
        cat_offer.is_active = deactivate
        cat_offer.save()
        return redirect('coupons_mgt')
    else:
        pro = product.objects.filter(category=cate)
        for item in pro:
            item.price = item.price_before_discount
            less_price = (item.price/100)*int(cat_off_percentage)
            item.price = int(item.price) - int(less_price)
            item.offer_active = True
            item.offer_discount = cat_off_percentage
            item.save()
        cat_offer.is_active = active
        cat_offer.save()
        return redirect('coupons_mgt')
            


# here the category offer is deleted and if that offer is active, the procduct price is coverted it og_price
def delete_category_offer(request, cat_id):
    cat_offer = CategoryAllOffer.objects.get(id=cat_id)
    cate = cat_offer.category
    try:
        if cat_offer.is_active == True:
            prod= product.objects.filter(category=cate)
            for item in prod:
                item.price = item.price_before_discount
                item.offer_active = False
                item.offer_discount = 0
                item.save()
            cat_offer.delete()
            return redirect('coupons_mgt')
        else:
            cat_offer.delete()
            return redirect('coupons_mgt')
    except:
        cat_offer.delete()
        return redirect('coupons_mgt')

