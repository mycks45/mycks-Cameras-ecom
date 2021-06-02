import coupons
from django.shortcuts import render, redirect, get_object_or_404
from store.models import product
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from accounts.models import UserProfile
from coupons.models import Coupon
from coupons.views import coupon_apply
from coupons.forms import CouponApplyForm



# Create your views here.




#create card with the session id
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart  


# add product to the cart with add to cart button 
def addCart(request, product_id):
    current_user = request.user
    produc = product.objects.get(id=product_id)
    # cart = Cart.objects.get(cart_id=_cart_id(request))
    # for authenticated users
    if current_user.is_authenticated:
        is_cart_item_exists = CartItem.objects.filter(product1=produc, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.get(product1=produc, user=current_user)
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(product1=produc, quandity=0, user=current_user)
            cart_item.save()
        try:
            cart_item = CartItem.objects.get(product1=produc, user=current_user)
            cart_item.quandity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(product1=produc, quandity=1, user=current_user)
            cart_item.save()
        
        return redirect('cart')
    # for guest and unauthenticated users
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()
        # increase the qundity of the product in the cart
        try:
            cart_item = CartItem.objects.get(product1=produc, cart=cart)
            cart_item.quandity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(product1=produc, quandity=1, cart=cart)
            cart_item.save()
        
        return redirect('cart')


# decrease the qundity of the product in the cart
def removeCart(request, product_id):
#     if request.user.is_authenticated:
#         produc = get_object_or_404(product, id =product_id)
#         cart_item = CartItem.objects.get(product1=produc,user=request.user)
#         if cart_item.quandity > 1:
#             cart_item.quandity -= 1
#             cart_item.save()
#         else:
#             cart_item.delete()
#     else:
#         cart = Cart.objects.get(cart_id=_cart_id(request))
#         produc = get_object_or_404(product, id =product_id)
#         cart_item = CartItem.objects.get(product1=produc,cart=cart)
#         if cart_item.quandity > 1:
#             cart_item.quandity -= 1
#             cart_item.save()
#         else:
#             cart_item.delete()
#     return redirect('cart')
    pass



# remove the product from the cart with the remove button
def removeCartItems(request, product_id):
    if request.user.is_authenticated:
        produc = get_object_or_404(product, id = product_id)
        cart_item = CartItem.objects.get(product1=produc, user=request.user)
        cart_item.delete()
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        produc = get_object_or_404(product, id = product_id)
        cart_item = CartItem.objects.get(product1=produc, cart=cart)
        cart_item.delete()
    return redirect('cart')


# display the cart 
def cart(request, total=0, quandity=0, cart_items=None):

    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:     
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product1.price * cart_item.quandity)
            quandity += cart_item.quandity
        # tax = (1 * total)/100
        tax = 100
        

        grand_total = get_cart_grandtotal_after_coupon(request=request ,total=total)
        try:
            if request.session['coupon_id']:
                couponID = request.session['coupon_id']
                coupon = Coupon.objects.get(id=couponID)
            else:
                coupon = None
        except:
            coupon=None

    except ObjectDoesNotExist:
        pass
    context = {
        'total':total, 
        'cart_items':cart_items, 
        'quandity':quandity, 
        'tax':tax, 
        'grand_total':grand_total,
        'coupon':coupon,
        
        }        
            
    return render(request, 'store/cart.html', context)



# decrease the qauntity of the cart items 
def ajax_posting(request, total=0, quandity=0, sub_total=0):
    Qty_less = request.GET.get('Qty_less', None) 
    
    grand_total = 0
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    else:     
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    for cart_item in cart_items:
        total += (cart_item.product1.price * cart_item.quandity)
        quandity += cart_item.quandity
        sub_total += total
    # tax = (1 * total)/100
    tax = 100
    grand_total = get_cart_grandtotal_after_coupon(request=request ,total=total)

    if request.is_ajax():
        Qty_less = request.GET.get('Qty_less', None) # getting data from first_name input 
        produc = get_object_or_404(product, id =Qty_less)
        cart_item = CartItem.objects.get(product1=produc,user=request.user)
        if cart_item.quandity > 1:
            cart_item.quandity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        produc = get_object_or_404(product, id =Qty_less)
        cart_item = CartItem.objects.get(product1=produc,cart=cart)
        if cart_item.quandity > 1:
            cart_item.quandity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    response = {
                'msg': cart_item.quandity, # response message
                'total': total,
                'grand_total': grand_total,
                'sub_total':sub_total,
    }
    return JsonResponse(response) # return response as JSON


# increase the qauntity of the cart items 
def ajax_postingPlus(request, total=0, quandity=0, sub_total=0):
    Qty_add = request.GET.get('Qty_add', None) # getting data from product id input 

    grand_total = 0
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    else:     
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    for cart_item in cart_items:
        total += (cart_item.product1.price * cart_item.quandity)
        quandity += cart_item.quandity
        sub_total += total
    # tax = (1 * total)/100
    tax = 100
    grand_total = get_cart_grandtotal_after_coupon(request=request ,total=total)

    if request.is_ajax():
        Qty_add = request.GET.get('Qty_add', None) # getting data from first_name input 
        produc = get_object_or_404(product, id =Qty_add)
        cart_item = CartItem.objects.get(product1=produc,user=request.user)
        cart_item.quandity += 1
        cart_item.save()
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        produc = get_object_or_404(product, id =Qty_add)
        cart_item = CartItem.objects.get(product1=produc,cart=cart)
        cart_item.quandity += 1
        cart_item.save()
    response = {
                'msg': cart_item.quandity,
                'total': total,
                'grand_total': grand_total,
                'sub_total':sub_total, # response message
    }
    return JsonResponse(response) # return response as JSON



# checkout page 
@login_required(login_url='user_login')
def checkout(request, total=0, quandity=0, cart_items=None):
    userprofile = UserProfile.objects.filter(user=request.user)
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product1.price * cart_item.quandity)
            quandity += cart_item.quandity
        # tax = (1 * total)/100
        tax = 100
        grand_total = get_cart_grandtotal_after_coupon(request=request ,total=total)
    except ObjectDoesNotExist:
        pass
    context = {
        'total':total, 
        'cart_items':cart_items, 
        'quandity':quandity, 
        'tax':tax, 
        'grand_total':grand_total,
        'userprofile':userprofile,
        } 
    return render(request, 'store/checkout.html', context)



def get_cart_grandtotal_after_coupon(request, total=0):
    tax = 100
    grand_total = total + tax
    try:
        if request.session['coupon_id']:
            print(2)
            post = Coupon.objects.get(id=request.session['coupon_id'])
            print(post.discount)
            total_before_coupon = grand_total
            grand_total = total_before_coupon - post.discount
            print(grand_total)  
        else:
            grand_total = total + tax
    except:
        grand_total = total + tax
        
    return grand_total
