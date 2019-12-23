from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .models import *


# Create your views here.


def index(request):

    if 'delete' in request.POST:
        time = datetime.strptime(request.POST['delete'], '%Y-%m-%d %H:%M:%S')
        meal = time.time()
        delete(time.date(), timedelta(hours=meal.hour, minutes=meal.minute))
        messages.add_message(request, messages.WARNING, str(time))
        return HttpResponseRedirect(reverse('cookschedule:index'))

    if 'date' in request.POST:
        if 'cooks' not in request.POST:
            level = messages.ERROR
            message = "You didn't set any one to cook."
        elif 'eaters' not in request.POST:
            level = messages.ERROR
            message = "You didn't set any one to eat."
        elif len(request.POST['meal']) == 0:
            level = messages.ERROR
            message = "You didn't set the meal to update for."
        else:
            update(day=datetime.strptime(
                request.POST['date'], '%Y-%m-%d').date(),
                   meal=meal_dict[request.POST['meal']],
                   cooks=request.POST.getlist('cooks'),
                   eaters=request.POST.getlist('eaters'),
                   notes=request.POST['notes']
                   )
            level = messages.SUCCESS
            message = "Update successful."
        messages.add_message(request, level, message)
        return HttpResponseRedirect(reverse('cookschedule:index'))

    scores = score()
    for people in scores:
        scores[people] = round(scores[people], 1)
    context = {'scores': scores,
               'plan': process_schedules(plan()),
               'history': process_schedules(history()),
               'today': str(datetime.today().date()),
               }
    return render(request, 'cookschedule/index.html', context)


def process_schedules(schedules: List['Schedule']):
    result = []
    for schedule in schedules:
        meal_time = schedule.time.time()
        meal_delta = timedelta(hours=meal_time.hour, minutes=meal_time.minute)
        context = {'cooks': ", ".join(schedule.cooks()),
                   'eaters': ", ".join(schedule.eaters()),
                   'notes': schedule.note,
                   'date': str(schedule.time.date()),
                   'meal': meal_dict[meal_delta],
                   'time': str(schedule.time),
                   'update_time': str(schedule.update_time)
                    }
        if schedule.note:
            context['notes'] = schedule.note
        result.append(context)
    return result
