import random
from collections import defaultdict

import requests
from decouple import config
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import redirect, render

from .models import AccessLog, AnomalyLog, File, User

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
    "Mozilla/5.0 (Linux; Android 11)",
]

IP_POOL = ["8.8.8.8", "104.26.10.228", "203.0.113.5", "185.199.110.153", "198.51.100.42"]


def index_view(request):
    return render(request, "monitor/index.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "monitor/login.html", {"error": "Invalid credentials"})

    return render(request, "monitor/login.html")


def logout_view(request):
    request.session.flush()
    return redirect("index")


@login_required
def file_browser(request):
    user = request.user
    files = File.objects.all()
    return render(request, "monitor/file_browser.html", {"user": user, "files": files})


@login_required
def open_file(request, file_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    user = User.objects.get(id=user_id)
    file = File.objects.get(id=file_id)

    ip = random.choice(IP_POOL)
    ua = random.choice(USER_AGENTS)

    AccessLog.objects.create(
        user=user,
        file=file,
        ip_address=ip,
        user_agent=ua,
    )

    return redirect("file_browser")


@login_required
def admin_dashboard(request):
    # Get recent anomalies
    recent_anomalies = AnomalyLog.objects.select_related("access_log", "access_log__user", "access_log__file").order_by("-access_log__timestamp")[:25]

    # Risk score: count anomalies per user
    user_anomalies = AnomalyLog.objects.values("access_log__user__id", "access_log__user__name").annotate(count=Count("id")).order_by("-count")

    # File sensitivity report
    sensitivity_counts = File.objects.values("sensitivity").annotate(count=Count("id"))

    # Total access logs
    total_logs = AccessLog.objects.count()

    return render(
        request,
        "monitor/admin_dashboard.html",
        {
            "recent_anomalies": recent_anomalies,
            "user_anomalies": user_anomalies,
            "sensitivity_counts": sensitivity_counts,
            "total_logs": total_logs,
        },
    )


def get_user_country_map(logs):
    token = config("IPINFO_TOKEN", default="")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    user_countries = defaultdict(set)
    anomalies = set()

    for log in logs:
        ip = log.ip_address
        if ip.startswith("192.") or ip.startswith("10.") or ip.startswith("127."):
            continue

        try:
            res = requests.get(f"https://ipinfo.io/{ip}/json", headers=headers, timeout=5)
            country = res.json().get("country", "??")
        except:
            country = "??"

        if country not in user_countries[log.user.id] and user_countries[log.user.id]:
            anomalies.add(log.id)

        user_countries[log.user.id].add(country)

    return anomalies


def access_log_view(request):
    logs = AccessLog.objects.select_related("user", "file").order_by("-timestamp")
    anomaly_ids = get_user_country_map(logs)
    return render(request, "monitor/file_access_log.html", {"logs": logs, "anomalies": anomaly_ids})
