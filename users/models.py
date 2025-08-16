from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    telegram_id = models.CharField(unique=True, max_length=255, blank=True, null=True)

    USERNAME_FIELD = "telegram_id"
    REQUIRED_FIELDS = []
