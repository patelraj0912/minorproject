from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render,redirect
from pymongo import MongoClient
from django.contrib import messages
from django.core.mail import send_mail
import random
import datetime
from django.core.files.storage import FileSystemStorage

# from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re
from django.http import JsonResponse

# database coonection 
client = MongoClient(settings.MONGO_URI)
db = client['pythontest']

# def check_username_exists(request):
#     if request.method == 'POST':
#         submitted_username = request.POST.get('username')

#         # Retrieve all usernames from MongoDB
#         # if request.session.get("username") == submitted_username:
#         #     return JsonResponse({"exists": True ,'message': 'Username is available'})
#         usernames = db['users'].find({'username': submitted_username})
#         if usernames.count() > 0:
#             return JsonResponse({'exists': True,'message': 'Username already exists'})
#         else:
#             return JsonResponse({'exists': False,'message': 'Username is available'})
        
#         existing_usernames = db.users.find({}, {"_id": 0, "username": 1})
#         username_list = [user['username'] for user in existing_usernames]

#         if submitted_username in username_list:
#             return JsonResponse({'exists': True, 'message': 'Username already exists'})
#         else:
#             return JsonResponse({'exists': False, 'message': 'Username is available'})
    
#     return HttpResponse("404 not found")

def home(request):
    # username = request.session.get('username', None)  # Get the username from the session if exists
    blog_collection = list(db.blogs.find({"status": "1"}).sort('timestamp', -1).limit(3))
    review_collection = list(db.reviews.find({"status": "1"}).sort('timestamp', -1).limit(5))
    contex ={
        "blogs" : blog_collection,
        "reviews" : review_collection
    }
    return render(request, "home.html", contex)


def user_profile(request):
    user = db['users'].find_one({'username': request.session.get('username')})
    return render(request, "user_profile.html",{'user': user})

def update_userdetails(request):
    if request.method == 'POST':
        email = request.POST['email']
        area = request.POST['area']
        city = request.POST['city']
        state = request.POST['state']
        db.users.update_one(
            {"username": request.session.get('username')},
            {"$set": {
                "email": email,
                "area" : area,
                "city" : city,
                "state" : state,
                "lastmodify" : datetime.datetime.now()
            }}
        )
        
        return redirect('user_profile')
    return HttpResponse("404 Not found")

def update_userdpassword(request):
    if request.method == 'POST':
        newpassword = request.POST['newpassword']
        # confirmpassword = request.POST['confirmpassword']
        # if newpassword == confirmpassword:
        db.users.update_one(
            {"username": request.session.get('username')},
            {"$set": {
                "password": newpassword,
                "lastmodify" : datetime.datetime.now()
            }}
        )
        return redirect('user_profile')
        # else:
        #     return HttpResponse("Crash")
    return HttpResponse("404 Not found")

def my_blog(request):
    
    my_blogs = db.blogs.find({"$and":[{'username': request.session.get('username')},{"status": "1"}]}).sort('timestamp', -1)
    return render(request, "my_blog.html", {'blogs': my_blogs})

def delete_my_blog(request, blog_id):
    if request.method == 'POST':
        db.blogs.update_one(
            {"blog_id": blog_id},
            {"$set":{
                "status":'0'
            }})
        
        return redirect('my_blog')
    return HttpResponse('Something went wrong')


def my_review(request):
    
    my_reviews = db.reviews.find({"$and":[{'username': request.session.get('username')},{"status": "1"}]}).sort('timestamp', -1)
    return render(request, "my_review.html", {'reviews': my_reviews})

def delete_my_review(request, r_id):
    if request.method == 'POST':
        db.reviews.update_one(
            {"r_id": r_id},
            {"$set":{
                "status":'0'
            }})
        
        return redirect('my_review')
    return HttpResponse('Something went wrong')



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
            request.session['userarea'] = user['area']
            request.session['usercity'] = user['city']
            return redirect('home')

        messages.error(request, 'Invalid credentials')
        return redirect('login')
    
    return render(request, "user_login.html")

def logout(request):
    request.session.flush()  # Clear the session
    # messages.success(request, 'You have been logged out.')
    return redirect('home')



def about_us(request):
    return render(request,'about_us.html')



def blog(request):
    blog_collection = db.blogs
    if 'username' not in request.session :
        return redirect('home')
    
    if request.method == "POST" :
        username = request.session.get('username')
        dish_name = request.POST['dishname']
        restaurant_name = request.POST['restaurantname']
        area = request.POST['area']
        city = request.POST['city']
        state = request.POST['state']
        blogContent = request.POST['blogContent']
        blogImage = request.FILES['blogImage']
        blog_id = str(blog_collection.count_documents({}) + 1)

        name=f'{blog_id}.jpg'
        fs = FileSystemStorage()
        filename = fs.save(name, blogImage)
        file_url = fs.url(filename)

        blog_collection.insert_one({
            "blog_id": blog_id,
            "dish_name": dish_name,
            "restaurant_name" : restaurant_name,
            "area":area,
            "city":city,
            "state":state,
            "dish_image": file_url,
            "description": blogContent,
            "username": username,
            "timestamp": datetime.datetime.now(),
            "status" : '1'
        })

        # blog_title = request.POST['dishname']
        return redirect('blog')
    
    distinct_dishnames = blog_collection.find({"status": "1"}).distinct("dish_name")
    distinct_restaurantnames = blog_collection.find({"status": "1"}).distinct("restaurant_name")
    distinct_cities = blog_collection.find({"status": "1"}).distinct("city")
    distinct_areas = blog_collection.find({"status": "1"}).distinct("area")
    distinct_state = blog_collection.find({"status": "1"}).distinct("state")
    

    # By default, display all reviews
    blogs_list = list(blog_collection.find({"status": "1"}).sort('timestamp', -1))
   
    context = {
        'blogs': blogs_list,
        'distinct_dishnames': distinct_dishnames,
        'distinct_restaurantnames': distinct_restaurantnames,
        'distinct_cities': distinct_cities,
        'distinct_areas': distinct_areas,
        'distinct_state':distinct_state
    }
    return render(request,'blog.html',context)



def review(request):
    review_collection = db.reviews
    if request.method == 'POST':
        dishname = request.POST['dishname']
        restaurantname = request.POST['restaurantname']
        area = request.POST['area']
        city = request.POST['city']
        description = request.POST['description']
        review={
            'r_id':str(review_collection.count_documents({}) + 1),
            'username' : request.session.get('username'),
            'dishname':dishname,
            'restaurantname':restaurantname,
            'area':area,  
            'city':city,
            'description': description,
            'timestamp': datetime.datetime.now(),
            'status' : "1"
        }
        insert = review_collection.insert_one(review)
        if insert:
            return redirect('review')
        else:
            return HttpResponse("Failed to insert review")
  
    distinct_dishnames = review_collection.find({"status": "1"}).distinct("dishname")
    distinct_restaurantnames = review_collection.find({"status": "1"}).distinct("restaurantname")
    distinct_cities = review_collection.find({"status": "1"}).distinct("city")
    distinct_areas = review_collection.find({"status": "1"}).distinct("area")
    
    # By default, display all reviews
    reviews_list = list(review_collection.find({"status": "1"}).sort('timestamp', -1))
   

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
