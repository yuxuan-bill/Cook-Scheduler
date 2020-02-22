from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth \
    import authenticate, login as auth_login, logout as auth_logout
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages

from .models import *


# Create your views here.


@login_required(login_url=reverse_lazy('cookschedule:login'))
def index(request):

    if 'delete' in request.POST:
        return handle_delete(request)

    if 'update' in request.POST:
        return handle_update(request)

    if 'undo' in request.POST:
        return handle_undo(request)

    scores = score()
    for people in scores:
        scores[people] = round(scores[people], 1)
    context = {'scores': scores,
               'plan': process_schedules(plan()),
               'history': process_schedules(history()),
               'today': str(datetime.today().date()),
               'user': request.user.username
               }

    # when 'edit' button is pressed
    if request.GET:
        context['info'] = {'cooks': request.GET['cooks'].split(", "),
                           'eaters': request.GET['eaters'].split(", "),
                           'notes': request.GET['notes'],
                           'meal': request.GET['meal'],
                           'date': request.GET['date']
                           }

    return render(request, 'cookschedule/index.html', context)


def handle_delete(request):
    time = datetime.strptime(request.POST['delete'], '%Y-%m-%d %H:%M:%S')
    day, meal = get_day_meal(time)
    delete(day=day, meal=meal, user=request.user.username)
    messages.add_message(request, messages.WARNING, "Deleted Schedule.")
    return HttpResponseRedirect(reverse('cookschedule:index'))


def handle_update(request):
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
               user=request.user.username,
               cooks=request.POST.getlist('cooks'),
               eaters=request.POST.getlist('eaters'),
               notes=request.POST['notes']
               )
        level = messages.SUCCESS
        message = "Update successful."
    messages.add_message(request, level, message)
    return redirect('cookschedule:index')


def handle_undo(request):
    success = undo(request.user.username)
    if success:
        messages.success(request, "Undid last action.", extra_tags="undo")
    else:
        messages.error(request, "There is nothing to undo", extra_tags="undo")
    return redirect('cookschedule:index')


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


def login(request):
    if request.user.is_authenticated:
        return index(request)
    if request.POST:
        user = authenticate(request, username=request.POST['username'],
                            password=request.POST['password'])
        if user is not None:
            auth_login(request, user)
            return HttpResponseRedirect(request.POST['next'])
        else:
            url = request.POST['next']
            error = "Invalid username or password"
            return render(request, 'cookschedule/login.html',
                          {'next': url, "error": error})

    url = request.GET['next'] if 'next' in request.GET \
        else reverse('cookschedule:index')
    return render(request, 'cookschedule/login.html', {'next': url})


def logout(request):
    auth_logout(request)
    return redirect('cookschedule:login')


@login_required(login_url=reverse_lazy('cookschedule:login'))
def change_password(request):

    # submit a change_password request
    if request.POST:
        user = authenticate(username=request.user.username,
                            password=request.POST['original'])
        if user is None:
            level = messages.ERROR
            message = "Your original password is incorrect."
        elif request.POST['new'] != request.POST['confirm']:
            level = messages.ERROR
            message = "The two new passwords you entered does not match."
        elif len(request.POST['new']) == 0:
            level = messages.ERROR
            message = "Your new password cannot be empty."
        elif request.POST['new'] == request.POST['original']:
            level = messages.ERROR
            message = "Your new password cannot be the same " \
                      "as the original one."
        else:
            request.user.set_password(request.POST['new'])
            request.user.save()
            level = messages.SUCCESS
            message = "Successfully changed password."

        messages.add_message(request, level, message)
        if level == messages.ERROR:
            return redirect('cookschedule:change_password')
        return redirect('cookschedule:index')

    # visiting the change password page
    return render(request, 'cookschedule/change_password.html',
                  {'user': request.user.username})


@login_required(login_url=reverse_lazy('cookschedule:login'))
def user_stat(request):

    joke = get_joke()
    context = {'user': request.user,
               'setup': joke['setup'], 'punchline': joke['punchline']}

    # time of the first update in changelog
    if ChangeLog.objects.count() == 0:
        first_update = datetime.now()
    else:
        first_update = ChangeLog.objects.all()[0].update_time

    # time of request.user's last update
    user_updates = ChangeLog.objects.filter(user=request.user.username)
    if user_updates.count() == 0:
        user_last_update = datetime.now()
    else:
        user_last_update = user_updates.order_by('-update_time')[0].update_time

    # the time elapse since last update by request.user
    update_timedelta = datetime.now() - user_last_update
    update_time = str(update_timedelta.seconds // 3600) + " hours"
    if update_timedelta.days > 0:
        update_time = str(update_timedelta.days) + " days and " + update_time
    context['last_update'] = update_time

    # number of days since first update ever
    context['num_days'] = (datetime.now() - first_update).days

    # get the partner that cooks with request.user most frequently, and the
    # number of meals this user cooked. If the user is an admin account,
    # information would not display correctly, since admin never participated
    # in any cooking activities.
    partner_count = dict()
    num_meal = 0
    for schedule in history():
        cooks = schedule.cooks()
        if request.user in cooks:
            num_meal += 1
            for cook in cooks:
                if cook != request.user:
                    partner_count[cook] = partner_count.get(cook, 0) + 1
    if len(partner_count) == 0:
        partner = "yourself"
    else:
        partner, _ = max(partner_count.items(), key=lambda kv: kv[1])
    context['partner'] = partner
    context['num_meal'] = num_meal

    return render(request, 'cookschedule/user_stat.html', context)
