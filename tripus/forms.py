from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
import datetime

from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .models import *
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


category_choices = [
    (_('restaurant'), _('restaurant')),
    (_('monument'), _('monument')),
    (_('attraction'), _('attraction')),
    (_('outside'), _('outside')),
    (_('shop'), _('shop')),
    (_('other'), _('other'))
]

target_choices = [
    (_('tourism'), _('tourism')),
    (_('business'), _('business')),
    (_('sports'), _('sports')),
    (_('health'), _('health'))
]


# Add trip form.
class AddTripForm(forms.ModelForm):
    country = CountryField().formfield(label=_('country'))
    target = forms.ChoiceField(choices=target_choices, label=_('Target'))
    class Meta:
        model = Trip
        fields = ('name', 'country', 'city', 'departure_date', 'comeback_date', 'target')
        labels = {
            'name': _('name'),
            'country': _('country'),
            'city': _('city'),
            'departure_date': _('Departure date'),
            'comeback_date': _('Comeback date'),
            'target': _('Target')
        }
        widgets = {
            'departure_date': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'}),
            'comeback_date': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'})
        }

    def process(self):
        process = self.cleaned_data
        return process

    def clean(self):
        cleaned_data = super().clean()
        departure_date = cleaned_data.get("departure_date")
        comeback_date = cleaned_data.get("comeback_date")
        if comeback_date < departure_date:
            raise forms.ValidationError("Comeback date should be greater than departure date.")


# Delete trip form.
class TripDeleteForm(ModelForm):
    class Meta:
        model = Trip
        fields = []


# Sign up form.
class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label=_('first name'), max_length=30, required=False)
    last_name = forms.CharField(label=_('last name'), max_length=30, required=False)
    email = forms.EmailField(label=_('email address'), max_length=254)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            user = User.objects.get(email=email)
            raise forms.ValidationError("This email address already exists. Did you forget your password?")
        except User.DoesNotExist:
            return email


# Delete user.
class UserDeleteForm(ModelForm):
    class Meta:
        model = User
        fields = []


# Spending form.
class SpendingForm(forms.ModelForm):
    date = forms.DateField(initial=datetime.date.today, label=_('spending date'))
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

    def process(self):
        process = self.cleaned_data
        return process


# Delete spending form.
class SpendingDeleteForm(ModelForm):
    class Meta:
        model = Spending
        fields = []


# Ticket form.
class TicketForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ('name', 'date', 'address', 'reservation_number', 'notes', 'file')
        labels = {
            'name': _('name'),
            'date': _('date'),
            'address': _('addess'),
            'reservation_number':_('reservation_number'),
            'notes': _('notes'),
            'file': _('file')
        }
        widgets = {
            'date': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'})
        }

    def process(self):
        process = self.cleaned_data
        return process

    def validate_file_extension(value):
        import os
        ext = os.path.splitext(value.name)[1]
        valid_extensions = ['.pdf', '.jpg', '.png']
        if not ext in valid_extensions:
            raise ValidationError(_('File not supported!'))


# Delete ticket form.
class TicketDeleteForm(ModelForm):
    class Meta:
        model = Ticket
        fields = []


# Visit places form.
class VisitForm(forms.ModelForm):
    category = forms.ChoiceField(choices=category_choices, label=_('category'))
    class Meta:
        model = Visit
        fields = ('name', 'category', 'visit_date', 'website', 'address', 'approach', 'notes', 'visited')
        labels = {
            'name': _('name'),
            'category': _('category'),
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


# Note form.
class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['text']
        labels = {
            'text': _('text'),
        }

    def process(self):
        process = self.cleaned_data
        return process


# Delete visit form.
class NoteDeleteForm(ModelForm):
    class Meta:
        model = Note
        fields = []