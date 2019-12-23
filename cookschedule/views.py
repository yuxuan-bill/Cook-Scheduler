from django.shortcuts import render
from .models import *


# Create your views here.


def index(request):
    context = {'scores': score(),
               'plan': process_schedules(plan()),
               'history': process_schedules(history()),
               'today': str(datetime.today().date())
               }
    if request.POST:
        print(request.POST)
    return render(request, 'cookschedule/index.html', context)


def process_schedules(schedules: List['Schedule']):
    result = []
    for schedule in schedules:
        meal_time = schedule.time.time()
        meal_delta = timedelta(hours=meal_time.hour, minutes=meal_time.minute)
        result.append({'cooks': ", ".join(schedule.cooks()),
                       'eaters': ", ".join(schedule.eaters()),
                       'notes': schedule.note,
                       'date': str(schedule.time.date()),
                       'meal': meal_dict[meal_delta],
                       'update_time': str(schedule.update_time)
                       })
    return result
