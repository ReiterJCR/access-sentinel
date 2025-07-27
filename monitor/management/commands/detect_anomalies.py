from collections import defaultdict
from datetime import timedelta

import pytz
import requests
from decouple import config
from django.core.management.base import BaseCommand

from monitor.models import AccessLog, AnomalyLog


class Command(BaseCommand):
    help = "Detect anomalies in access logs and populate AnomalyLog table"

    def handle(self, *args, **kwargs):
        token = config("IPINFO_TOKEN", default="")
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        user_country_map = defaultdict(set)
        access_logs = AccessLog.objects.select_related("user", "file").order_by("timestamp")
        anomaly_count = 0

        for i, log in enumerate(access_logs):
            user = log.user
            ip = log.ip_address
            timestamp = log.timestamp
            file = log.file

            # Check if already flagged
            if hasattr(log, "anomalylog"):
                continue

            anomalies = []

            # 🌍 GeoIP Mismatch
            try:
                res = requests.get(f"https://ipinfo.io/{ip}/json", headers=headers, timeout=3)
                country = res.json().get("country", "??")
            except:
                country = "??"

            known_countries = user_country_map[user.id]
            if country not in known_countries and known_countries:
                anomalies.append({"type": "GeoIP Mismatch", "detail": f"User accessed from new country {country} (previous: {', '.join(known_countries)})", "severity": 3})
            user_country_map[user.id].add(country)

            # 🌙 After-hours access (local time 9am–6pm UTC)
            hour = timestamp.hour
            if hour < 9 or hour > 18:
                anomalies.append({"type": "After-hours Access", "detail": f"Access at {hour}:00 UTC (outside working hours)", "severity": 2})

            # 📤 Access Spike Detection
            window_start = timestamp - timedelta(minutes=10)
            window_logs = AccessLog.objects.filter(user=user, timestamp__gte=window_start, timestamp__lte=timestamp)
            if window_logs.count() > 20:
                anomalies.append({"type": "Suspicious Activity Spike", "detail": f"{window_logs.count()} file accesses within 10 minutes", "severity": 4})

            # 🚨 Save all anomalies
            for a in anomalies:
                AnomalyLog.objects.create(access_log=log, anomaly_type=a["type"], detail=a["detail"], severity=a["severity"])
                anomaly_count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Detection complete — {anomaly_count} anomalies logged."))
