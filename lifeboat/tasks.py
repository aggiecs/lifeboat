from __future__ import absolute_import
from datetime import datetime

from celery.task.base import periodic_task
from celery.utils.log import get_task_logger
from celery.beat import crontab

from lifeboat.models import Error as LifeboatError
from lifeboat.models import Rescue
from lifeboat.models import Statistic

logger = get_task_logger("lifeboat")


# A periodic task that will run every minute (the symbol "*" means every)
@periodic_task(queue='lifeboat', options={'queue': 'lifeboat'}, run_every=(crontab(hour="*", minute="*", day_of_week="*")))
def handle_rescues():
    logger.debug("Starting task handle_rescues")
    unhandled_errors = LifeboatError.objects.filter(status="unhandled")
    logger.info("Found {0} unhandled errors".format(unhandled_errors.count()))
    for error in unhandled_errors:
        Rescue.rescue(error)

@periodic_task(queue='lifeboat', options={'queue': 'lifeboat'}, run_every=(crontab(hour="*", minute="*", day_of_week="*")))
def gather_stats():
    for stat in Statistic.objects.all():
        stat.try_reset_value()
        Statistic.gather_stat(stat)