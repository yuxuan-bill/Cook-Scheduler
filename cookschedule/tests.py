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
            time=get_time(self.today + timedelta(days=1), breakfast),
            note="future schedule"
        )
        future_schedule.set_eaters([leo, darcy, bill])
        future_schedule.set_cooks([leo, darcy])

        past_schedule1 = Schedule.objects.create(
            time=get_time(self.today + timedelta(days=-1), lunch),
            note="lunch for yesterday"
        )
        past_schedule1.set_eaters([leo, darcy, bill])
        past_schedule1.set_cooks([leo, darcy])

        past_schedule2 = Schedule.objects.create(
            time=get_time(self.today + timedelta(days=-1), dinner),
            note="dinner@for#yesterday!"
        )
        past_schedule2.set_cooks([bill])
        past_schedule2.set_eaters(participants)

        cancelled_schedule = Schedule.objects.create(
            time=get_time(self.today, lunch),
            cancelled=True,
            note="cancelled schedule"
        )
        cancelled_schedule.set_eaters(participants)
        cancelled_schedule.set_cooks(participants)

    def test_schema(self):
        schedules = Schedule.objects.all()
        self.assertEquals(len(schedules), 4)
        info2 = {'time': get_time(self.today + timedelta(days=-1), dinner),
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
            time=get_time(self.today + timedelta(days=1), breakfast))
        self.assertEquals(future_schedule.note, "future schedule")

    def test_add_new_schedule(self):
        day = datetime(year=2000, month=1, day=1).date()
        update(day=day,
               meal=lunch,
               cooks=[darcy],
               eaters=[leo],
               notes='new schedule')
        schedule = Schedule.objects.get(time=get_time(day, lunch))
        self.assertEquals(schedule.cooks(), [darcy])
        self.assertEquals(schedule.eaters(), [leo])
        self.assertEquals(schedule.note, 'new schedule')

    def test_modify_existent_schedule(self):
        update(day=self.today,
               meal=lunch,
               cooks=[darcy, bill, leo],
               eaters=participants,
               notes='restore schedule')
        schedule = Schedule.objects.get(time=get_time(self.today, lunch))
        self.assertEquals(schedule.cancelled, False)
        self.assertEquals(schedule.cooks(), [darcy, bill, leo])

    def test_delete_schedule(self):
        delete(self.today + timedelta(days=1), breakfast)
        self.assertEquals(len(plan()), 0)

    def test_hard_delete(self):
        hard_delete(self.today + timedelta(days=-1), dinner)
        time = get_time(self.today + timedelta(days=-1), dinner)
        try:
            Schedule.objects.get(time=time)
        except Schedule.DoesNotExist:
            pass
        else:
            self.fail()
        self.assertEquals(len(Cook.objects.filter(time=time)), 0)
        self.assertEquals(len(Eater.objects.filter(time=time)), 0)

    def test_delete_all(self):
        delete_all()
        self.assertEquals(len(Schedule.objects.all()), 0)
        self.assertEquals(len(Cook.objects.all()), 0)
        self.assertEquals(len(Eater.objects.all()), 0)

    def test_get_score(self):
        scores = score()
        self.assertEquals(scores,
                          {bill: 2, darcy: -0.5, leo: -0.5, daniel: -1})

    def test_get_history_schedule(self):
        history_schedule = history()
        self.assertEquals(len(history_schedule), 2)

        # history is in descending order of time
        self.assertEquals(history_schedule[1].note, "lunch for yesterday")
        self.assertEquals(history_schedule[0].note, "dinner@for#yesterday!")

    def test_get_planned_schedule(self):
        planned_schedule = plan()
        self.assertEquals(len(planned_schedule), 1)
        self.assertEquals(planned_schedule[0].note, "future schedule")
