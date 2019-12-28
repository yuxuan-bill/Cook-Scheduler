from django.contrib import admin
from .models import Schedule, Eater, Cook

# Register your models here.

admin.site.register(Schedule)
admin.site.register(Eater)
admin.site.register(Cook)
