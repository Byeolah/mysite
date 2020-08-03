from django import forms


class AddTripForm(forms.Form):
    name = forms.CharField(label='Nazwa podróży', min_length=4, max_length=100)
    country = forms.CharField(label='Kraj', min_length=2, max_length=50)
    city = forms.CharField(label='Miasto', max_length=50)
    departure_date = forms.DateField(label='Data wyjazdu')
    comeback_date = forms.DateField(label='Data powrotu')
    target = forms.CharField(label='Cel wyjazdu')