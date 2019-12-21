from django.db import models
from django.utils import timezone

# Create your models here.

# names for reference
bill = "Bill"
daniel = "Daniel"
darcy = "Darcy"
leo = "Leo"
breakfast = "8:30"

def get_score():
    schedules = Schedule.objects.filter(cancelled=False, time__lt=timezone.now())
    scores = {bill: 0.0, daniel: 0.0, darcy: 0.0, leo: 0.0}
    for schedule in schedules:
        eaters = 0
        if schedule.e_bill:
            scores[bill] -= 1
            eaters += 1
        if schedule.e_daniel:
            scores[daniel] -= 1
            eaters += 1
        if schedule.e_darcy:
            scores[darcy] -= 1
            eaters += 1
        if schedule.e_leo:
            scores[leo] -= 1
            eaters += 1
        cooks = 0
        if schedule.c_bill:
            cooks += 1
        if schedule.c_daniel:
            cooks += 1
        if schedule.c_darcy:
            cooks += 1
        if schedule.c_leo:
            cooks += 1
        gain = eaters / cooks
        if schedule.c_bill:
            scores[bill] += gain
        if schedule.c_daniel:
            scores[daniel] += gain
        if schedule.c_darcy:
            scores[darcy] += gain
        if schedule.c_leo:
            scores[leo] += gain
    return scores

def add(date, cooks, eaters, cancelled=True):
    pass


class Schedule(models.Model):

    # 3 times in one day, 8:30, 12:30 and 6:30, denoting the
    # time when a planned schedule should become history
    time = models.DateTimeField(primary_key=True)

    c_bill = models.BinaryField(default=False)
    c_daniel = models.BinaryField(default=False)
    c_darcy = models.BinaryField(default=False)
    c_leo = models.BinaryField(default=False)
    e_bill = models.BinaryField(default=False)
    e_daniel = models.BinaryField(default=False)
    e_darcy = models.BinaryField(default=False)
    e_leo = models.BinaryField(default=False)

    update_time = models.DateTimeField()

    cancelled = models.BinaryField(default=False)

    def __str__(self):
        ans = str(self.time) + " Cooking: "
        if self.c_bill:
            ans += "Bill, "
        if self.c_daniel:
            ans += "Daniel, "
        if self.c_darcy:
            ans += "Darcy, "
        if self.c_leo:
            ans += "Leo, "
        ans += "Eating: "
        if self.e_bill:
            ans += "Bill, "
        if self.e_daniel:
            ans += "Daniel, "
        if self.e_darcy:
            ans += "Darcy, "
        if self.e_leo:
            ans += "Leo, "
        ans += "Updated on: " + str(self.update_time)
        if self.cancelled:
            ans += "Cancelled"
        return ans

class Cook(models.Model):

    time = models.ForeignKey(Schedule, on_delete=models.CASCADE())
    name = models.CharField(max_length=20)
