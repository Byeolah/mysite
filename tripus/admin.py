from django.contrib import admin
from .models import Trip
from .models import Spending
from .models import Visit
from .models import Note
# Register your models here.

admin.site.register(Trip)
admin.site.register(Spending)
admin.site.register(Visit)
admin.site.register(Note)
