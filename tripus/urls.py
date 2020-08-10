from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import urls

app_name = 'tripus'
urlpatterns = [
    path('', views.index, name='index'),
    path('mytrips/', views.MytripsView.as_view(), name='mytrips'),
    path('mytrips/<int:pk>/', views.SingletripView.as_view(), name='singleTrip'),
    path('addtrip/', views.addtrip, name='addTrip'),
    path('addperson/', views.PersonUpdateView.as_view(), name='addPerson'),
    path("login/", auth_views.LoginView.as_view(), name='login'),
    path("logout/", auth_views.LogoutView.as_view(), name='logout'),
    path("signup/", views.signup, name='signup'),
    path("profile/", views.profile, name='profile'),
    path('accounts/', include('django.contrib.auth.urls')),
]