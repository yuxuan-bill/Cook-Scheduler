from django.test import TestCase
from .models import *

# Create your tests here.

leo = Schedule.leo
darcy = Schedule.darcy
bill = Schedule.bill
daniel = Schedule.daniel
participants = [x for x, _ in Schedule.participants]


class ScheduleModelTests(TestCase):

    def setUp(self):

        self.today = datetime.now().date()

        future_schedule = Schedule.objects.create(
            time=self.today + timedelta(days=1) + breakfast,
            note="future schedule"
        )
        future_schedule.set_eaters([leo, darcy, bill])
        future_schedule.set_cooks([leo, darcy])

        past_schedule1 = Schedule.objects.create(
            time=self.today + timedelta(days=-1) + lunch,
            note="lunch for yesterday"
        )
        past_schedule1.set_eaters([leo, darcy, bill])
        past_schedule1.set_cooks([leo, darcy])

        past_schedule2 = Schedule.objects.create(
            time=self.today + timedelta(days=-1) + dinner,
            note="dinner@for#yesterday!"
        )
        past_schedule2.set_cooks([bill])
        past_schedule2.set_eaters(participants)

        cancelled_schedule = Schedule.objects.create(
            time=self.today + lunch,
            update_time=datetime.now(),
            cancelled=True,
            note="cancelled schedule"
        )
        cancelled_schedule.set_eaters(participants)
        cancelled_schedule.set_cooks(participants)

    def test_schema(self):
        schedules = Schedule.objects.all()
        self.assertEquals(len(schedules), 3)
        info2 = {'time': self.today + timedelta(days=1) + breakfast,
                 'cancelled': False,
                 'cooks': [bill],
                 'eaters': [bill, daniel, darcy, leo],
                 'note': "dinner@for#yesterday!"}
        actual_info = schedules[2].getinfo()
        self.assertLessEqual(
            abs((actual_info['update_time'] - datetime.now()).total_seconds()),
            5)
        del actual_info['update_time']
        self.assertEquals(actual_info, info2)

        future_schedule = Schedule.objects.get(
            time=self.today + timedelta(days=1) + breakfast)
        self.assertEquals(future_schedule.note, "future schedule")

    def test_add_new_schedule(self):
        day = datetime(year=2000, month=1, day=1).date()
        add(day=day,
            meal=lunch,
            cooks=[darcy],
            eaters=[darcy, leo],
            note='new schedule')
        schedule = Schedule.objects.get(time=day + lunch)
        self.assertEquals(schedule.cooks(), [darcy])
        self.assertEquals(schedule.note, 'new schedule')

    def test_modify_existent_schedule(self):
        add(day=self.today,
            meal=lunch,
            cooks=[darcy, bill, leo],
            eaters=participants,
            note='restore schedule')
        schedule = Schedule.objects.get(time=self.today + lunch)
        self.assertEquals(schedule.cancelled, False)
        self.assertEquals(schedule.cooks(), [darcy, bill, leo])

    def test_delete_schedule(self):
        delete(self.today + timedelta(days=1), breakfast)
        self.assertEquals(len(plan()), 0)

    def test_get_score(self):
        scores = score()
        self.assertEquals(scores,
                          {bill: 2, darcy: -0.5, leo: -0.5, daniel: -1})

    def test_get_history_schedule(self):
        history_schedule = history()
        self.assertEquals(len(history_schedule), 2)
        self.assertEquals(history_schedule[0].note, "lunch for yesterday")
        self.assertEquals(history_schedule[1].note, "dinner@for#yesterday")

    def test_get_planned_schedule(self):
        planned_schedule = plan()
        self.assertEquals(len(planned_schedule), 1)
        self.assertEquals(planned_schedule[0].note, "future schedule")
