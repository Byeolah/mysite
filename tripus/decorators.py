from django.core.exceptions import PermissionDenied
from .models import Trip

def user_is_trip_author(function):
    def wrap(request, *args, **kwargs):
        trip = Trip.objects.get(pk=kwargs['trip_id'])
        if trip.user_id == request.user.id:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
