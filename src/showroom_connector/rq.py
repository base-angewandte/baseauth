from datetime import timedelta

from django_rq import get_queue
from rq.exceptions import NoSuchJobError
from rq.registry import ScheduledJobRegistry

from django.conf import settings


def enqueue(job_id, function, **kwargs):
    """Wrapper function to enqueue worker jobs only once and with a delay.

    In cases of mass user updates, or when a user updates their settings
    in several quick consecutive API calls, we only want to enqueue the
    sync of the user once. Therefore, we delete prior existing jobs to
    sync the same user, before we freshly enqueue it with a configurable
    delay.
    """
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
