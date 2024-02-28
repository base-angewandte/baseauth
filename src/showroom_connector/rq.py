from datetime import timedelta

from django_rq import get_queue
from rq.exceptions import NoSuchJobError
from rq.registry import ScheduledJobRegistry

from django.conf import settings


def enqueue(job_id, function, **kwargs):
    queue = get_queue('default')
    registry = ScheduledJobRegistry(queue=queue)
    if job_id in registry.get_job_ids():
        try:
            registry.remove(job_id, delete_job=True)
        except NoSuchJobError:
            pass
    queue.enqueue_in(
        timedelta(seconds=settings.WORKER_DELAY),
        function,
        **kwargs,
        job_id=job_id,
    )
