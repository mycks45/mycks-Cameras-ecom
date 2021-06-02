from datetime import date
from orders.views import orderComplete
from orders.models import OrderProduct
from django.shortcuts import render,redirect, get_object_or_404
from store.models import product, ReviewRating
from category.models import category
from cart.models import CartItem
from cart.views import _cart_id
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from .forms import ReviewForms
from django.http import HttpResponse

# Create your views here.

# display product in the store page
def store(request, category_slug=None):
    categories = None
    products = None


    if category_slug != None:
        categories = get_object_or_404(category, slug=category_slug)
        products = product.objects.filter(category=categories, is_available=True)
        paginator= Paginator(products, 9)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = product.objects.all().filter(is_available=True).order_by('id')
        paginator= Paginator(products, 9)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {'products':paged_products, 'product_count':product_count}
    return render(request, 'store/store.html', context)


# display products in the product details page
def product_detail(request, category_slug, product_slug):
    try:
        single_product = product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id =_cart_id(request), product1=single_product).exists()
        
    except Exception as e:
        raise e
        
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None
    # reviews 
    reviews = ReviewRating.objects.filter(product_id = single_product.id, status=True)

    context = {
        'single_product':single_product,
        'in_cart':in_cart,
        'orderproduct':orderproduct,
        'reviews':reviews,
        }
    return render(request, 'store/product_detail.html', context)
    
    
def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {'products':products, 'product_count':product_count}
    return render(request, 'store/store.html', context)


@login_required(login_url='user_login')
def submitReview(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForms(request.POST, instance=reviews)
            form.save()
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForms(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                return redirect(url)