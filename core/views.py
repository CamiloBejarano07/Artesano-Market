from django.shortcuts import render

def home(request):
    return render(request, 'pages/index.html')

def catalogo(request):
    return render(request, 'pages/catalog.html')

def contacto(request):
    return render(request, 'pages/help.html')

def login_view(request):
    return render(request, 'auth/login.html')

def register_view(request):
    return render(request, 'auth/register.html')

def cart(request):
    return render(request, 'pages/cart.html')

def checkout(request):
    return render(request, 'pages/checkout.html')


    
