from django.shortcuts import render,redirect
from django.http import HttpResponse
from store.models import product

# Create your views here.



def home(request):
    products = product.objects.all().filter(is_available=True)

    context = {'products':products,}
    return render(request, 'home.html', context)


def contactUs(request):
    return render(request, 'contactUs.html')
