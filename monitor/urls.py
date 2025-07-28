from django.urls import path

from . import views

urlpatterns = [
    path("", views.index_view, name="index"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("files/", views.file_browser, name="file_browser"),
    path("open/<int:file_id>/", views.open_file, name="open_file"),
    path("access-log/", views.access_log_view, name="access_log"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-dashboard/data/", views.dashboard_stats, name="dashboard_stats"),
    path("admin-dashboard/live-feed/", views.live_access_feed, name="live_access_feed"),
]
