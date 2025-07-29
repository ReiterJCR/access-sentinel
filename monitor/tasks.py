from celery import shared_task

from .models import User as MonitorUser


@shared_task
def calculate_risk_score(user_id):
    user = MonitorUser.objects.get(id=user_id)
    logs = user.accesslog_set.order_by("-timestamp")[:50]  # last 50 actions
    score = 0

    for log in logs:
        sensitivity = log.file.sensitivity
        if sensitivity == "classified":
            score += 10
        elif sensitivity == "confidential":
            score += 6
        elif sensitivity == "internal":
            score += 3
        elif sensitivity == "public":
            score += 1

    # Apply trust level modifier (e.g., reduce risk for trusted users)
    trust_factor = (100 - user.trust_level) / 100
    adjusted_score = round(score * trust_factor, 2)

    user.risk_score = adjusted_score
    user.save()
    return adjusted_score
