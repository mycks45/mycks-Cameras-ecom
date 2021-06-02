import accounts
from typing import AsyncContextManager
from django.http.response import HttpResponse
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, message
from django.contrib import sessions
from django.utils import timezone
from django.core.files.base import ContentFile


from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account,UserProfile, ProfileReferral
from  .decorators import unauthenticated_user
from cart.views import _cart_id
from cart.models import Cart, CartItem
from coupons.models import Coupon


import requests
from orders.models import Order, OrderProduct
from .sms_fuc import gen_otp, send_sms
import base64


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Create your views here.


# create new users 
@unauthenticated_user
def register(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        
        if form.is_valid():
            first_name      =form.cleaned_data['first_name']
            last_name       =form.cleaned_data['last_name']
            phone_number    =form.cleaned_data['phone_number']
            email           =form.cleaned_data['email']
            password        =form.cleaned_data['password']
            username        =email.split('@')[0]
            referral_counts = 0
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.phone_number =phone_number
            user.save()
            post = UserProfile.objects.create(user=user)
            post.save()
            profileReferral = ProfileReferral.objects.create(user=user)
            profileReferral.save()
            auth.login(request, user)
            messages.success(request, 'New account is created')
            return redirect('referral')
       
    context = {'form' : form ,}
    return render(request, 'accounts/register.html', context)


# here user with recommention code 
def referral(request):
    if request.method == 'POST':
        code = request.POST['ref_code']
        try:
            if code:
                recommended = ProfileReferral.objects.get(code=code)
                recommended_to = ProfileReferral.objects.get(user=request.user)
                ref_count = Account.objects.get(id=request.user.id)
                ref_count.referral_count +1
                ref_count.save
                recommended_to.recommended_by = recommended.user
                recommended_to.save()
                return redirect('home')
        except:
            messages.error(request, 'No user exist by given referral code')
            return redirect('referral')  
    return render(request, 'accounts/referralPage.html')




# login 
@unauthenticated_user
def userLogin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))  
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    
                    product_id =[]
                    for item in cart_item:
                        product_id.append(item.product1)
                        
                    cart_item = CartItem.objects.filter(user=user)
                    
                    ex_product_id =[]
                    for item in cart_item:
                        ex_product_id.append(item.product1)
                        
                    for pr in product_id:
                        if pr in ex_product_id:
                            index = ex_product_id.index(pr)
                            item_id = product_id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quandity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
                                    
            except:
                pass

            auth.login(request, user)
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextpage = params['next']
                    return redirect(nextpage)
            except:
                return redirect('home')
        else:
            user = Account.objects.get(email=email)
            if user.is_active:
                messages.error(request, 'Invalid Email or password')
                return redirect('user_login')
            else:
                messages.error(request, 'you are blocked from this website')
                return redirect('user_login')
    return render(request, 'accounts/login.html')


#logout of users
@login_required(login_url='user_login')
def userLogout(request):
    auth.logout(request)
    return redirect('home')


# this function create random six digit number
random_otp = gen_otp()
msg_body = F'''
Your Mycks account login request is recived and
your OTP is {random_otp}
'''
user_number='0'


# here the phone number is valitated and send otp 
def sign_in_otp(request):
    if request.method == "POST":
        phone = request.POST['phone_number']
        num = Account.objects.get(phone_number=phone)
        if num is not None:
            global user_number
            user_number = num.phone_number
            send_sms(msg_body, user_number)
            print(random_otp)
            messages.success(request, 'OTP has send to your Phone number')
            return redirect('OTP_page')
        else:
            messages.error(request, 'your Mobile number does not match any account')
            return redirect('sign_in_otp')

    return render(request, 'accounts/sign_in_otp.html')


# here is otp id checked  and login 
def OTP_page(request):
    if request.method == "POST":
        otp_rev = request.POST['OTP_rev']
        if random_otp == otp_rev:
            global user_number
            user = Account.objects.get(phone_number = user_number)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    return redirect('home')
                else:
                    messages.error(request, 'you are blocked from this website')
                    return redirect('user_login')
            else:
                messages.error(request, 'No user is registered in this number')
        else:
            messages.error(request, 'Incorrect OTP')
            return redirect('OTP_page')      
    return render(request, 'accounts/OTP_page.html')



# forgot password via email, here email is send to the give email if they are in database
def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__iexact=email)

            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html',{
                'user':user,
                'domain': current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_mail =email
            send_email = EmailMessage(mail_subject, message, to=[to_mail])
            send_email.send()

            messages.success(request, 'Reset password email has sented to you email')
            return redirect('user_login')

        else:
            messages.error(request, 'Account with this email address does not exist')
            return redirect('forgot_password')
        
    return render(request, 'accounts/forgotPassword.html')


#here the link is the forgot email is valitated
def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid) 
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'please reset you password')        
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('user_login')


# if the link is valid here the password is reseted
def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'password has reseted successfully')
            return redirect('user_login')
        else:
            messages.error(request, 'password do not match!')
            return redirect('reset_password') 
    else:
        return render(request, 'accounts/resetPassword.html')


# user profile
@login_required(login_url='user_login')
def profile(request):
    user = Account.objects.get(email = request.user)
    userprofile = UserProfile.objects.filter(user=request.user)
    order = Order.objects.order_by('-created_at').filter(user_id = request.user.id, is_ordered=True)
    order_count = order.count()
    ref = ProfileReferral.objects.get(user=request.user)
    ref_code = ref.code
    ref_c = ProfileReferral.objects.filter(recommended_by= request.user)
    ref_count = ref_c.count()
    user_ref_count = Account.objects.get(id=request.user.id)
    user_ref_count.referral_count = ref_count
    user_ref_count.save()

    now = timezone.now()

    # for redeeming the referral offers
    if request.method == 'POST':
        try:
            if ref_count>5:
                coupon = Coupon.objects.get(code__iexact='REFONE', valid_from__lte=now, valid_to__gte=now, active=True)
                request.session['coupon_id']=coupon.id
                messages.success(request,'coupon is add to cart')
                return redirect('profile')
            else:
                messages.error(request,'min 5 referral is required')
                return redirect('profile')
        except:
            messages.error(request,'Cart has no items')
            return redirect('profile')

    
    context = {
        'user':user,
        'order_count':order_count,
        'userprofile':userprofile,
        'ref_code':ref_code,
        'ref_count':ref_count,
    }
    return render(request, 'accounts/profile.html', context)


# add userprofile address form the profile page of user
@login_required(login_url='user_login')
def addAddress(request):
    if request.method == 'POST':
        address_line_1 = request.POST['address_line_1']
        address_line_2 = request.POST['address_line_2']
        pin_code = request.POST['pin_code']
        city = request.POST['city']
        country = request.POST['country']
        state = request.POST['state']
        post = UserProfile(user=request.user, address_line_1=address_line_1, address_line_2=address_line_2, pin_code=pin_code,city=city, state=state, country=country)
        post.save()
        return redirect('profile')
    return render(request, 'accounts/addAddress.html')


#udate the address in userprofile from the user profile page
@login_required(login_url='user_login')
def addressUpdate(request, id):
    obj = UserProfile.objects.get(id=id)
    form = UserProfileForm(instance=obj)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance = obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address has been updated')
            return redirect('profile')
        else:
            messages.error(request, 'error in the forms')
    
    context = {
        'form':form
    }
    return render(request, 'accounts/addressUpdate.html', context)


# this is to delete the save userprofile address
@login_required(login_url='user_login')
def addressDelete(request, id):
    post = UserProfile.objects.get(id = id)
    post.delete()
    return redirect('profile')



# user order
@login_required(login_url='user_login')
def myOrder(request):
    # orders = Order.objects.filter(user = request.user, is_ordered=True).order_by('-created_at')
    orders = OrderProduct.objects.filter(user = request.user)

    context = {
        'orders':orders
    }
    return render(request, 'accounts/myOrder.html', context)


# here display the order history page of user
@login_required(login_url='user_login')
def myOrderHistory(request):
    # orders = Order.objects.filter(user = request.user, is_ordered=True).order_by('-created_at')
    orders = OrderProduct.objects.filter(user = request.user, order__status='Completed')

    context = {
        'orders':orders
    }
    return render(request, 'accounts/myOrderHistory.html', context)



# user order details
@login_required(login_url='user_login')
def userOrderDetails(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal +=i.product_price * i.quantity
        
    grand_total = subtotal + order.tax
     
    context = {
        'order_detail':order_detail,
        'order':order,    
        'subtotal':subtotal,    
        'grand_total':grand_total,    
    }
    return render(request, 'accounts/userOrderDetails.html', context)


# here user can cancel his order
@login_required(login_url='user_login')
def userdeleteOrder(request, id):
    post = Order.objects.get(order_number=id)
    # produc = product.objects.get(id=product.product1_id)
    # produc.stock += item.quandity
    # produc.save()
    post.status = 'Cancelled'
    post.save()
    context = {}
    return redirect('my_order')


# here the user can edit his profile
@login_required(login_url='user_login')
def editProfile(request):
    print(request.user)
    userprofile = UserProfile.objects.filter(user=request.user)
    userPhotoUpdate = Account.objects.get(email=request.user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, request.FILES, instance=request.user)
        image1 = request.POST['pro_img1']
       
        if user_form.is_valid():
            user_form.save()
            format, img1 = image1.split(';base64,')
            ext = format.split('/')[-1]
            img_data = ContentFile(base64.b64decode(img1),name=request.user.first_name +  '1.'+ext)
            userPhotoUpdate.profile_picture = img_data
            userPhotoUpdate.save()
            
            messages.success(request, 'your profile has updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
              
    context = {
        'user_form':user_form,
        'userprofile':userprofile,
    }
    return render(request, 'accounts/editProfile.html', context)


# here the user can change his password
@login_required(login_url='user_login')
def changePassword(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        Comfirm_password = request.POST['Comfirm_password']

        user = Account.objects.get(username__exact=request.user.username)
        
        if new_password == Comfirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                auth.logout(request)
                messages.success(request, 'You password has updated')
                return redirect('change_password')
            else:
                messages.error(request, 'please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'New Password does not match')
            return redirect('change_password')
    context = {}
    return render(request, 'accounts/change_password.html', context)