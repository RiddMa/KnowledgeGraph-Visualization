from flask import Blueprint, request

from web.aps_test import _start_crawl, _stop_job, _start_job, check_aps

bp = Blueprint('aps', __name__, url_prefix='/api/aps')


@bp.get('/')
def get_aps_stats():
    return str(check_aps())


@bp.route('/<job>', methods=['GET', 'POST', 'DELETE'])
def find_method(job):
    if request.method == 'GET':
        return get_job_stats()
    elif request.method == 'POST':
        return start_job(job)
    elif request.method == 'DELETE':
        return stop_job(job)


def get_job_stats():
    pass


def start_job(job):
    if _start_job(job):
        return 'Good.'
    return 'Bad.'


def stop_job(job):
    if _stop_job(job):
        return 'Good.'
    return 'Bad.'
