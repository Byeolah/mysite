from django.urls import path
from . import views

app_name = 'tripus'
urlpatterns = [
    path('', views.index, name='index'),
    path('mytrips/', views.MytripsView.as_view(), name='mytrips'),
    path('mytrips/<int:pk>/', views.SingletripView.as_view(), name='singleTrip'),
    path('addtrip/', views.addtrip, name='addTrip'),
]