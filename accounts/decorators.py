from django.http import HttpResponse
from django.shortcuts import redirect


# user authentication
def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        else:
            return view_func(request,  *args, **kwargs)
    return wrapper_func


# admin session
def unauthenticated_admin(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.session.has_key('is_logged')==False:
            return redirect("login_admin")
        else:
            return view_func(request,  *args, **kwargs)
    return wrapper_func
