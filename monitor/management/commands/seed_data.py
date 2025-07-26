from django.core.management.base import BaseCommand
from monitor.models import User, File, AccessLog
from faker import Faker
import random

fake = Faker()

class Command(BaseCommand):
    help = "Seed the database with fake users, files, and access logs"

    def handle(self, *args, **kwargs):
        User.objects.all().delete()
        File.objects.all().delete()
        AccessLog.objects.all().delete()

        users = []
        for _ in range(10):
            user = User.objects.create(
                name=fake.name(),
                department=fake.job().split(' ')[0]
            )
            users.append(user)

        files = []
        for _ in range(10):
            file = File.objects.create(
                name=fake.file_name(extension="docx"),
                path=fake.file_path(depth=2)
            )
            files.append(file)

        for _ in range(100):
            AccessLog.objects.create(
                user=random.choice(users),
                file=random.choice(files),
                ip_address=fake.ipv4_public(),
                timestamp=fake.date_time_this_year()
            )

        self.stdout.write(self.style.SUCCESS("Seeded DB with users, files, and access logs."))
