from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from .models import Trip
from .forms import *
from django.views import generic
from django.urls import reverse
from pprint import pprint
from django.views.generic import UpdateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm

def index(request):
    return render(request, 'trip/index.html')


def profile(request):
    return render(request, 'profile.html')


#Single trip view.
class SingletripView(generic.DetailView):
    context_object_name = 'my_trip'
    model = Trip
    template_name = 'trip/singletrip.html'

class PersonUpdateView(generic.UpdateView):
    model = Trip
    form_class = PersonForm
    template_name = 'trip/addtrip.html'

class MytripsView(generic.ListView):
    context_object_name = 'my_trip_list'
    template_name = 'trip/trip_list.html'

    def get_queryset(self):
        my_trip_list = Trip.objects.filter(user_id=self.request.user.id).order_by('departure_date')
        for i in my_trip_list:
            i.url = i.name.replace(' ', '-').lower()
        return my_trip_list


def addtrip(request): #TODO zrób z tego klasę
    if request.method == 'POST':
        form = AddTripForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            country = form.cleaned_data['country']
            city = form.cleaned_data['city']
            departure_date = form.cleaned_data['departure_date']
            comeback_date = form.cleaned_data['comeback_date']
            target = form.cleaned_data['target']
            user_id = request.user.id
            t = Trip(name=name, country=country, city=city, departure_date=departure_date, comeback_date=comeback_date, target=target, user_id=user_id)
            t.save()
            return redirect('tripus:singleTrip', pk=t.pk)#todo redirect do nowej podróży
    else:
        form = AddTripForm()
    return render(request, 'trip/addtrip.html', {'form': form})


def userlogin(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('tripus:mytrips')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


