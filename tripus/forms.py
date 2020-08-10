from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Trip
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class AddTripForm(forms.Form): #TODO do zmiany na ładne klasowe
    name = forms.CharField(label=_('trip name'), min_length=4, max_length=100)
    country = forms.CharField(label=_('country'), min_length=2, max_length=50)
    city = forms.CharField(label=_('city'), max_length=50, required=False)
    departure_date = forms.DateField(label=_('departure date'), widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    comeback_date = forms.DateField(label=_('comeback date'), widget=forms.widgets.DateInput(attrs={'type': 'date'}))#todo walidacja daty, powrotna nie może być wczesniejsza
    target = forms.CharField(label=_('trip target'))


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label=_('first name'), max_length=30, required=False)
    last_name = forms.CharField(label=_('last name'), max_length=30, required=False)
    email = forms.EmailField(label=_('email address'), max_length=254)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )


class PersonForm(forms.Form):
    class Meta:
        model = Trip
        fields = ('name', 'country', 'city', 'departure_date', 'comeback_date', 'target')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save perso'))