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
from django.contrib import admin
from django.urls import path
from minorproject import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home,name="home"),
    path('login/',views.login,name="login"),
    path('registration/',views.registration,name="registration"),
    path('logout/', views.logout, name='logout'),
    path('blog/',views.blog , name="blog"),
    path('about_us/',views.about_us , name="about_us"),
    path('review/',views.review , name="review"),
    path('filter-reviews/', views.filter_reviews, name='filter_reviews'),
    path('forgot_password_sendotp/',views.forgot_password_sendotp , name="forgot_password_sendotp"),
    path('forgot_password_verifyotp/',views.forgot_password_verifyotp , name="forgot_password_verifyotp"),
]
