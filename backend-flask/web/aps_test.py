import datetime
from datetime import timezone
from time import sleep

from apscheduler.triggers.cron import CronTrigger
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler

# aps = APScheduler()
from vuln_kg.init_kg_p import init_kg_runner

scheduler = BackgroundScheduler()
ct = None


def fun1():
    print("From Func1")
    while 1:
        sleep(2)
    # print("From Func1 SLEEP")


def fun2():
    print(datetime.datetime.now())


def fun3():
    


def _start_kg():
    global ct
    # ct = CronTrigger(second='*', timezone=datetime.datetime.now().astimezone().tzinfo)
    ct = CronTrigger(hour=22, minute=30, timezone=datetime.datetime.now().astimezone().tzinfo)
    scheduler.add_job(id='init_kg_runner', func=init_kg_runner, trigger=ct)
    scheduler.start()
    return ct


def _start_crawl():
    global ct
    # ct = CronTrigger(second='*', timezone=datetime.datetime.now().astimezone().tzinfo)
    ct = CronTrigger(hour=22, minute=30, timezone=datetime.datetime.now().astimezone().tzinfo)
    scheduler.add_job(id='init_kg_runner', func=fun3, trigger=ct)
    scheduler.start()
    return ct


def stop_job():
    pass


def retrieve_progress():
    pass


if __name__ == '__main__':
    CronTrigger(hour=4, timezone=datetime.datetime.now().astimezone().tzinfo)
    _start_kg()
    while True:
        sleep(1)
