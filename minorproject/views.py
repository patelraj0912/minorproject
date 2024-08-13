from django.http import HttpResponse
from django.shortcuts import render,redirect
from .mongodb_client import mongo_client
from django.contrib import messages
from django.core.mail import send_mail
import random
# from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

def home(request):
    username = request.session.get('username', None)  # Get the username from the session if exists
    return render(request, "home.html", {'username': username})

def registration(request):
    if request.method == 'POST':
        email = request.POST['email']
        area = request.POST['area']
        city = request.POST['city']
        state = request.POST['state']
        username = request.POST['username']
        password = request.POST['password']
    
        collection = mongo_client.get_collection('users')
        if collection.find_one({'username': username}):
            messages.error(request, 'Username already exists')
            return redirect('registration')

        data={
            'email':email,
            'area':area,
            'city':city,
            'state':state,  
            'username': username,
            'password': password
        }
        collection.insert_one(data)
        # messages.success(request, 'Signup successful! Please login.')
        return redirect('login')
    return render(request, "user_registration.html")

def login(request):
    if 'username' in request.session :
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        collection = mongo_client.get_collection('users')
        user = collection.find_one({'username': username, 'password': password})
        
        if user:
            request.session['username'] = username
            return redirect('home')

        messages.error(request, 'Invalid credentials')
        return redirect('login')
    
    return render(request, "user_login.html")

def logout(request):
    request.session.flush()  # Clear the session
    # messages.success(request, 'You have been logged out.')
    return redirect('home')


def blog(request):
    return render(request,'blog.html')


def about_us(request):
    return render(request,'about_us.html')

def review(request):
    return render(request,'review.html')