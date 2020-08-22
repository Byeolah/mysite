from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import urls


app_name = 'tripus'
urlpatterns = [
    path('', views.index, name='index'),
    path('mytrips/', views.mytrips, name='mytrips'),
    path('mytrips/<int:trip_id>/', views.singletrip, name='singleTrip'),
    path('addtrip/', views.addtrip, name='addTrip'),
    path('mytrips/<int:trip_id>/edit/', views.edittrip, name='editTrip'),
    path('mytrips/<int:trip_id>/delete/', views.deletetrip, name='deleteTrip'),
    path('mytrips/<int:trip_id>/visit-places/', views.visitplace, name='visitPlaceList'),
    path('mytrips/<int:trip_id>/visit-places/add/', views.visitplaceadd, name='visitPlaceAdd'),
    path('mytrips/<int:trip_id>/visit-places/<int:visit_id>/', views.visitplaceview, name='visitPlaceView'),
    path('mytrips/<int:trip_id>/visit-places/<int:visit_id>/edit/', views.visitplaceedit, name='visitPlaceEdit'),
    path('mytrips/<int:trip_id>/visit-places/<int:visit_id>/delete/', views.visitplacedelete, name='visitPlaceDelete'),
    path('mytrips/<int:trip_id>/spending/', views.spending, name='spending'),
    path('mytrips/<int:trip_id>/spending/<int:spending_id>/edit/', views.spendingedit, name='spendingEdit'),
    path('mytrips/<int:trip_id>/spending/<int:spending_id>/delete/', views.spendingdelete, name='spendingDelete'),
    path('mytrips/<int:trip_id>/note/<int:note_id>/edit/', views.noteedit, name='noteEdit'),
    path('mytrips/<int:trip_id>/note/<int:note_id>/delete/', views.notedelete, name='noteDelete'),
    path("login/", auth_views.LoginView.as_view(), name='login'),
    path("logout/", auth_views.LogoutView.as_view(), name='logout'),
    path("signup/", views.signup, name='signup'),
    path("profile/", views.view_profile, name='profile'),
    path("profile/edit/", views.edit_profile, name='editProfile'),
    path("profile/password/", views.change_password, name='changePassword'),
    path('accounts/', include('django.contrib.auth.urls')),
]