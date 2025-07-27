from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class File(models.Model):
    name = models.CharField(max_length=200)
    path = models.CharField(max_length=300)
    sensitivity = models.CharField(
        max_length=20,
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="low"
    )

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
