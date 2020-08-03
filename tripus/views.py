from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from .models import Trip
from .forms import *
from django.views import generic
from django.urls import reverse
from pprint import pprint


def index(request):
    return HttpResponse("Hello, world. You're at the main site of your app.")


#Single trip view.
class SingletripView(generic.DetailView):
    context_object_name = 'my_trip'
    model = Trip
    template_name = 'trip/singletrip.html'


class MytripsView(generic.ListView):
    context_object_name = 'my_trip_list'
    template_name = 'trip/index.html'

    def get_queryset(self):
        my_trip_list = Trip.objects.all()
        for i in my_trip_list:
            i.url = i.name.replace(' ', '-').lower()
        return my_trip_list


def addtrip(request):
    if request.method == 'POST':
        form = AddTripForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            country = form.cleaned_data['country']
            city = form.cleaned_data['city']
            departure_date = form.cleaned_data['departure_date']
            comeback_date = form.cleaned_data['comeback_date']
            target = form.cleaned_data['target']
            t = Trip(name=name, country=country, city=city, departure_date=departure_date, comeback_date=comeback_date, target=target)
            t.save()
            return HttpResponseRedirect('/mytrips/')
    else:
        form = AddTripForm()
    return render(request, 'trip/add_trip.html', {'form': form})


