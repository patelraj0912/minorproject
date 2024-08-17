from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render,redirect
from pymongo import MongoClient
from django.contrib import messages
from django.core.mail import send_mail
import random
import datetime
# from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout


from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re

client = MongoClient(settings.MONGO_URI)
db = client['pythontest']


def home(request):
    username = request.session.get('username', None)  # Get the username from the session if exists
    return render(request, "home.html", {'username': username})

def registration(request):
    if 'username' in request.session :
        return redirect('home')
    if request.method == 'POST':
        email = request.POST['email'].strip()
        area = request.POST['area'].strip()
        city = request.POST['city'].strip()
        state = request.POST['state'].strip()
        username = request.POST['username'].strip()
        password = request.POST['password'].strip()
    
        user_collection = db.users
        if user_collection.find_one({"$or": [{"username": username}, {"email": email}]}):
            messages.error(request, 'Username or Email already exists')
            return redirect('registration')

        data={
            'email':email,
            'area':area,
            'city':city,
            'state':state,  
            'username': username,
            'password': password
        }
        user_collection.insert_one(data)
        return redirect('login')
        
    return render(request, "user_registration.html")

def login(request):
    if 'username' in request.session :
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user_collection = db.users
        user = user_collection.find_one({'username': username, 'password': password})
        
        if user:
            request.session['username'] = username
            request.session['userlevel'] = user['level']
            return redirect('home')

        messages.error(request, 'Invalid credentials')
        return redirect('login')
    
    return render(request, "user_login.html")

def logout(request):
    request.session.flush()  # Clear the session
    # messages.success(request, 'You have been logged out.')
    return redirect('home')


def blog(request):
    if 'username' not in request.session :
        return redirect('home')
    return render(request,'blog.html')


def about_us(request):
    return render(request,'about_us.html')

def review(request):
    review_collection = db.reviews
    if request.method == 'POST':
        dishname = request.POST['dishname']
        restaurantname = request.POST['restaurantname']
        area = request.POST['area']
        city = request.POST['city']
        description = request.POST['description']
        review={
            'username' : request.session.get('username'),
            'dishname':dishname,
            'restaurantname':restaurantname,
            'area':area,  
            'city':city,
            'description': description,
            'timestamp': datetime.datetime.now()
        }
        insert = review_collection.insert_one(review)
        if insert:
            return redirect('review')
        else:
            return HttpResponse("Failed to insert review")
  
    distinct_dishnames = review_collection.distinct("dishname")
    distinct_restaurantnames = review_collection.distinct("restaurantname")
    distinct_cities = review_collection.distinct("city")
    distinct_areas = review_collection.distinct("area")
    
    # By default, display all reviews
    reviews_list = list(review_collection.find())

    context = {
        'reviews': reviews_list,
        'distinct_dishnames': distinct_dishnames,
        'distinct_restaurantnames': distinct_restaurantnames,
        'distinct_cities': distinct_cities,
        'distinct_areas': distinct_areas
    }
    return render(request,'review.html', context)
    # reviews_list = list(collection.find())
    # return render(request, 'reviews.html', {'reviews': reviews_list})

def filter_reviews(request):
    dishname = request.GET.get('dishname', '')
    restaurantname = request.GET.get('restaurantname', '')
    city = request.GET.get('city', '')
    area = request.GET.get('area', '')
    query = request.GET.get('query', '')
    review_collection = db.reviews
    # Build the query based on the provided filters and search query
    query_filter = {}
    if dishname:
        query_filter['dishname'] = dishname
    if restaurantname:
        query_filter['restaurantname'] = restaurantname
    if city:
        query_filter['city'] = city
    if area:
        query_filter['area'] = area
    if query:
        query_filter['$or'] = [
            {"dishname": {"$regex": query, "$options": "i"}},
            {"restaurantname": {"$regex": query, "$options": "i"}},
            {"city": {"$regex": query, "$options": "i"}},
            {"area": {"$regex": query, "$options": "i"}}
        ]

    # Filter the reviews collection
    reviews_list = list(review_collection.find(query_filter))

    return render(request, 'reviews_list.html', {'reviews': reviews_list})


def forgot_password_sendotp(request):
    if request.method == 'POST':
        email=request.POST['email']
        users_collection = db.users
        user = users_collection.find_one({'email': email})
        if user :
            generated_otp = str(random.randint(100000, 999999))
            request.session['otp'] = generated_otp
            request.session['email']=email
            send_mail(
            'Verify your email',
            f'Your Reset Password code is: {generated_otp}',
            'grpcx7@gmail.com',
            [email],
            fail_silently=False,)
            return redirect('forgot_password_verifyotp')
        else :
            return redirect('forgot_password_sendotp')
        
    return render(request, 'forgot_password_sendotp.html')

def forgot_password_verifyotp(request):
    if request.method == 'POST':
        otp = request.POST['otp']
        if otp == request.session.get('otp'):
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']
            if password == confirm_password:
                filter_query = {"email": request.session.get('email') }
                new_values = {"$set": {"password": password}}
                user_collection = db.users
                user_collection.update_one(filter_query, new_values)
                del request.session['otp']
                del request.session['email']
                return redirect("login")
            else :
                return HttpResponse("Password and Confirm Password must be same")
        return HttpResponse("OTP not match")
    return render(request,'forgot_password_verifyotp.html')
