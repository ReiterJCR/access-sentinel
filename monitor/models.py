from django.contrib.auth.models import User as AuthUser
from django.contrib.postgres.fields import ArrayField
from django.db import models


class User(models.Model):
    username = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, null=True, blank=True)
    risk_score = models.IntegerField(default=0)
    trust_level = models.PositiveIntegerField(default=50)  # 50 is neutral, 0 is untrusted, 100 is fully trusted
    # if a user logs in with a different IP address, trust level should be reduced until they log in with their original IP
    file_access_history = models.ManyToManyField("File", through="AccessLog", related_name="user_history")
    home_ip = models.GenericIPAddressField(null=True, blank=True)
    trusted_ips = ArrayField(models.GenericIPAddressField(), default=list, blank=True)

    flagged_for_ip_mismatch = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class File(models.Model):
    name = models.CharField(max_length=200)
    path = models.CharField(max_length=300)
    sensitivity = models.CharField(max_length=20, choices=[("public", "Public"), ("internal ", "Internal"), ("confidential", "Confidential"), ("classified", "Classified")], default="public")

    def __str__(self):
        return self.name


class AccessLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=300, blank=True)  # Simulated device/browser

    def __str__(self):
        return f"{self.user.name} accessed {self.file.name} at {self.timestamp}"


class AnomalyLog(models.Model):
    access_log = models.OneToOneField(AccessLog, on_delete=models.CASCADE)
    anomaly_type = models.CharField(max_length=100)
    detail = models.TextField()
    severity = models.IntegerField(default=1)  # 1 = low, 5 = critical

    def __str__(self):
        return f"{self.anomaly_type} for {self.access_log.user.name} at {self.access_log.timestamp}"
