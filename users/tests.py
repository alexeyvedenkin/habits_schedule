from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User  # Импортируем модель User


class UserTests(APITestCase):

    def test_user_registration(self):
        # Создаем URL для регистрации пользователя
        url = reverse('users:register')

        # Данные для нового пользователя
        data = {
            "email": "testuser@example.com",
            "password": "testpassword",
            "chat_id": 123456789
        }

        # Отправляем POST-запрос на регистрацию
        response = self.client.post(url, data, format='json')

        # Проверяем, что ответ успешен и пользователь создан
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Ожидаем статус 201
        self.assertEqual(User.objects.count(), 1)  # Убедимся, что пользователь создан
        self.assertEqual(User.objects.get().email, "testuser@example.com")  # Проверяем email

    def test_user_registration_invalid_email(self):
        url = reverse('users:register')
        data = {
            "email": "not-an-email",
            "password": "testpassword",
            "chat_id": 123456789
        }

        # Отправляем POST-запрос с невалидным email
        response = self.client.post(url, data, format='json')

        # Проверяем, что получен ответ с ошибкой
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # Ожидаем статус 400
