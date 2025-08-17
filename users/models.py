from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True)
    chat_id = models.BigIntegerField(verbose_name="ID чата в Telegram")

    # Изменяем related_name для групп
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # Добавляем уникальное имя
        blank=True,
        help_text='The groups this user belongs to.'
    )

    # Изменяем related_name для разрешений
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',  # Добавляем уникальное имя
        blank=True,
        help_text='Specific permissions for this user.'
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
