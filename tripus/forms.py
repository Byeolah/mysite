from django.urls import reverse
from pprint import pprint
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
import datetime
from django_countries.fields import CountryField
from django.forms import ModelForm
from .models import *
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


# Add trip form.
class AddTripForm(forms.ModelForm):
    name = forms.CharField(label=_('trip name'), min_length=4, max_length=100)
    country = CountryField().formfield()
    city = forms.CharField(label=_('city'), max_length=50, required=False)
    departure_date = forms.DateField(label=_('departure date'), widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    comeback_date = forms.DateField(label=_('comeback date'), widget=forms.widgets.DateInput(attrs={'type': 'date'}))#todo walidacja daty, powrotna nie może być wczesniejsza
    target = forms.CharField(label=_('trip target'))

    class Meta:
        model = Trip
        fields = ['name', 'country', 'city', 'departure_date', 'comeback_date', 'target']


# Sign up form.
class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label=_('first name'), max_length=30, required=False)
    last_name = forms.CharField(label=_('last name'), max_length=30, required=False)
    email = forms.EmailField(label=_('email address'), max_length=254)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )


# Spending form.
class SpendingForm(forms.ModelForm):
    date = forms.DateField(initial=datetime.date.today)
    currency_code = forms.ChoiceField(label=_('currency'))

    class Meta:
        model = Spending
        fields = ('name', 'price', 'currency_code', 'date')
        labels = {
            'name': _('spending name'),
            'price': _('price'),
            'currency_code': _('currency'),
            'date': _('spending date'),
        }
        widgets = {
            'date': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'})
        }


# Delete spending form.
class SpendingDeleteForm(ModelForm):
    class Meta:
        model = Spending
        fields = []


# Visit places form.
class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ('name', 'visit_date', 'website', 'address', 'approach', 'notes', 'visited')
        labels = {
            'name': _('name'),
            'visit_date': _('visit_date'),
            'website': _('website'),
            'address': _('addess'),
            'approach':_('approach'),
            'notes': _('notes'),
            'visited': _('visited')
        }
        widgets = {
            'visit_date': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super(VisitForm, self).__init__(*args, **kwargs)
        self.fields['visit_date'].required = False

    def process(self):
        process = self.cleaned_data
        return process


# Delete visit form.
class VisitDeleteForm(ModelForm):
    class Meta:
        model = Visit
        fields = []


# Edit profile form.
class EditProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
        )