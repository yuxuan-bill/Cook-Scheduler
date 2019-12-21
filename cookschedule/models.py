from django.db import models
from datetime import timedelta
from datetime import date, datetime
from typing import List, Dict


# Create your models here.

breakfast = timedelta(hours=8, minutes=30)
lunch = timedelta(hours=12, minutes=30)
dinner = timedelta(hours=18, minutes=30)


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


# add to schedule if the date + meal combination is new, otherwise
# modify existing entry. Return True on success, False on failure.
def add(day: date, meal: timedelta,
        cooks: List[str], eaters: List[str], note, cancelled=False):
    if meal not in [breakfast, lunch, dinner]:
        return False
    time = day + meal
    try:
        schedule = Schedule.objects.get(time=time)
    except Schedule.DoesNotExist:
        schedule = Schedule(time=time, cancelled=cancelled, note=note)
        schedule.save()
        schedule.set_cooks(cooks)
        schedule.set_eaters(eaters)
        return True
    else:
        schedule.time = time
        schedule.note = note
        schedule.cancelled = cancelled
        schedule.set_cooks(cooks)
        schedule.set_eaters(eaters)
        return True


# cancel the schedule specified by date and meal, return False if
# meal is not one of breakfast/lunch/dinner or the entry does not
# exist, otherwise True
def delete(day: date, meal: timedelta):
    if meal not in [breakfast, lunch, dinner]:
        return False
    time = day + meal
    try:
        schedule = Schedule.objects.get(time=time)
    except Schedule.DoesNotExist:
        return False
    else:
        schedule.cancelled = True
        schedule.save()
        return True


# get history schedules in descending order of time
def history() -> List['Schedule']:
    return Schedule.objects\
        .filter(time__lt=datetime.now(), cancelled=False).order_by('-time')


# get upcoming schedules, in ascending order of time
def plan() -> List['Schedule']:
    return Schedule.objects\
        .filter(time__gte=datetime.now(), cancelled=False).order_by('time')


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
    cancelled = models.BooleanField(default=False)
    note = models.CharField(max_length=1024)

    def __str__(self):
        return str(self.getinfo())

    def cooks(self) -> List[str]:
        names = []
        for cook in self.cook_set.all():
            names.append(cook.name)
        return names

    def set_cooks(self, cooks: List[str]):
        self.cook_set.all().delete()
        for cook in cooks:
            self.cook_set.create(time=self.time, name=cook).save()
        self.update_time = datetime.now()
        self.save()

    def eaters(self) -> List[str]:
        names = []
        for eater in self.eat_set.all():
            names.append(eater.name)
        return names

    def set_eaters(self, eaters: List[str]):
        self.eat_set.all().delete()
        for eater in eaters:
            self.eat_set.create(time=self.time, name=eater).save()
        self.update_time = datetime.now()
        self.save()

    def getinfo(self):
        return {'time': self.time,
                'update_time': self.update_time,
                'cancelled': self.cancelled,
                'cooks': self.cooks(),
                'eaters': self.eaters(),
                'note': self.note}


class Cook(models.Model):

    time = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    name = models.CharField(choices=Schedule.participants, max_length=16)


class Eat(models.Model):

    time = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    name = models.CharField(choices=Schedule.participants, max_length=16)
