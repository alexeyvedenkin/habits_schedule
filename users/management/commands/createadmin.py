from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'Создает суперпользователя с заданным email и паролем'

    def handle(self, *args, **options):
        User = get_user_model()

        # Проверка, существует ли пользователь с таким email
        if User.objects.filter(email="testadmin@sky.pro").exists():
            self.stdout.write(self.style.WARNING("Пользователь уже существует."))
            return

        user = User(
            email="testadmin@sky.pro",  # Установка email по умолчанию
            chat_id=12345  # Удалил кавычки для числового значения
        )

        user.set_password("1234")  # Установка пароля по умолчанию
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True

        user.save()  # Сохранение пользователя в базе данных
        self.stdout.write(self.style.SUCCESS(f"Успешно создан администратор с email {user.email}"))
