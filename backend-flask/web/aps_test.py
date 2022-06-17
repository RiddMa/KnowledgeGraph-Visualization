import datetime
from datetime import timezone
from time import sleep
from tzlocal import get_localzone

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler

from vuln_kg.init_kg_p import init_kg_runner

tz = datetime.datetime.now().astimezone().tzinfo
print(f'Current timezone: {tz}')
scheduler = BackgroundScheduler(timezone=tz)
ct = None


def fun1():
    print("From Func1")
    while 1:
        sleep(2)
    # print("From Func1 SLEEP")


def fun2():
    print(datetime.datetime.now())


def fun3():
    while True:
        print(f'func3 {datetime.datetime.now()}')
        sleep(1)


def _start_kg():
    global ct
    # ct = CronTrigger(second='*', timezone=datetime.datetime.now().astimezone().tzinfo)
    ct = CronTrigger(hour=4, timezone=datetime.datetime.now().astimezone().tzinfo)
    scheduler.add_job(id='init_kg_runner', func=init_kg_runner, trigger=ct)
    scheduler.start()
    return ct


def _start_crawl():
    ct = CronTrigger(hour=4, timezone=datetime.datetime.now().astimezone().tzinfo)
    scheduler.add_job(id='init_kg_runner', func=fun3, trigger=ct)
    scheduler.start()
    return ct


def _start_job(job):
    if job == 'data_collection':
        print(f'Start {job}')
        _ct = CronTrigger(second='*', timezone=datetime.datetime.now().astimezone().tzinfo)
        scheduler.add_job(id='data_collection', func=fun3, trigger=_ct)
        scheduler.start()
        return True
    elif job == 'build_kg':
        print(f'Add {job}')
        _ct = CronTrigger(second='*', timezone=datetime.datetime.now().astimezone().tzinfo)
        scheduler.add_job(id='build_kg', func=fun3, trigger=_ct)
        return True
    elif job == 'test':
        print(f'Add {job}')
        _t = DateTrigger(run_date=datetime.datetime.now(), timezone=datetime.datetime.now().astimezone().tzinfo)
        scheduler.add_job(id=job, func=fun3, trigger=_t)
        scheduler.start()
        return True
    return False


def _stop_job(job):
    if job == 'data_collection':
        print(f'Stop {job}')
        return True
    elif job == 'build_kg':
        print(f'Stop {job}')
        return True
    elif job == 'test':
        print(f'Stop {job}')
        # scheduler.remove_job(job_id=job)
        scheduler.shutdown()
        return True
    return False


def check_progress():
    pass


def check_aps():
    scheduler.print_jobs()
    return scheduler.print_jobs()


if __name__ == '__main__':
    CronTrigger(hour=4, timezone=datetime.datetime.now().astimezone().tzinfo)
    _start_kg()
    while True:
        sleep(1)
