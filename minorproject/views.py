from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render,redirect
from pymongo import MongoClient
from django.contrib import messages
from django.core.mail import send_mail
import random
import datetime
from django.core.files.storage import FileSystemStorage




# database coonection 
client = MongoClient(settings.MONGO_URI)
db = client['pythontest']


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
    if 'username' not in request.session :
        return redirect('not_found_404')
    user = db['users'].find_one({'username': request.session.get('username')})
    return render(request, "user_profile.html",{'user': user})

def update_userdetails(request):
    if 'username' not in request.session :
        return redirect('not_found_404')
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
    if 'username' not in request.session :
        return redirect('not_found_404')
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



def critic_request(request):
    if 'username' not in request.session :
        return redirect('not_found_404')
    if request.method=="POST":
        u_id = request.POST['u_id']
        email = request.POST['email']
        db.users.update_one(
            {"u_id": u_id},
            {"$set":{
                "status":'1'
            }})
        send_mail(
            'Verify your Critic account',
            f'Hey, Critic welcome to family explore restaurant or cafes and make blogs',
            'grpcx7@gmail.com',
            [email],
            fail_silently=False,)
        # return HttpResponse("activated")
    critic_requests=db.users.find({"$and":[{"level": "critic"},{"status": "-1"}]}).sort('timestamp', -1)
    return render(request,"critic_request.html",{'critics':critic_requests})

def user_list(request):
    if 'username' not in request.session :
        return redirect('not_found_404')
    user_collection=db.users
    active_users=list(user_collection.find({"$and":[{"level": "user"},{"status": "1"}]}).sort('timestamp', -1))
    active_critics=list(user_collection.find({"$and":[{"level": "critic"},{"status": "1"}]}).sort('timestamp', -1))
    unactive_users=list(user_collection.find({"$and":[{"level": "user"},{"status": "0"}]}).sort('timestamp', -1))
    unactive_critics=list(user_collection.find({"$and":[{"level": "critic"},{"status": "0"}]}).sort('timestamp', -1))
    admin_list=list(user_collection.find({"$and":[{"level": "admin"},{"status": "1"}]}).sort('timestamp', -1))

    context={
        'active_users':active_users,
        'active_critics':active_critics,
        'unactive_users':unactive_users,
        'unactive_critics':unactive_critics,
        'admin_list':admin_list
    }
    return render(request,"user_list.html",context)

#for user delete account action by admin
def delete_user(request,u_id):
    if 'username' not in request.session :
        return redirect('not_found_404')
    if request.method == 'POST':
        username = request.POST['username']
        level = request.POST['level']
        db.users.update_one(
            {"u_id": u_id},
            {"$set":{
                "status":'0'
            }})
        if(level=="critic"):
            db.blogs.update_many(
                {"username":username},
                {"$set":{
                    "status":'00'
                }})
        elif(level=="user"):
            db.reviews.update_many(
                {"username":username},
                {"$set":{
                    "status":'00'
                }})
        return redirect('user_list')
    return HttpResponse('Opration Failed')

#for user delete account action by user
def delete_user_account(request): 
    if 'username' not in request.session :
        return redirect('not_found_404')
    if request.method == 'POST':
        u_id = request.session.get('u_id')
        db.users.update_one(
            {"u_id": u_id},
            {"$set":{
                "status":'0'
            }})
        username = request.session.get('username')
        userlevel = request.session.get('userlevel')
        if(userlevel == "critic"):
            # delete blogs of critics
            db.blogs.update_many(
                {"username":username},
                {"$set":{
                    "status":"0"
                }})
        elif(userlevel == "user"):
            db.reviews.update_many(
            # delete reviews of critics
                {"username" : username},
                {"$set":{
                    "status":"0"
                }})
        return redirect('logout')
    return HttpResponse('operation Failed')

def make_admin(request,u_id):
    if 'username' not in request.session :
        return redirect('not_found_404')
    if request.method == 'POST':
        db.users.update_one(
            {"u_id": u_id},
            {"$set":{
                "level":'admin'
            }})
        return redirect('user_list')
    return HttpResponse('Opration Failed')

def make_user(request,u_id):
    if 'username' not in request.session :
        return redirect('not_found_404')
    if request.method == 'POST':
        db.users.update_one(
            {"u_id": u_id},
            {"$set":{
                "level":'user'
            }})
        return redirect('user_list')
    return HttpResponse('Opration Failed')

def active_user(request,u_id):
    if 'username' not in request.session :
        return redirect('not_found_404')
    if request.method == 'POST':
        db.users.update_one(
            {"u_id": u_id},
            {"$set":{
                "status":'1'
            }})
        # activate user's data(reviews,blog)
        # query = {"u_id": u_id}
        # Specify the field to retrieve (only 'email' in this case)
        # projection = { "_id":0,"username": 1, "level": 1}  # _id: 0 to exclude the _id field from the result
        # user_info = db.uers.find_one(query, projection) # Retrieve the document
        # if user_info:
        #     username = user_info.get('username')
        #     level = user_info.get('level')
        #     if(level=="critic"):
        #         db.blogs.update_many(
        #             {"username":username},
        #             {"$set":{
        #                 "status":'1'
        #             }})
        #     elif(level=="user"):
        #         db.reviews.update_many(
        #             {"username":username},
        #             {"$set":{
        #                 "status":'1'
        #             }})
        # else:
        #     username = None
        #     level = None
        return redirect('user_list')
    return HttpResponse('Opration Failed')




def my_review(request):
    if 'username' not in request.session :
        return redirect('not_found_404')
    my_reviews = db.reviews.find({"$and":[{'username': request.session.get('username')},{"status": "1"}]}).sort('timestamp', -1)
    return render(request, "my_review.html", {'reviews': my_reviews})

def delete_my_review(request, r_id):
    if 'username' not in request.session :
        return redirect('not_found_404')
    if request.method == 'POST':
        db.reviews.update_one(
            {"r_id": r_id},
            {"$set":{
                "status":'0'
            }})
        
        return redirect('my_review')
    return HttpResponse('Something went wrong')

def edit_my_review(request,r_id):
    review_collection=db.reviews
    if 'username' not in request.session :
        return redirect('not_found_404')
    if request.method == 'POST':
        dishname = request.POST['dishname']
        restaurantname = request.POST['restaurantname']
        area = request.POST['area']
        city = request.POST['city']
        description = request.POST['description']
        review_collection.update_one(
            {"r_id": r_id},
            {"$set": {
                'dishname':dishname.lower(),
                'restaurantname':restaurantname.lower(),
                'area':area.lower(),  
                'city':city.lower(),
                'description': description.lower(),
                'lastmodify': datetime.datetime.now(),
            }}
        )
        
        return redirect('my_review')
    review_data = review_collection.find_one({'r_id': r_id,'status':"1"})
    return render(request,'edit_my_review.html',{'review':review_data})


def my_blog(request):
    if 'username' not in request.session :
        return redirect('not_found_404')
    my_blogs = db.blogs.find({"$and":[{'username': request.session.get('username')},{"status": "1"}]}).sort('timestamp', -1)
    return render(request, "my_blog.html", {'blogs': my_blogs})

def delete_my_blog(request, b_id):
    if 'username' not in request.session :
        return redirect('not_found_404')
    if request.method == 'POST':
        db.blogs.update_one(
            {"b_id": b_id},
            {"$set":{
                "status":'0'
            }})
        
        return redirect('my_blog')
    return HttpResponse('Something went wrong')

def edit_my_blog(request,b_id):
    blog_collection=db.blogs
    if 'username' not in request.session :
        return redirect('not_found_404')
    if request.method == 'POST':
        dishname = request.POST['dishname']
        restaurantname = request.POST['restaurantname']
        area = request.POST['area']
        city = request.POST['city']
        state = request.POST['state']
        description = request.POST['blogContent']
        blog_collection.update_one(
            {"b_id": b_id},
            {"$set": {
                'dish_name':dishname.lower(),
                'restaurant_name':restaurantname.lower(),
                'area':area.lower(),  
                'city':city.lower(),
                'state':state.lower(),
                'description': description.lower(),
                'lastmodify': datetime.datetime.now(),
            }}
        )
        
        return redirect('my_blog')
    blog_data = blog_collection.find_one({'b_id': b_id,'status':"1"})
    return render(request,'edit_my_blog.html',{'blog':blog_data})





def delete_review_by_admin(request,r_id):
    if 'username' not in request.session :
        return redirect('not_found_404')
    if request.method == 'POST':
        db.reviews.update_one(
            {"r_id": r_id},
            {"$set":{
                "status":"00"
            }})
        
        return redirect('review')
    return HttpResponse('Something went wrong')

def delete_blog_by_admin(request,b_id):
    if 'username' not in request.session :
        return redirect('not_found_404')
    if request.method == 'POST':
        db.blogs.update_one(
            {"b_id": b_id},
            {"$set":{
                "status":"00"
            }})
        
        return redirect('blog')
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
        usertype = request.POST['usertype']

        if usertype == "critic":
            status="-1"
        else :
            status="1"
        user_collection = db.users
        if user_collection.find_one({"$or": [{"username": username}, {"email": email}]}):
            messages.error(request, 'Username or Email already exists')
            return redirect('registration')
        # print(f'Selected gender: {usertype}')
        data={
            'u_id':str(user_collection.count_documents({}) + 1),
            'email':email.lower(),
            'username': username.lower(),
            'level':usertype.lower(),
            'area':area.lower(),
            'city':city.lower(),
            'state':state.lower(),  
            'password': password,
            'status':status,
            'timestamp':datetime.datetime.now(),
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
        user = user_collection.find_one({'username': username, 'password': password,'status':"1"})
        
        if user:
            request.session['username'] = username
            request.session['userlevel'] = user['level']
            request.session['userarea'] = user['area']
            request.session['usercity'] = user['city']
            request.session['u_id'] = user['u_id']
            return redirect('home')

        messages.error(request, 'Invalid credentials')
        return redirect('login')
    
    return render(request, "user_login.html")

def logout(request):
    if 'username' not in request.session :
        return redirect('not_found_404')
    request.session.flush()  # Clear the session
    return redirect('home')



def about_us(request):
    return render(request,'about_us.html')



def blog(request):
    blog_collection = db.blogs
    
    if request.method == "POST" :
        username = request.session.get('username')
        dish_name = request.POST['dishname']
        restaurant_name = request.POST['restaurantname']
        area = request.POST['area']
        city = request.POST['city']
        state = request.POST['state']
        blogContent = request.POST['blogContent']
        blogImage = request.FILES['blogImage']
        b_id = str(blog_collection.count_documents({}) + 1)

        name=f'{b_id}.jpg'
        fs = FileSystemStorage()
        filename = fs.save(name, blogImage)
        file_url = fs.url(filename)

        blog_collection.insert_one({
            "b_id": b_id,
            "dish_name": dish_name.lower(),
            "restaurant_name" : restaurant_name.lower(),
            "area":area.lower(),
            "city":city.lower(),
            "state":state.lower(),
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

def filter_blogs(request):
    dishname = request.GET.get('dishname', '')
    restaurantname = request.GET.get('restaurantname', '')
    state = request.GET.get('state', '')
    city = request.GET.get('city', '')
    area = request.GET.get('area', '')
    query = request.GET.get('query', '')

    blog_collection = db.blogs
    query_filter = {"status": "1"}  # Start with the base query

    # Apply filters
    if dishname:
        query_filter['dish_name'] = dishname
    if restaurantname:
        query_filter['restaurant_name'] = restaurantname
    if state:
        query_filter['state'] = state
    if city:
        query_filter['city'] = city
    if area:
        query_filter['area'] = area

    # Apply search query to all relevant fields
    if query:
        query_filter['$or'] = [
            {"dish_name": {"$regex": query, "$options": "i"}},
            {"restaurant_name": {"$regex": query, "$options": "i"}},
            {"state": {"$regex": query, "$options": "i"}},
            {"city": {"$regex": query, "$options": "i"}},
            {"area": {"$regex": query, "$options": "i"}}
        ]

    blogs_list = list(blog_collection.find(query_filter).sort('timestamp', -1))

    return render(request, 'blog_list.html', {'blogs': blogs_list})



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
            'dishname':dishname.lower(),
            'restaurantname':restaurantname.lower(),
            'area':area.lower(),  
            'city':city.lower(),
            'description': description.lower(),
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
    if 'username' in request.session :
        return redirect('home')
    if request.method == 'POST':
        email=request.POST['email']
        users_collection = db.users
        user = users_collection.find_one({'email': email,'status':"1"})
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
            messages.error(request, 'Invalid Email')
            return redirect('forgot_password_sendotp')
        
    return render(request, 'forgot_password_sendotp.html')

def forgot_password_verifyotp(request):
    if 'username' in request.session :
        return redirect('home')
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
                messages.error(request, 'Password and Confirm Password does not match')
                return redirect('forgot_password_verifyotp')
        messages.error(request, 'Invalid OTP')
        return redirect('forgot_password_verifyotp')
    return render(request,'forgot_password_verifyotp.html')

def not_found_404(request):
    return render(request,"404_not_found.html")
