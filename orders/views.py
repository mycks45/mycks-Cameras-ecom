from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from cart.models import CartItem
from .forms import Orderform
from .models import Order, OrderProduct, Payment, codId
import datetime
from store.models import product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import json
import razorpay
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from accounts.models import UserProfile
from cart.views import get_cart_grandtotal_after_coupon
from coupons.models import Coupon

# Create your views here.


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='user_login')
def placeOrder(request, total = 0, quandity = 0):
    current_user = request.user
    # if cart is empty don't show this page and redirect to store
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    con = codId.objects.filter(user=current_user)
    if con:
        con.delete()
    # get grand total price
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product1.price * cart_item.quandity)
        quandity += cart_item.quandity
    tax = 100
    grand_total = get_cart_grandtotal_after_coupon(request=request ,total=total)
    grand_total_usd = grand_total/80
    razorpay_total = grand_total *100
    try:
        if request.session['coupon_id']:
            couponID = request.session['coupon_id']
            coupon = Coupon.objects.get(id=couponID)
        else:
            coupon = None
    except:
        coupon=None

    
    # here we recive date from the checkout form
    if request.method == 'POST':
        print('mothod is post')

        form = Orderform(request.POST)
        if form.is_valid():
            print('form is vaild')
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.pin_code = form.cleaned_data['pin_code']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            post = UserProfile(user=request.user, address_line_1=data.address_line_1, address_line_2=data.address_line_2, pin_code=data.pin_code,city=data.city, state=data.state, country=data.country)
            post.save()
            data.save()
            print('first save')
            
            
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            
            payment_id = codId(user=current_user, cod_id= order_number)
            payment_id.save()

         
            
            print('second save')
            
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order':order,
                'cart_items':cart_items, 
                'total':total,
                'tax':tax,
                'grand_total':grand_total,
                'grand_total_usd':grand_total_usd,
                'razorpay_total':razorpay_total,
                'coupon':coupon,
                
            }
            
            return render(request, 'orders/payments.html', context)
        else:
            print('form is not valid')
    
        return redirect('checkout') 
    return redirect('checkout')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='user_login')
def addressChoice(request, id, total = 0, quandity = 0):
    current_user = request.user
    post = UserProfile.objects.get(id = id)
    # if cart is empty don't show this page and redirect to store
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    con = codId.objects.filter(user=current_user)
    if con:
        con.delete()
    
    # get grand total price
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product1.price * cart_item.quandity)
        quandity += cart_item.quandity
    tax = 100
    grand_total = get_cart_grandtotal_after_coupon(request=request ,total=total)
    grand_total_usd = grand_total/80
    razorpay_total = grand_total *100
    try:
        if request.session['coupon_id']:
            couponID = request.session['coupon_id']
            coupon = Coupon.objects.get(id=couponID)
        else:
            coupon = None
    except:
        coupon=None

    # data to order database
    data = Order()
    data.user = current_user
    data.first_name = post.user.first_name
    data.last_name = post.user.last_name
    data.phone = post.user.phone_number
    data.email = post.user.email
    data.address_line_1 = post.address_line_1
    data.address_line_2 = post.address_line_2
    data.pin_code = post.pin_code
    data.country = post.country
    data.state = post.state
    data.city = post.city
    data.order_total = grand_total
    data.tax = tax
    data.ip = request.META.get('REMOTE_ADDR')
    data.save()
    print('first save')
    
    yr = int(datetime.date.today().strftime('%Y'))
    dt = int(datetime.date.today().strftime('%d'))
    mt = int(datetime.date.today().strftime('%m'))
    d = datetime.date(yr, mt, dt)
    current_date = d.strftime("%Y%m%d")
    order_number = current_date + str(data.id)
    data.order_number = order_number
    data.save()
    
    payment_id = codId(user=current_user, cod_id= order_number)
    payment_id.save()

    print('second save')
            
    order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
    context = {
        'order':order,
        'cart_items':cart_items, 
        'total':total,
        'tax':tax,
        'grand_total':grand_total,
        'grand_total_usd':grand_total_usd,
        'razorpay_total':razorpay_total,
        'coupon':coupon,
        
    }
    
    return render(request, 'orders/payments.html', context)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='user_login')
def payments(request, total = 0, quandity = 0):
    
    try:
        current_user = request.user
        print('1')
        
        # codId is a db that is crated to get the order number of the last crated order
        con = codId.objects.get(user=current_user)
        order_number = con.cod_id
        con.delete()
        
        cart_items = CartItem.objects.filter(user=current_user)
        grand_total = 0
        tax = 0
        for cart_item in cart_items:
            total += (cart_item.product1.price * cart_item.quandity)
            quandity += cart_item.quandity
        tax = 100
        grand_total = get_cart_grandtotal_after_coupon(request=request ,total=total)
        print('2')
        if request.method == 'POST':
            print('3')
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            payment = Payment(
                user = current_user,
                payment_id=order.order_number,
                amount_paid = grand_total,
                payment_method = 'COD',
                status = 'COMPLETE',
            )
            payment.save()
            
            order.payment = payment
            order.is_ordered = True
            order.save()
            
            # Move orders to order product table
            cart_item = CartItem.objects.filter(user=current_user)
            
            for item in cart_item:
                orderedProduct = OrderProduct()
                orderedProduct.order_id= order.id
                orderedProduct.payment = payment 
                orderedProduct.user_id = request.user.id
                orderedProduct.product_id = item.product1_id
                orderedProduct.quantity = item.quandity
                orderedProduct.product_price = item.product1.price
                orderedProduct.ordered = True
                orderedProduct.save()
                
            
            # Reduse the quandity of the product sold
                produc = product.objects.get(id=item.product1_id)
                produc.stock -= item.quandity
                produc.save()
                
            # clear cart
            CartItem.objects.filter(user=request.user).delete()
            
            # send order recieved email to customer
            
            # mail_subject = "Thank you for your purchase"
            # massage = render_to_string('orders/order_recived_mail.html',{
            #     'user':request.user,
            #     'order':order,
            # })
            # to_mail = request.user.email
            # send_mail = EmailMessage(mail_subject,massage, to=[to_mail])
            # send_mail.send()
            
        order = Order.objects.get(user=current_user, is_ordered=True, order_number=order_number)
        ordered_product = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id=order_number)
        del request.session['coupon_id']
        context = {
            'order':order,
            'ordered_product':ordered_product,
            'payment':payment,
            
        }
            
        return render(request, 'orders/success.html', context)
    except:
        return redirect('home')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='user_login')
def paypal(request):
    print('in paypal')
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

     # codId is a db that is crated to get the order number of the last crated order
    con = codId.objects.get(user=request.user)
    con.delete()

    # save transaction details in the payment model;
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = 'Paypal',
        status = body['status'],
        amount_paid = order.order_total,
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move orders to order product table
    cart_item = CartItem.objects.filter(user=request.user)
    
    for item in cart_item:
        orderedProduct = OrderProduct()
        orderedProduct.order_id= order.id
        orderedProduct.payment = payment 
        orderedProduct.user_id = request.user.id
        orderedProduct.product_id = item.product1_id
        orderedProduct.quantity = item.quandity
        orderedProduct.product_price = item.product1.price
        orderedProduct.ordered = True
        orderedProduct.save()

        # Reduse the quandity of the product sold
        produc = product.objects.get(id=item.product1_id)
        produc.stock -= item.quandity
        produc.save()

    # clear cart
    CartItem.objects.filter(user=request.user).delete()

    # send order recieved email to customer
            
    # mail_subject = "Thank you for your purchase"
    # massage = render_to_string('orders/order_recived_mail.html',{
    #     'user':request.user,
    #     'order':order,
    # })
    # to_mail = request.user.email
    # send_mail = EmailMessage(mail_subject,massage, to=[to_mail])
    # send_mail.send()

    # sent order number and transaction id back to sendData method as json respond
    data = {
        'order_number':order.order_number,
        'transID':payment.payment_id,
    }
    return JsonResponse(data)


# here the ordercomplete function is for redirecting the paypal order completion
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='user_login')
def orderComplete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(user=request.user, is_ordered=True, order_number=order_number)
        ordered_product = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id=transID)
        del request.session['coupon_id']
        context = {
            'order':order,
            'ordered_product':ordered_product,
            'payment':payment,
        }
        return render(request, 'orders/success.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='user_login')
def razorpay(request):
    try:
            
        # codId is a db that is crated to get the order number of the last crated order
        con = codId.objects.get(user=request.user)
        order_number = con.cod_id
        con.delete()

        order = Order.objects.get(user=request.user, is_ordered = False,order_number = order_number)
        # amount = int(order.order_total)
        # currency = 'INR'
        # client = razorpay.Client(auth=('rzp_test_1spaICVLqKfs9g', 'I19NWKYE94060Ntce934dYd8'))
        # payment = client.order.create({'amount':amount, 'currency':currency,'payment_capture':'1'})
        # print(payment)

        if request.method == "POST":
                
            payments = Payment(
                user = request.user,
                payment_id=order.order_number,
                amount_paid = order.order_total,
                payment_method = 'Razorpay',
                status = 'COMPLETE',
            )
            payments.save()
            
            order.payment = payments
            order.is_ordered = True
            order.save()
                # Move orders to order product table
            cart_item = CartItem.objects.filter(user=request.user)
            
            for item in cart_item:
                orderedProduct = OrderProduct()
                orderedProduct.order_id= order.id
                orderedProduct.payment = payments 
                orderedProduct.user_id = request.user.id
                orderedProduct.product_id = item.product1_id
                orderedProduct.quantity = item.quandity
                orderedProduct.product_price = item.product1.price
                orderedProduct.ordered = True
                orderedProduct.save()

                # Reduse the quandity of the product sold
                produc = product.objects.get(id=item.product1_id)
                produc.stock -= item.quandity
                produc.save()

        # clear cart
        CartItem.objects.filter(user=request.user).delete()

        # send order recieved email to customer
                
        # mail_subject = "Thank you for your purchase"
        # massage = render_to_string('orders/order_recived_mail.html',{
        #     'user':request.user,
        #     'order':order,
        # })
        # to_mail = request.user.email
        # send_mail = EmailMessage(mail_subject,massage, to=[to_mail])
        # send_mail.send()

        order = Order.objects.get(user=request.user, is_ordered=True, order_number=order_number)
        ordered_product = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id=order_number)
        del request.session['coupon_id']
        context = {
            'order':order,
            'ordered_product':ordered_product,
            'payment':payment,
            }
                
        return render(request, 'orders/success.html', context)
    except:
        return redirect('home')
