from decimal import Context
from django.shortcuts import render,redirect, get_object_or_404
from store.models import product
from accounts.models import Account, ProfileReferral
from category.models import category, CategoryAllOffer
from .forms import NewProductForm, OrderStatusForm
from django.contrib.sessions.models import Session
from django.views.decorators.cache import cache_control
from accounts.decorators import unauthenticated_admin
from orders.models import OrderProduct, Order, Payment
from django.db.models import Q
from datetime import date
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from coupons.models import Coupon
from coupons.forms import CouponApplyAdminForm
from django.core.files.base import ContentFile
import base64
from django.contrib import messages

# Create your views here.


# Here admin login and display dashbroad
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@unauthenticated_admin
def adminPanel(request):
    post = Account.objects.filter(is_active=True)
    userCount = post.count()

    order = Order.objects.filter(is_ordered=True)
    orderCount = order.count()

    payment=Payment.objects.all()
    sales = 0
    for item in payment:
        sale = float(item.amount_paid)
        sales += sale
    sales = round(sales)
        

    categories = get_object_or_404(category, slug='cameras')
    products = product.objects.filter(category=categories, is_available=True)
    camCount = 0
    for item in products:
        camCount +=1

    categories = get_object_or_404(category, slug='lens')
    products = product.objects.filter(category=categories, is_available=True)
    lensCount = 0
    for item in products:
        lensCount +=1

    categories = get_object_or_404(category, slug='accessories')
    products = product.objects.filter(category=categories, is_available=True)
    accessoriesCount = 0
    for item in products:
        accessoriesCount +=1

    categories = get_object_or_404(category, slug='flash')
    products = product.objects.filter(category=categories, is_available=True)
    flashCount = 0
    for item in products:
        flashCount +=1
    
    cod = Payment.objects.filter(payment_method = 'COD')
    codCount = cod.count()
    cod1 = Payment.objects.filter(payment_method = 'Razorpay')
    razCount = cod1.count()
    cod2 = Payment.objects.filter(payment_method = 'Paypal')
    payCount = cod2.count()

    today = date.today()
    thisYearsale =  Payment.objects.filter(created_at__year=today.year)
    salesThisYear = 0
    for item in thisYearsale:
        sale = float(item.amount_paid)
        salesThisYear += sale
    

    thisYearsale =  Payment.objects.filter(created_at__month=today.month)
    salesThisMonth = 0
    for item in thisYearsale:
        sale = float(item.amount_paid)
        salesThisMonth += sale

    thisYearsale =  Payment.objects.filter(created_at__day=today.day)
    salesToday = 0
    for item in thisYearsale:
        sale = float(item.amount_paid)
        salesToday += sale

    thisYearorder =  Order.objects.filter(created_at__day=today.day)
    orderToday = 0
    for item in thisYearorder:
        orderToday +=1
        
    thisYearorder =  Order.objects.filter(status = 'Accepted')
    orderStatusAccepted = 0
    for item in thisYearorder:
        orderStatusAccepted +=1

    thisYearorder =  Order.objects.filter(status = 'Shipped')
    orderStatusShipped = 0
    for item in thisYearorder:
        orderStatusShipped +=1

    thisYearorder =  Order.objects.filter(status = 'Completed')
    orderStatusCompleted = 0
    for item in thisYearorder:
        orderStatusCompleted +=1

    thisYearorder =  Order.objects.filter(status = 'Cancelled')
    orderStatusCancelled = 0
    for item in thisYearorder:
        orderStatusCancelled +=1

    context ={
        'userCount':userCount,
        'orderCount':orderCount,
        'sales':sales,
        'camCount':camCount,
        'lensCount':lensCount,
        'accessoriesCount':accessoriesCount,
        'flashCount':flashCount,
        'codCount':codCount,
        'payCount':payCount,
        'razCount':razCount,
        'salesThisYear':salesThisYear,
        'salesThisMonth':salesThisMonth,
        'salesToday':salesToday,
        'orderToday':orderToday,
        'orderStatusAccepted':orderStatusAccepted,
        'orderStatusShipped':orderStatusShipped,
        'orderStatusCompleted':orderStatusCompleted,
        'orderStatusCancelled':orderStatusCancelled,
        
    }
    return render(request, 'adminPanel/dashbroad.html', context)


# admin login 
def loginAdmin(request):
    if request.method== 'POST':
        print('here')
        admin = 'admin'
        pwd = '12345'
        if admin == request.POST['admin'] and pwd == request.POST['pwd']:
            request.session['is_logged'] = True
            return redirect('admin_panel')
        else:
            # messages.info(request, "incorrect username or password")
            return redirect('login_admin')
    else:       
        return render(request, 'adminPanel/adminLogin.html')



# This fuunction handle Logout admin in admin panel
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logoutAdmin(request):
    del request.session['is_logged']
    return redirect('admin_panel')


# Product management in the admin side
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@unauthenticated_admin
def productMgt(request):
    products = product.objects.all()
    paginator= Paginator(products, 9)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()

    context = {'products':paged_products, 'product_count':product_count}
    return render(request, 'adminPanel/productMgtlist.html', context)


# add new product from admin side
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@unauthenticated_admin
def addProduct(request):
    form = NewProductForm(request.POST, request.FILES)
    if request.method == 'POST':
        
        image = request.POST['pro_img1']
        image11 = request.POST['pro_img2']
        image22 = request.POST['pro_img3']
    
        if form.is_valid():
            form.save()
            product_name = form.cleaned_data['product_name']
            remove_dublicate = product.objects.filter(product_name=product_name).count()
            if remove_dublicate <=1:
                post_crop_img = product.objects.get(product_name=product_name)
                
                # crop images
                try:
                    if image:        
                        format, img1 = image.split(';base64,')
                        ext = format.split('/')[-1]
                        img1_Croped_data = ContentFile(base64.b64decode(img1),name=product_name + '1.'+ext)
                        post_crop_img.Images = img1_Croped_data
                        post_crop_img.save()
                except:
                    pass
                try:
                    if image11:        
                        format, img2 = image11.split(';base64,')
                        ext = format.split('/')[-1]
                        img2_Croped_data = ContentFile(base64.b64decode(img2),name=product_name + '1.'+ext)      
                        post_crop_img.Images11 = img2_Croped_data
                        post_crop_img.save()
                except:
                    pass
                try:
                    if image11:        
                        format, img3 = image22.split(';base64,')
                        ext = format.split('/')[-1]
                        img3_Croped_data = ContentFile(base64.b64decode(img3),name=product_name + '1.'+ext)     
                        post_crop_img.Images22 = img3_Croped_data
                        post_crop_img.save()
                except:
                    pass
              

                try:
                    offerper = form.cleaned_data['offer_discount']
                    offer_active = form.cleaned_data['offer_active']
                    realprice = form.cleaned_data['price']
                    og_price = form.cleaned_data['price']
                    lesspercentage = og_price*(offerper/100)
                    discounted_price = og_price - lesspercentage
                    
                    if offer_active:
                        post = product.objects.get(product_name=product_name)
                        post.price_before_discount = int(realprice)
                        post.price = int(discounted_price)
                        post.save()
                        return redirect('product_mgt')
                except:
                    print(form.cleaned_data['product_name']+'in exception')
                    form.save()
                    return redirect('product_mgt')
                return redirect('product_mgt')
            else:
                messages.error(request, 'this product all ready exist')
                return redirect('add_product')

    context = {'form':form}   
    return render(request, 'adminPanel/productAddForm.html', context)


# update existing product from admin panel
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@unauthenticated_admin
def updateProduct(request, id):
    obj= product.objects.get(id=id)
    form= NewProductForm(instance = obj)
    if request.method == 'POST':
        form = NewProductForm(request.POST,request.FILES, instance= obj)
        image = request.POST['pro_img1']
        image11 = request.POST['pro_img2']
        image22 = request.POST['pro_img3']

        if form.is_valid(): 
            form.save()
            product_name = form.cleaned_data['product_name']
            remove_dublicate = product.objects.filter(id=id).count()
            if remove_dublicate <=1:
                post_crop_img = product.objects.get(id=id)
                
                # crop images
                try:
                    if image:        
                        format, img1 = image.split(';base64,')
                        ext = format.split('/')[-1]
                        img1_Croped_data = ContentFile(base64.b64decode(img1),name=product_name + '1.'+ext)
                        post_crop_img.Images = img1_Croped_data
                        post_crop_img.save()
                except:
                    pass
                try:
                    if image11:        
                        format, img2 = image11.split(';base64,')
                        ext = format.split('/')[-1]
                        img2_Croped_data = ContentFile(base64.b64decode(img2),name=product_name + '1.'+ext)      
                        post_crop_img.Images11 = img2_Croped_data
                        post_crop_img.save()
                except:
                    pass
                try:
                    if image11:        
                        format, img3 = image22.split(';base64,')
                        ext = format.split('/')[-1]
                        img3_Croped_data = ContentFile(base64.b64decode(img3),name=product_name + '1.'+ext)     
                        post_crop_img.Images22 = img3_Croped_data
                        post_crop_img.save()
                except:
                    pass

            try:
                post = product.objects.get(product_name=form.cleaned_data['product_name'])
                if post.offer_active == False:
                    print('else')
                    real_price = post.price_before_discount
                    post.price = real_price
                    post.save()
                    return redirect('product_mgt')
                else:
                    offerper = form.cleaned_data['offer_discount']
                    realprice = post.price_before_discount
                    lesspercentage = realprice*(offerper/100)
                    discounted_price = realprice - lesspercentage
                    post.price = int(discounted_price)
                    post.save()
                    return redirect('product_mgt')

            except:
                print(form.cleaned_data['product_name']+'in exception')
                form.save()
                return redirect('product_mgt')

    context = {'form':form, 'obj':obj}   
    return render(request, 'adminPanel/productUpdate.html', context)


# delete product from admin panel
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@unauthenticated_admin
def deleteProduct(request, id):
    post = product.objects.get(id=id)
    post.delete()  
    context = {}
    return redirect('product_mgt')


# user management in admin panel
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@unauthenticated_admin
def userMgt(request):
    customers = Account.objects.all()

    context = {
        'customers':customers,
        }
    return render(request, 'adminPanel/userMgt.html', context)


# here count and ref code of the user is displayed in the profile of the user
@unauthenticated_admin
def referrenceStats(request, pk):
    customer = Account.objects.get(id=pk)
    ref_c = ProfileReferral.objects.filter(recommended_by= customer)
    ref_count = ref_c.count()

    context = {
        'customer':customer,
        'ref_count':ref_count,
        }
    return render(request, 'adminPanel/userRef.html', context)



# delete users from admin panel
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@unauthenticated_admin
def deleteUser(request, pk):
    user = Account.objects.get(id=pk)
    user.delete()
    return redirect('user_mgt')  
    

# Block usrs from admin panel
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@unauthenticated_admin   
def blockUser(request, pk):
    user = Account.objects.get(id=pk)
    if user.is_active == True:
        user.is_active = False
        user.save()
    else:
        user.is_active = True
        user.save()
    customers = Account.objects.all()
    context = {'customers':customers}
    return redirect('user_mgt')   
    
    

# category management in the admin panel
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@unauthenticated_admin
def categoryMgt(request):
    categories = category.objects.all()
    context = {'categories':categories}
    return render(request, 'adminPanel/categoryMgt.html', context)


# add category
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@unauthenticated_admin
def addCategory(request):
    if request.method == 'POST':

        if request.POST.get('name') and request.POST.get('image') and request.POST.get('slug'):

            post=category()

            post.category_name  = request.POST.get('name')
            post.cat_image      = request.POST.get('image')
            post.slug           = request.POST.get('slug')

            post.save()
            return redirect('category_mgt')
    return render(request, 'adminPanel/categoryAddForm.html')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@unauthenticated_admin
def orderMgt(request):
    orders = OrderProduct.objects.order_by('-created_at')
    context = {'orders':orders}
    return render(request, 'adminPanel/order_mgt.html', context)



# delete order from admin panel
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@unauthenticated_admin
def deleteOrder(request, id):
    post = OrderProduct.objects.get(id=id)
    # produc = product.objects.get(id=product.product1_id)
    # produc.stock += item.quandity
    # produc.save()
    post.delete()  
    context = {}
    return redirect('order_mgt')



# detail page of the the order in admin order page
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@unauthenticated_admin
def orderDetail(request, id):
    order_detail = OrderProduct.objects.filter(order__order_number=id)
    order = Order.objects.get(order_number=id)
    
    # handles the order status update
    if request.method == 'POST':
        order.status = request.POST['status']
        order.save()
        
    context = {
        'order_detail':order_detail,
        'order':order,
    }
    return render(request, 'adminPanel/order_detail.html', context)



# search function in admin side
@unauthenticated_admin
def adminSearch(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {'products':products}
    return render(request, 'adminPanel/productMgtlist.html', context)


# sale report on sales in given time
def sales_report(request):
    salesInDate = 0
    if request.method == 'GET':
        startdate = request.GET['startdate']
        enddate = request.GET['enddate']
        if startdate and enddate:
            sale_in_date = Payment.objects.filter(created_at__range=[startdate, enddate])
            for item in sale_in_date:
                salesInDate += float(item.amount_paid)
            product_sold = OrderProduct.objects.filter(created_at__range=[startdate,enddate])
            salesTotal =0
            salesqty =0
            for item in product_sold:
                salesTotal += item.product_price
                salesqty += item.quantity
            
            context ={
                'salesInDate':salesInDate,
                'startdate':startdate,
                'enddate':enddate,
                'product_sold':product_sold,
                'salesTotal':salesTotal,
                'salesqty':salesqty,
            }
            return render(request, 'adminPanel/salesReport.html', context)
        else:
            return redirect('admin_panel')
        

@unauthenticated_admin
def couponsMgt(request):
    coupons = Coupon.objects.all()
    cat_offers = CategoryAllOffer.objects.all()
    context ={
        'coupons':coupons,
        'cat_offers':cat_offers,
    }
    return render(request, 'adminPanel/coupons.html', context)


@unauthenticated_admin
def couponsAdd(request):
    form = CouponApplyAdminForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
        else:
            return redirect('coupons_mgt')
    context = {
        'form':form,
    }
    return render(request, 'adminPanel/couponsAdd.html', context)



@unauthenticated_admin
def deleteCoupon(request, id):
    post = Coupon.objects.get(id=id)
    post.delete()  
    return redirect('coupons_mgt')


@unauthenticated_admin
def couponStatus(request, id):
    post = Coupon.objects.get(id=id)
    if post.active:
        post.active = False
    else:
        post.active = True
    post.save()  
    return redirect('coupons_mgt')