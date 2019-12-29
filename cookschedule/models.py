from django.db import models
from datetime import timedelta
from datetime import date, datetime
from typing import List, Dict


# Create your models here.

breakfast = timedelta(hours=8, minutes=30)
lunch = timedelta(hours=12, minutes=30)
dinner = timedelta(hours=18, minutes=30)
meal_dict = {breakfast: "Breakfast", lunch: "Lunch", dinner: "Dinner",
             "Breakfast": breakfast, "Lunch": lunch, "Dinner": dinner}
undo_time_limit = timedelta(minutes=1)


# get score for every participant, counting only history meal
# for every meal, people who eat get -1, and people who cook
# get eaters / cookers score.
def score() -> Dict[str, float]:
    schedules = history()
    scores = {}
    for participant, _ in Schedule.participants:
        scores[participant] = 0.0
    for schedule in schedules:
        eaters = schedule.eaters()
        cooks = schedule.cooks()
        for eater in eaters:
            scores[eater] -= 1
        for cook in cooks:
            scores[cook] += len(eaters) / len(cooks)
    return scores


# add to schedule if the get_time(date, meal) combination is new,
# otherwise modify existing entry. Return true if this is an update, false
# if new entry was added.
def update(day: date, meal: timedelta, user: str,
           cooks: List[str], eaters: List[str], notes=""):
    time = get_time(day, meal)
    is_update = True
    try:
        schedule = Schedule.objects.get(time=time)
    except Schedule.DoesNotExist:
        action = ChangeLog.add
        note_previous = notes
        cooks_previous = cooks
        eaters_previous = eaters
        schedule = Schedule(time=time, note=notes)
        is_update = False
    else:
        action = ChangeLog.update
        note_previous = schedule.note
        cooks_previous = schedule.cooks()
        eaters_previous = schedule.eaters()
        schedule.time = time
        schedule.note = notes
    schedule.save()
    schedule.set_cooks(cooks)
    schedule.set_eaters(eaters)
    add_changelog(day=day, meal=meal, action=action, user=user,
                  note_previous=note_previous, cooks_previous=cooks_previous,
                  eaters_previous=eaters_previous)
    return is_update


# delete the schedule specified by date and meal from database,
# return False if the entry does not exist, otherwise True
def delete(day: date, meal: timedelta, user: str):
    time = get_time(day, meal)
    try:
        schedule = Schedule.objects.get(time=time)
    except Schedule.DoesNotExist:
        return False
    else:
        info = schedule.getinfo()
        add_changelog(day=day, meal=meal,
                      action=ChangeLog.delete, user=user,
                      note_previous=info['note'], cooks_previous=info['cooks'],
                      eaters_previous=info['eaters'])
        schedule.delete()
        return True


def add_changelog(day: date, meal: timedelta, action: str, user: str,
                  note_previous: str,
                  cooks_previous: List[str], eaters_previous: List[str]):
    changelog = ChangeLog(time=get_time(day, meal), action=action, user=user,
                          note_previous=note_previous)
    changelog.save()
    changelog.set_previous_cooks(cooks_previous)
    changelog.set_previous_eaters(eaters_previous)


# undo the last recent action done by the user with specified username,
# return false if there is no such recent action, true otherwise. Upon
# success, this also adds to changelog, since undo is also part of a change.
def undo(username):
    change_logs = ChangeLog.objects.filter(
        update_time__gt=datetime.now() - undo_time_limit, user=username)\
        .order_by('update_time')
    if len(change_logs) == 0:
        return False
    else:
        change_log = change_logs[0]
        day, meal = get_day_meal(change_log.time)
        if change_log.action == ChangeLog.add:
            delete(day, meal, username)
        else:  # action is delete or update
            update(day=day, meal=meal, user=username,
                   cooks=change_log.previous_cooks(),
                   eaters=change_log.previous_eaters())
        return True


# 删库跑路
def delete_all():
    Schedule.objects.all().delete()
    ChangeLog.objects.all().delete()


# get history schedules in descending order of time
def history() -> List['Schedule']:
    return Schedule.objects.filter(time__lt=datetime.now()).order_by('-time')


# get upcoming schedules, in ascending order of time
def plan() -> List['Schedule']:
    return Schedule.objects.filter(time__gte=datetime.now()).order_by('time')


# utility for combining date and meal to create datetime for a meal
def get_time(day: date, meal: timedelta) -> datetime:
    if meal not in [breakfast, lunch, dinner]:
        raise Exception(str(meal) + " is not one of breakfast/lunch/dinner.")
    return datetime(year=day.year, month=day.month, day=day.day) + meal


def get_day_meal(time: datetime) -> (date, timedelta):
    meal = time.time()
    meal_delta = timedelta(hours=meal.hour, minutes=meal.minute)
    return time.date(), meal_delta


class Schedule(models.Model):

    bill = "Bill"
    daniel = "Daniel"
    darcy = "Darcy"
    leo = "Leo"
    participants = [(bill, "Bill"), (daniel, "Daniel"),
                    (darcy, "Darcy"), (leo, "Leo")]

    # have time value 8:30, 12:30 or 18:30, denoting the time when a
    # planned schedule should become history. Can be formed using
    # datetime(year, month, day) + breakfast/lunch/dinner
    time = models.DateTimeField(primary_key=True)
    update_time = models.DateTimeField(auto_now=True)
    note = models.CharField(max_length=1024)

    def __str__(self):
        return str(self.getinfo())

    def cooks(self) -> List[str]:
        return [cook.name for cook in self.cook_set.all()]

    def set_cooks(self, cooks: List[str]):
        self.cook_set.all().delete()
        for cook in cooks:
            self.cook_set.create(time=self.time, name=cook).save()
        self.update_time = datetime.now()
        self.save()

    def eaters(self) -> List[str]:
        return [eater.name for eater in self.eater_set.all()]

    def set_eaters(self, eaters: List[str]):
        self.eater_set.all().delete()
        for eater in eaters:
            self.eater_set.create(time=self.time, name=eater).save()
        self.update_time = datetime.now()
        self.save()

    def getinfo(self):
        return {'time': self.time,
                'update_time': self.update_time,
                'cooks': self.cooks(),
                'eaters': self.eaters(),
                'note': self.note}


class Cook(models.Model):
    time = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    name = models.CharField(choices=Schedule.participants, max_length=30)


class Eater(models.Model):
    time = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    name = models.CharField(choices=Schedule.participants, max_length=30)


# ChangeLog represents each change made to the cooking schedule. We store
# all change histories so that no data gets lost. The layout of this table is
# similar to that of Schedule table, except that primary key is auto picked,
# and there are two additional fields user and action.
#
# ChangeLog is a monotonically increasing table, and no previous entries should
# be modified, since they serve as a record.
class ChangeLog(models.Model):

    delete = "delete"
    update = "update"
    add = "add"
    actions = [(delete, "delete"), (update, "update"), (add, "add")]

    time = models.DateTimeField()
    update_time = models.DateTimeField(auto_now=True)
    action = models.CharField(choices=actions, max_length=6)
    user = models.CharField(choices=Schedule.participants, max_length=150)
    note_previous = models.CharField(max_length=1024)

    def __str__(self):
        return str(self.getinfo())

    def previous_cooks(self):
        return [cook.name for cook in self.previouscook_set.all()]

    def previous_eaters(self):
        return [eater.name for eater in self.previouseater_set.all()]

    def set_previous_cooks(self, cooks):
        self.previouscook_set.all().delete()
        for cook in cooks:
            self.previouscook_set.create(key=self.pk, name=cook).save()
        self.update_time = datetime.now()
        self.save()

    def set_previous_eaters(self, eaters):
        self.previouseater_set.all().delete()
        for eater in eaters:
            self.previouseater_set.create(key=self.pk, name=eater).save()
        self.update_time = datetime.now()
        self.save()

    def getinfo(self):
        return {'pk': self.pk,
                'update_time': self.update_time,
                'action': self.action,
                'user': self.user,
                'note_previous': self.note_previous,
                'cooks_previous': self.previous_cooks(),
                'eaters_previous': self.previous_eaters()}


class PreviousCook(models.Model):
    key = models.ForeignKey(ChangeLog, on_delete=models.CASCADE)
    name = models.CharField(choices=Schedule.participants, max_length=16)


class PreviousEater(models.Model):
    key = models.ForeignKey(ChangeLog, on_delete=models.CASCADE)
    name = models.CharField(choices=Schedule.participants, max_length=16)
