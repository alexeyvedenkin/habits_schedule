from django.contrib.auth.models import AbstractUser, UserManager as DefaultUserManager
from django.db import models


# class UserManager(DefaultUserManager):  # Создаем собственный менеджер
#     def create_superuser(self, email, chat_id, password=None, **extra_fields):
#         """Создание суперпользователя с email и chat_id"""
#         if not email:
#             raise ValueError("Email обязателен для создания суперпользователя")
#         email = self.normalize_email(email)
#         user = self.model(email=email, chat_id=chat_id, **extra_fields)  # Создаем пользователя
#         user.set_password(password)  # Устанавливаем пароль
#         user.is_staff = True
#         user.is_superuser = True
#         user.save(using=self._db)
#         return user


class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True)
    chat_id = models.BigIntegerField(verbose_name="ID чата в Telegram")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
