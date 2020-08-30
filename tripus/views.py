from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from .forms import *
from .decorators import *
from django.urls import reverse
from pprint import pprint
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from country_currencies import get_by_country
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import currency_exchange
from django.db.models import F, Count
from pyowm.owm import OWM
from pyowm.utils.config import get_default_config
from geopy import geocoders
from django_countries.data import COUNTRIES


# Main site.
def index(request):
    popular_country = Trip.objects.values_list('country').annotate(country_count=Count('name'))[:3]
    country_list = []
    for country in popular_country:
        country_list.append(COUNTRIES[country[0]])
    return render(request, 'index.html', {'country_list': country_list})


# Info.
def info(request):
    return render(request, 'info.html')


# <----------User section---------->


# User profile view.
@login_required(login_url='/tripus/login')
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

    return render(request, 'profile.html', {'profile': profile, 'future_trip': future_trip, 'past_trip': past_trip,
                                            'current_trip': current_trip})


# Edit user's profile.
@login_required(login_url='/tripus/login')
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


# Delete user's profile.
@login_required(login_url='/tripus/login')
def delete_profile(request):
    instance = get_object_or_404(User, id=request.user.id)
    if request.method == "POST":
        form = UserDeleteForm(request.POST, instance=instance)
        if form.is_valid():
            instance.delete()
            messages.success(request, _('User was deleted successfully!'))
            return redirect('tripus:index')
    else:
        form = UserDeleteForm(instance=instance)

    return render(request, 'deleteuser.html', {'form': form, 'user': instance})


# Login.
def userlogin(request):
    if request.user.is_anonymous:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
    else:
        return (redirect('tripus:index'))


# Sign up.
def signup(request):
    if request.user.is_anonymous:
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
    else:
        return (redirect('tripus:index'))


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

        return render(request, 'change_password.html', {'form': form})


# <----------Trip section---------->


# View all trips.
def mytrips(request):
    trips = Trip.objects.filter(user_id=request.user.id).order_by('departure_date')
    current_trip, future_trip, past_trip = [], [], []
    for trip in trips:
        if trip.comeback_date < datetime.date.today():
            trip.country = COUNTRIES[trip.country]
            past_trip.append(trip)
        elif trip.departure_date > datetime.date.today():
            trip.country = COUNTRIES[trip.country]
            future_trip.append(trip)
        else:
            trip.country = COUNTRIES[trip.country]
            current_trip.append(trip)

    return render(request, 'trip/trip_list.html', {'past_trip': past_trip, 'future_trip': future_trip,
                                                   'current_trip': current_trip})


# View single trip.
@user_is_trip_author
def singletrip(request, trip_id):
    trip = Trip.objects.get(id=trip_id)
    note_exists = Note.objects.filter(trip_id=trip_id).count()
    ticket = Ticket.objects.filter(trip_id=trip_id).order_by('-id')[:5]
    spending_record = Spending.objects.filter(trip_id=trip_id).order_by('-id')[:5]
    places_list = Visit.objects.filter(trip_id=trip_id).order_by(F('visit_date').asc(nulls_last=True))[:5]
    country_currency = get_by_country(trip.country.code)[0]
    topln = round(Decimal(currency_exchange.exchange(country_currency, 'PLN', 1)[0][:-4]), 3)
    frompln = round(Decimal(currency_exchange.exchange('PLN', country_currency, 1)[0][:-4]), 3)
    forecast, forecast_helper = [], {}

# Weather
    config_dict = get_default_config()
    config_dict['language'] = 'pl'
    today = datetime.datetime.now()
    owm = OWM('61628e9b974ab0c76ffb1ce46c10b2d1', config_dict)
    mgr = owm.weather_manager()
    gn = geocoders.GeoNames(username='fuxus')
    one_call = mgr.one_call(lat=gn.geocode(trip.city)[1][0], lon=gn.geocode(trip.city)[1][1])
    for i in range(7):
        forecast_helper.update({'date': today})
        forecast_helper.update({'max_temp': (one_call.forecast_daily[i].temperature('celsius')['max'])})
        forecast_helper.update({'min_temp': (one_call.forecast_daily[i].temperature('celsius')['min'])})
        forecast_helper.update({'weather': (one_call.forecast_daily[i].detailed_status)})
        forecast.append(forecast_helper.copy())
        today = today + datetime.timedelta(days=1)

# Spending
    if request.method == 'POST':
        form = SpendingForm(request.POST)
        if country_currency == 'PLN':
            form.fields['currency_code'].choices = [(country_currency, country_currency)]
        else:
            form.fields['currency_code'].choices = [(country_currency, country_currency), ('PLN', 'PLN')]
        form.fields['currency_code'].initial = country_currency
        if form.is_valid():
            form.process()
            bbb = form.save(commit=False)
            bbb.trip_id = trip_id
            bbb.save()
            messages.success(request, _('You added a new spending!'))
            return redirect('tripus:singleTrip', trip_id)
    else:
        form = SpendingForm(initial={'currency_code':country_currency})
        if country_currency == 'PLN':
            form.fields['currency_code'].choices = [(country_currency, country_currency)]
        else:
            form.fields['currency_code'].choices = [(country_currency, country_currency), ('PLN', 'PLN')]

# Note
    if note_exists == 0:
        if request.method == 'POST':
            form_note = NoteForm(request.POST)
            if form_note.is_valid():
                form_note.process()
                bbb = form_note.save(commit=False)
                bbb.trip_id = trip_id
                bbb.save()
                messages.success(request, _('You added a note!'))
            return redirect('tripus:singleTrip', trip_id)
        else:
            form_note = NoteForm()
    else:
        form_note = Note.objects.get(trip_id=trip_id)

    return render(request, 'trip/singletrip.html', {'my_trip': trip, 'spending_record': spending_record, 'places_list': places_list,
                                                    'form_spending': form,'trip_id': trip.id, 'topln': topln, 'frompln': frompln,
                                                    'country_currency': country_currency, 'form_notes': form_note,
                                                    'note_exists': note_exists, 'forecast': forecast, 'ticket': ticket})


# Add trip.
@login_required(login_url='/tripus/login')
def addtrip(request):
    if request.method == 'POST':
        form = AddTripForm(request.POST)
        if form.is_valid():
            form.process()
            bbb = form.save(commit=False)
            bbb.user_id = request.user.id
            bbb.save()
            messages.success(request, _('You added a new trip!'))
            return redirect('tripus:singleTrip', trip_id=bbb.id)
    else:
        form = AddTripForm()
    return render(request, 'trip/addtrip.html', {'form': form})


# Edit trip.
@user_is_trip_author
def edittrip(request, trip_id):
    instance = get_object_or_404(Trip, id=trip_id)
    if request.method == 'POST':
        form = AddTripForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, _('Trip was updated successfully!'))
            return redirect('tripus:singleTrip', trip_id=trip_id)
    else:
        form = AddTripForm(instance=instance)
    return render(request, 'trip/edittrip.html', {'form': form, 'trip_id': trip_id})


# Delete trip.
@user_is_trip_author
def deletetrip(request, trip_id):
    instance = get_object_or_404(Trip, id=trip_id)
    if request.method == "POST":
        form = TripDeleteForm(request.POST, instance=instance)
        if form.is_valid():
            instance.delete()
            messages.success(request, _('Trip was deleted successfully!'))
            return redirect('tripus:mytrips')
    else:
        form = TripDeleteForm(instance=instance)

    return render(request, 'trip/deletetrip.html', {'form': form, 'trip': instance, 'trip_id': trip_id })

# <----------Spending section---------->


# Spending page.
@user_is_trip_author
def spending(request, trip_id):
    trip = Trip.objects.get(id=trip_id)
    country_currency = get_by_country(trip.country.code)[0]
    spending_record = Spending.objects.filter(trip_id=trip_id).order_by('-id')
    total, total_ex = 0, 0

    if request.method == 'POST':
        form = SpendingForm(request.POST)
        if country_currency == 'PLN':
            form.fields['currency_code'].choices = [(country_currency, country_currency)]
        else:
            form.fields['currency_code'].choices = [(country_currency, country_currency), ('PLN', 'PLN')]
        form.fields['currency_code'].initial = country_currency
        if form.is_valid():
            form.process()
            bbb = form.save(commit=False)
            bbb.trip_id = trip_id
            bbb.save()
            messages.success(request, _('You added a new spending!'))
            return redirect('tripus:spending', trip_id)
    else:
        form = SpendingForm()
        if country_currency == 'PLN':
            form.fields['currency_code'].choices = [(country_currency, country_currency)]
        else:
            form.fields['currency_code'].choices = [(country_currency, country_currency), ('PLN', 'PLN')]
        form.fields['currency_code'].initial = country_currency

    for i in spending_record:
        if i.currency_code == 'PLN':
            total = total + i.price
        else:
            total_ex = total_ex + i.price

    if total_ex == 0:
        sum_pln = total
    else:
        sum_pln = total + round(Decimal(currency_exchange.exchange(country_currency, 'PLN', total_ex)[0][:-4].replace(',', '')), 2)

    if total == 0:
        sum_exch = total_ex
    else:
        sum_exch = total_ex + round(Decimal(currency_exchange.exchange('PLN', country_currency, total)[0][:-4].replace(',', '')), 2)

    return render(request, 'spending/viewspending.html', {'spending_record': spending_record, 'form_spending': form, 'trip_id': trip_id,
                                                  'trip': trip, 'sum_pln': sum_pln, 'sum_exch': sum_exch, 'country_currency': country_currency,
                                                  'spending_site': 1})


# Edit spending.
@user_is_trip_author
def spendingedit(request, trip_id, spending_id):
    instance = get_object_or_404(Spending, id=spending_id)
    trip = Trip.objects.get(id=trip_id)
    country_currency = get_by_country(trip.country.code)[0]

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

    return render(request, 'spending/editspending.html', {'form': form, 'spending': instance, 'trip_id': trip_id})


# Delete spending.
@user_is_trip_author
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

    return render(request, 'spending/deletespending.html', {'form': form, 'spending': instance, 'trip_id': trip_id})


# <----------Ticket&reservation section---------->


# Display tickets
@user_is_trip_author
def ticketlist(request, trip_id):
    tickets = Ticket.objects.filter(trip_id=trip_id)
    return render(request, 'ticket/ticketlist.html', {'trip_id': trip_id, 'ticket': tickets})


# Add ticket
@user_is_trip_author
def ticketadd(request, trip_id):
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            form.process()
            bbb = form.save(commit=False)
            bbb.trip_id = trip_id
            bbb.save()
            messages.success(request, _('You added a new ticket!'))
            return redirect('tripus:singleTrip', trip_id=trip_id)
    else:
        form = TicketForm()
    return render(request, 'ticket/addticket.html', {'form': form, 'trip_id': trip_id})


# Edit ticket
@user_is_trip_author
def ticketedit(request, trip_id, ticket_id):
    instance = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, _('Ticket was updated successfully!'))
            return redirect('tripus:singleTrip', trip_id=trip_id)
    else:
        form = TicketForm(instance=instance)

    return render(request, 'ticket/editticket.html', {'form': form, 'ticket': instance, 'trip_id': trip_id})


# Delete ticket.
@user_is_trip_author
def ticketdelete(request, trip_id, ticket_id):
    instance = get_object_or_404(Ticket, id=ticket_id)
    if request.method == "POST":
        form = TicketDeleteForm(request.POST, instance=instance)
        if form.is_valid():
            instance.delete()
            messages.success(request, _('Ticket was deleted successfully!'))
            return redirect('tripus:ticketList', trip_id=trip_id)
    else:
        form = TicketDeleteForm(instance=instance)

    return render(request, 'ticket/deleteticket.html', {'form': form, 'ticket': instance, 'trip_id': trip_id})


# View single ticket.
@user_is_trip_author
def ticketview(request, trip_id, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    return render(request, 'ticket/viewticket.html', {'ticket': ticket, 'trip_id': trip_id})


# <----------Place section---------->


# Display places to visit
@user_is_trip_author
def visitplace(request, trip_id):
    places_list = Visit.objects.filter(trip_id=trip_id).order_by(F('visit_date').asc(nulls_last=True))
    return render(request, 'place/visitlist.html', {'trip_id': trip_id, 'places_list': places_list})


# Add place to visit
@user_is_trip_author
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
    return render(request, 'place/addplace.html', {'form': form, 'trip_id': trip_id})


# Edit place to visit.
@user_is_trip_author
def visitplaceedit(request, trip_id, visit_id):
    instance = get_object_or_404(Visit, id=visit_id)
    if request.method == 'POST':
        form = VisitForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, _('Place was updated successfully!'))
            return redirect('tripus:visitPlaceView', trip_id=trip_id, visit_id=visit_id)
    else:
        form = VisitForm(instance=instance)

    return render(request, 'place/editplace.html', {'form': form, 'place': instance, 'trip_id': trip_id})


# Delete place.
@user_is_trip_author
def visitplacedelete(request, trip_id, visit_id):
    instance = get_object_or_404(Visit, id=visit_id)
    if request.method == "POST":
        form = VisitDeleteForm(request.POST, instance=instance)
        if form.is_valid():
            instance.delete()
            messages.success(request, _('Place was deleted successfully!'))
            return redirect('tripus:visitPlaceList', trip_id=trip_id)
    else:
        form = VisitDeleteForm(instance=instance)

    return render(request, 'place/deleteplace.html', {'form': form, 'place': instance, 'trip_id': trip_id})


# View single place to visit.
@user_is_trip_author
def visitplaceview(request, trip_id, visit_id):
    place = Visit.objects.get(id=visit_id)
    return render(request, 'place/viewplace.html', {'place': place, 'trip_id': trip_id})

# <----------Note section---------->


# Edit note.
@user_is_trip_author
def noteedit(request, trip_id, note_id):
    instance = get_object_or_404(Note, id=note_id)
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, _('Note was updated successfully!'))
            return redirect('tripus:singleTrip', trip_id=trip_id)
    else:
        form = NoteForm(instance=instance)

    return render(request, 'note/editnote.html', {'form': form, 'note': instance, 'trip_id': trip_id})


# Delete note.
@user_is_trip_author
def notedelete(request, trip_id, note_id):
    instance = get_object_or_404(Note, id=note_id)
    if request.method == "POST":
        form = NoteDeleteForm(request.POST, instance=instance)
        if form.is_valid():
            instance.delete()
            messages.success(request, _('Note was deleted successfully!'))
            return redirect('tripus:singleTrip', trip_id=trip_id)
    else:
        form = NoteDeleteForm(instance=instance)

    return render(request, 'note/deletenote.html', {'form': form, 'note': instance, 'trip_id': trip_id})


# <----------Errors custom views---------->


# Error 400.
def error_400(request, exception):
    return render(request, 'error/400.html')


# Error 403.
def error_403(request, exception):
    return render(request, 'error/403.html')


# Error 404.
def error_404(request, exception):
    return render(request, 'error/404.html')


# Error 500.
def error_500(request):
    return render(request, 'error/500.html')
