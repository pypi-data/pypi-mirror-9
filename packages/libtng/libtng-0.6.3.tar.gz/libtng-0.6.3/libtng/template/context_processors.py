"""
Generic context processor used by the :mod:`libtng`/:mod:`jinja2`
template engine.
"""
from libtng.timezone import now


def current_timestamp(request):
    return {'current_timestamp': now()}