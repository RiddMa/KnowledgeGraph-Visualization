import datetime
from datetime import timezone
from time import sleep

from apscheduler.triggers.cron import CronTrigger
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler

# aps = APScheduler()
scheduler = BackgroundScheduler()


def fun1():
    print("From Func1")
    while 1:
        sleep(2)
    # print("From Func1 SLEEP")


def fun2():
    print("From Func2")


def fun3():
    print("From Func3")


if __name__ == '__main__':
    CronTrigger(hour=4, timezone=datetime.datetime.now().astimezone().tzinfo)
    ct = CronTrigger(second=30, timezone=datetime.datetime.now().astimezone().tzinfo)

    # print('{:.0f}%'.format(133/244*100))
    scheduler.add_job(id='Scheduled task 2', func=fun2, trigger=ct)
    scheduler.start()
    while True:
        sleep(1)
