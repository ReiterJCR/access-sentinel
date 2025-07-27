from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path("logout/", views.logout_view, name="logout"),
    path('files/', views.file_browser, name='file_browser'),
    path('open/<int:user_id>/<int:file_id>/', views.open_file, name='open_file'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('access-log/', views.access_log_view, name='access_log'),
]
