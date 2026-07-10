from datetime import timedelta
from time import time
from celery import Celery
from celery.schedules import crontab
import time
from typing import Optional

celery = Celery(
    "tasks",
    broker="redis://localhost:6379",
)

# Schedule Jobs
celery.conf.beat_schedule = {
    # Run every night at midnight
    'task_every_30_sec': {
        'task': 'hello',
        'schedule': timedelta(minutes=1),
    }
}

# This is Task 
@celery.task(name= "hello")
def hello(a:Optional[int] = 1, b: Optional[int] = 2):
    n = 5
    sum = 0
    while n > 0:
        time.sleep(1)
        sum += n
        n -= 1

    return a + b