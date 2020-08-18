from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from .models import *
from .forms import *
from django.views import generic
from django.urls import reverse
from pprint import pprint
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django_countries import countries
from country_currencies import get_by_country
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import exchange
import currency_exchange


# Main site.
def index(request):
    return render(request, 'trip/index.html')


# User profile view.
def view_profile(request):
    profile = request.user
    past_trip, future_trip = 0, 0
    current_trip = []
    trips = Trip.objects.filter(user_id=profile.id)
    for trip in trips:
        if trip.comeback_date < datetime.date.today():
            past_trip += 1
        elif trip.departure_date > datetime.date.today():
            future_trip += 1
        else:
            current_trip.append(trip)

    return render(request, 'profile.html', {'profile':profile, 'future_trip':future_trip, 'past_trip':past_trip,
                                            'current_trip':current_trip})


# Change password.
@login_required(login_url='/tripus/login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, _('Your password was updated successfully!'))
            return redirect(reverse('tripus:profile'))
        else:
            return redirect(reverse('tripus:changePassword'))
    else:
        form = PasswordChangeForm(user=request.user)

        args = {'form': form}
        return render(request, 'change_password.html', args)


# View single trip.
def singletrip(request, trip_id):
    trip = Trip.objects.get(id=trip_id)
    for name, key in countries:
        if key == trip.country:
            country_code = name
    country_currency = get_by_country(country_code)[0]

    if request.method == 'POST':
        form = SpendingForm(request.POST)
        if country_currency == 'PLN':
            form.fields['currency_code'].choices = [(country_currency, country_currency)]
        else:
            form.fields['currency_code'].choices = [(country_currency, country_currency), ('PLN', 'PLN')]
        form.fields['currency_code'].initial = country_currency
        if form.is_valid():
            name = form.cleaned_data['name']
            price = form.cleaned_data['price']
            currency_code = form.cleaned_data['currency_code']
            date = form.cleaned_data['date']
            s = Spending(name=name, price=price, currency_code=currency_code, date=date, trip_id=trip_id)
            s.save()
            return redirect('tripus:singleTrip', trip_id)
    else:
        form = SpendingForm(initial={'currency_code':country_currency})
        if country_currency == 'PLN':
            form.fields['currency_code'].choices = [(country_currency, country_currency)]
        else:
            form.fields['currency_code'].choices = [(country_currency, country_currency), ('PLN', 'PLN')]
        #form.fields['currency_code'].initial = country_currency

    spending_record = Spending.objects.filter(trip_id=trip_id).order_by('-id')[:5]
    places_list = Visit.objects.filter(trip_id=trip_id).order_by('-id')[:5]

    topln = round(Decimal(currency_exchange.exchange(country_currency, 'PLN', 1)[0][:-4]), 2)
    frompln = round(Decimal(currency_exchange.exchange('PLN', country_currency, 1)[0][:-4]), 2)

    return render(request, 'trip/singletrip.html', {'my_trip': trip, 'spending_record': spending_record, 'places_list':places_list,
                                                    'form_spending': form,'trip_id': trip.id, 'topln': topln, 'frompln': frompln,
                                                    'country_currency': country_currency})


# Spending page.
def spending(request, trip_id):
    trip = Trip.objects.get(id=trip_id)
    for name, key in countries:
        if key == trip.country:
            country_code = name
    country_currency = get_by_country(country_code)[0]

    if request.method == 'POST':
        form = SpendingForm(request.POST)
        if country_currency == 'PLN':
            form.fields['currency_code'].choices = [(country_currency, country_currency)]
        else:
            form.fields['currency_code'].choices = [(country_currency, country_currency), ('PLN', 'PLN')]
        form.fields['currency_code'].initial = country_currency
        if form.is_valid():
            name = form.cleaned_data['name']
            price = form.cleaned_data['price']
            currency_code = form.cleaned_data['currency_code']
            date = form.cleaned_data['date']
            s = Spending(name=name, price=price, currency_code=currency_code, date=date, trip_id=trip_id)
            s.save()
            return redirect('tripus:spending', trip_id)
    else:
        form = SpendingForm()
        if country_currency == 'PLN':
            form.fields['currency_code'].choices = [(country_currency, country_currency)]
        else:
            form.fields['currency_code'].choices = [(country_currency, country_currency), ('PLN', 'PLN')]
        form.fields['currency_code'].initial = country_currency

    spending_record = Spending.objects.filter(trip_id=trip_id).order_by('-id')
    sum = 0
    for i in spending_record:
        if i.currency_code == 'PLN':
            sum = sum + i.price
        else:
            val = currency_exchange.exchange(i.currency_code, 'PLN', i.price)
            val = round(Decimal(val[0][:-4]), 2)
            sum = sum + val

    sum_exch = currency_exchange.exchange('PLN', country_currency, sum)
    sum_exch = round(Decimal(sum_exch[0][:-4]), 2)
    return render(request, 'trip/spending.html', {'spending_record': spending_record, 'form_spending': form, 'trip_id': trip_id,
                                                  'trip':trip, 'sum':sum, 'sum_exch': sum_exch, 'country_currency': country_currency,
                                                  'spending_site': 1})


# Edit spending.
def spendingedit(request, trip_id, spending_id):
    instance = Spending.objects.get(id=spending_id)
    trip = Trip.objects.get(id=trip_id)
    for name, key in countries:
        if key == trip.country:
            country_code = name
    country_currency = get_by_country(country_code)[0]
    if request.method == 'POST':
        form = SpendingForm(request.POST, instance=instance)
        if country_currency == 'PLN':
            form.fields['currency_code'].choices = [(country_currency, country_currency)]
        else:
            form.fields['currency_code'].choices = [(country_currency, country_currency), ('PLN', 'PLN')]
        form.fields['currency_code'].initial = country_currency
        if form.is_valid():
            form.save()
            messages.success(request, _('Spending was updated successfully!'))
            return redirect('tripus:spending', trip_id=trip_id)
    else:
        form = SpendingForm(instance=instance)
        if country_currency == 'PLN':
            form.fields['currency_code'].choices = [(country_currency, country_currency)]
        else:
            form.fields['currency_code'].choices = [(country_currency, country_currency), ('PLN', 'PLN')]
        form.fields['currency_code'].initial = country_currency

    return render(request, 'spending/editspending.html', {'form': form, 'spending':instance, 'trip_id':trip_id})


# Delete spending.
def spendingdelete(request, trip_id, spending_id):
    instance = get_object_or_404(Spending, id=spending_id)
    if request.method == "POST":
        form = SpendingDeleteForm(request.POST, instance=instance)
        if form.is_valid():
            instance.delete()
            messages.success(request, _('Spending was deleted successfully!'))
            return redirect('tripus:spending', trip_id=trip_id)
    else:
        form = SpendingDeleteForm(instance=instance)

    return render(request, 'spending/deletespending.html', {'form': form, 'spending': instance, 'trip_id':trip_id })


class MytripsView(generic.ListView):
    context_object_name = 'my_trip_list'
    template_name = 'trip/trip_list.html'

    def get_queryset(self):
        my_trip_list = Trip.objects.filter(user_id=self.request.user.id).order_by('departure_date')
        for i in my_trip_list:
            i.url = i.name.replace(' ', '-').lower()
        return my_trip_list


# Add trip.
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
            user_id = request.user.id
            t = Trip(name=name, country=country, city=city, departure_date=departure_date, comeback_date=comeback_date, target=target, user_id=user_id)
            t.save()
            return redirect('tripus:singleTrip', pk=t.pk)
    else:
        form = AddTripForm()
    return render(request, 'trip/addtrip.html', {'form': form})


# Edit trip.
def edittrip(request, trip_id):
    mytrip = get_object_or_404(Trip, id=trip_id)
    if request.method == 'POST':
        form = AddTripForm(request.POST)
    else:
        form = AddTripForm()
    return render(request, 'trip/addtrip.html', {'form': form})


# Display places to visit
def visitplace(request, trip_id):
    places_list = Visit.objects.filter(trip_id=trip_id)
    return render(request, 'trip/visitlist.html', {'trip_id':trip_id, 'places_list':places_list})


# Add place to visit
def visitplaceadd(request, trip_id):
    if request.method == 'POST':
        form = VisitForm(request.POST, initial={'visited': False})
        if form.is_valid():
            form.process()
            bbb = form.save(commit=False)
            bbb.trip_id = trip_id
            bbb.save()
            messages.success(request, _('You added a new place to visit!'))
            return redirect('tripus:visitPlaceList', trip_id=trip_id)
    else:
        form = VisitForm()
    return render(request, 'trip/addplace.html', {'form': form, 'trip_id':trip_id})


# Edit place to visit.
def visitplaceedit(request, trip_id, visit_id):
    instance = Visit.objects.get(id=visit_id)
    if request.method == 'POST':
        form = VisitForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, _('Place was updated successfully!'))
            return redirect('tripus:visitPlaceView', trip_id=trip_id, visit_id=visit_id)
    else:
        form = VisitForm(instance=instance)

    return render(request, 'trip/editplace.html', {'form': form, 'place':instance, 'trip_id':trip_id})


# Delete place.
def visitplacedelete(request, trip_id, visit_id):
    instance = get_object_or_404(Visit, id=visit_id)
    if request.method == "POST":
        form = VisitDeleteForm(request.POST, instance=instance)
        if form.is_valid():
            instance.delete()
            return redirect('tripus:visitPlaceList', trip_id=trip_id)
    else:
        form = VisitDeleteForm(instance=instance)

    return render(request, 'trip/deleteplace.html', {'form': form, 'place': instance, 'trip_id':trip_id })


# View single place to visit.
def visitplaceview(request, trip_id, visit_id):
    place = Visit.objects.get(id=visit_id)
    return render(request, 'trip/viewplace.html', {'place':place, 'trip_id':trip_id})


# Login.
def userlogin(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)


# Sign up.
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


# Edit user's profile.
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your profile was updated successfully!'))
            return redirect(reverse('tripus:profile'))
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'editprofile.html', {'form': form})