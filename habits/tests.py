from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist

from users.models import User
from users.views import UserCreateAPIView


class HabitTests(APITestCase):

    def setUp(self):
        """ Создает тестового пользователя перед каждым тестом """
        self.user_data = {
            "email": "test@example.com",
            "password": "password123",  # Убедитесь, что пароль соответствует требованиям
            "chat_id": 1234567890
        }
        response = self.client.post('/users/register/', self.user_data)
        self.assertEqual(response.status_code, 201)  # Проверяем, что пользователь был успешно создан

        self.user = User.objects.get(email=self.user_data['email'])
        self.token = Token.objects.get(user=self.user)

        # Принудительное прохождение аутентификации для следующих запросов
        self.client.force_authenticate(user=self.user)

    def test_create_habit(self):
        """ Тестируем создание привычки """
        url = reverse('habits:habit-list-create')
        data = {
            "user": self.user.id,
            "location": "Дом",
            "time": "09:00:00",
            "action": "Завтрак",
            "is_pleasant": True,
            "frequency": 7,
            "reward": "",
            "duration": "00:05:00",  # 5 минут
            "is_public": False,
            "owner": self.user.id,
        }

        # Добавляем заголовок авторизации с токеном
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Проверяем, что ответ 201
        self.assertEqual(response.data["action"], "Завтрак")  # Проверяем, что действие совпадает

    def test_create_habit_with_invalid_data(self):
        """ Тестируем создание привычки с неверными данными """
        url = reverse('habits:habit-list-create')
        data = {
            "user": self.user.id,
            "location": "Офис",
            "time": "10:00:00",
            "action": "Перерыв",
            "is_pleasant": True,
            "frequency": 5,
            "reward": "Кофе",
            "duration": "00:03:00",  # 3 минуты
            "is_public": False,
            "owner": self.user.id,
        }

        # Добавляем заголовок авторизации с токеном
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        response = self.client.post(url, data, format='json')
        response_content = response.content.decode('utf-8')

        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)  # Проверяем, что ответ 400 за неправильные данные
        self.assertIn("У приятной привычки не может быть вознаграждения", str(response_content))
