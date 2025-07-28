import random
from collections import defaultdict

import requests
from decouple import config
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import redirect, render

from .models import AccessLog, AnomalyLog, File
from .models import User as MonitorUser

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
    "Mozilla/5.0 (Linux; Android 11)",
]

IP_POOL = ["8.8.8.8", "104.26.10.228", "203.0.113.5", "185.199.110.153", "198.51.100.42"]


def index_view(request):
    return render(request, "monitor/index.html")


def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            auth_user = form.save()
            # Create linked monitor.User object
            MonitorUser.objects.create(auth_user=auth_user, username=auth_user.username, department="General")
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "monitor/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")
    users = MonitorUser.objects.all()
    error = None
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("index")
        else:
            error = "Invalid username or password"

    return render(request, "monitor/login.html", {"users": users, "error": error})


def logout_view(request):
    request.session.flush()
    return redirect("index")


@login_required
def file_browser(request):
    user = MonitorUser.objects.get(auth_user=request.user)
    files = File.objects.all()
    return render(request, "monitor/file_browser.html", {"user": user, "files": files})


@login_required
def open_file(request, file_id):
    user = MonitorUser.objects.get(auth_user=request.user)
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

    user_profiles = MonitorUser.objects.all()

    # File sensitivity report
    sensitivity_counts = File.objects.values("sensitivity").annotate(count=Count("id"))

    # Total access logs
    total_logs = AccessLog.objects.count()

    return render(
        request,
        "monitor/admin_dashboard.html",
        {
            "recent_anomalies": recent_anomalies,
            "user_profiles": user_profiles,
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
        except requests.RequestException:
            country = "??"

        if country not in user_countries[log.user.id] and user_countries[log.user.id]:
            anomalies.add(log.id)

        user_countries[log.user.id].add(country)

    return anomalies


def access_log_view(request):
    logs = AccessLog.objects.select_related("user", "file").order_by("-timestamp")
    anomaly_ids = get_user_country_map(logs)
    paginator = Paginator(logs, 25)  # Show 25 logs per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "monitor/file_access_log.html",
        {
            "logs": page_obj,
            "anomalies": anomaly_ids,
            "page_obj": page_obj,  # for pagination UI
        },
    )


@login_required
def live_access_feed(request):
    logs = AccessLog.objects.select_related("user", "file").order_by("-timestamp")[:15]
    data = [
        {
            "user": log.user.username,
            "file": log.file.name,
            "sensitivity": log.file.sensitivity,
            "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for log in logs
    ]
    return JsonResponse(data, safe=False)


@login_required
def dashboard_stats(request):
    top_users = AccessLog.objects.values("user__username").annotate(count=Count("id")).order_by("-count")[:5]

    anomaly_types = AnomalyLog.objects.values("anomaly_type").annotate(count=Count("id")).order_by("-count")

    sensitivity_counts = File.objects.values("sensitivity").annotate(count=Count("id"))

    return JsonResponse(
        {
            "top_users": list(top_users),
            "anomaly_types": list(anomaly_types),
            "sensitivity_counts": list(sensitivity_counts),
        }
    )
