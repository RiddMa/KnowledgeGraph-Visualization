from flask import Blueprint

from web.aps_test import _start_job

bp = Blueprint('aps', __name__, url_prefix='/api/aps')


@bp.route('/<job>', methods=['GET', 'POST'])
def start_job(job):
    print(job)
    _start_job()
    return 'Good.'
