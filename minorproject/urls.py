"""
URL configuration for minorproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path
from minorproject import views
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home,name="home"),
    path('login/',views.login,name="login"),
    path('registration/',views.registration,name="registration"),
    path('logout/', views.logout, name='logout'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('update_userdetails/', views.update_userdetails, name='update_userdetails'),
    path('update_userdpassword/', views.update_userdpassword, name='update_userdpassword'),
    path('critic_request/', views.critic_request, name='critic_request'),
    path('user_list/', views.user_list, name='user_list'),
    path('delete_user/<str:u_id>/',views.delete_user , name="delete_user"),
    path('delete_user_account/',views.delete_user_account , name="delete_user_account"),
    path('make_admin/<str:u_id>/',views.make_admin , name="make_admin"),
    path('active_user/<str:u_id>/',views.active_user , name="active_user"),
    path('make_user/<str:u_id>/',views.make_user , name="make_user"),
    path('my_blog/', views.my_blog, name='my_blog'),
    path('my_review/', views.my_review, name='my_review'),
    path('blog/',views.blog , name="blog"),
    path('delete_my_blog/<str:b_id>/',views.delete_my_blog , name="delete_my_blog"),
    path('about_us/',views.about_us , name="about_us"),
    path('review/',views.review , name="review"),
    path('delete_my_review/<str:r_id>/',views.delete_my_review , name="delete_my_review"),
    path('edit_my_review/<str:r_id>/',views.edit_my_review , name="edit_my_review"),
    path('edit_my_blog/<str:b_id>/',views.edit_my_blog , name="edit_my_blog"),
    path('delete_review_by_admin/<str:r_id>/',views.delete_review_by_admin , name="delete_review_by_admin"),
    path('delete_blog_by_admin/<str:b_id>/',views.delete_blog_by_admin , name="delete_blog_by_admin"),
    path('delete_user/<str:u_id>/',views.delete_user , name="delete_user"),
    path('filter-reviews/', views.filter_reviews, name='filter_reviews'),
    path('filter-blogs/', views.filter_blogs, name='filter_blogs'),
    path('forgot_password_sendotp/',views.forgot_password_sendotp , name="forgot_password_sendotp"),
    path('forgot_password_verifyotp/',views.forgot_password_verifyotp , name="forgot_password_verifyotp"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

