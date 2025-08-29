from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class UserAPITestCase(APITestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user_data = {
            "email": "test@example.com",
            "password": "password123",  # Убедитесь, что пароль соответствует требованиям
            "chat_id": 1234567890,
        }

    def test_user_creation_and_str(self):
        # Отправляем запрос на создание пользователя
        response = self.client.post("/users/register/", self.user_data, format="json")

        # Проверяем, что запрос успешен
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Получаем созданного пользователя из базы данных
        user = User.objects.get(email=self.user_data["email"])

        # Проверяем корректное строковое представление
        expected_str = f"{user.first_name} {user.last_name} - {user.email}"
        self.assertEqual(str(user), expected_str)


class UserTestsCase(APITestCase):

    def test_user_registration(self):
        # Создаем URL для регистрации пользователя
        url = reverse("users:register")

        # Данные для нового пользователя
        data = {"email": "testuser@example.com", "password": "testpassword", "chat_id": 123456789}

        # Отправляем POST-запрос на регистрацию
        response = self.client.post(url, data, format="json")

        # Проверяем, что ответ успешен и пользователь создан
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Ожидаем статус 201
        self.assertEqual(User.objects.count(), 1)  # Убедимся, что пользователь создан
        self.assertEqual(User.objects.get().email, "testuser@example.com")  # Проверяем email

    def test_user_registration_invalid_email(self):
        url = reverse("users:register")
        data = {"email": "not-an-email", "password": "testpassword", "chat_id": 123456789}

        # Отправляем POST-запрос с невалидным email
        response = self.client.post(url, data, format="json")

        # Проверяем, что получен ответ с ошибкой
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # Ожидаем статус 400
