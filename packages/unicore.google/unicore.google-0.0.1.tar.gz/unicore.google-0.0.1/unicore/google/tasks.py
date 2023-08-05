from celery.task import task

from UniversalAnalytics import Tracker


@task(ignore_result=True)
def pageview(profile_id, client_id, data):
    tracker = Tracker.create(profile_id,
                             client_id=client_id,
                             user_agent=data.pop('user_agent'))
    tracker.send('pageview', data)
