"""
Asynchronous message-queue framework.
"""
from libtng.brokers.registry import brokers as __brokers




get = __brokers.get
add = __brokers.add
task = __brokers.task
init_celery = __brokers.init_celery