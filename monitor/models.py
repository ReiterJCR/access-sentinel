from django.db import models


class User(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class File(models.Model):
    name = models.CharField(max_length=200)
    path = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class AccessLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return f"{self.user} accessed {self.file} from {self.ip_address} at {self.timestamp}"
