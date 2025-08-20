import unittest
from datetime import time, timedelta

from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from habits.models import Habit
from habits.serializers import HabitSerializer
from habits.validators import CreateHabitValidator, UpdateHabitValidator
from users.models import User


class HabitTests(APITestCase):

    def setUp(self):
        """Создает тестового пользователя перед каждым тестом"""
        self.user_data = {
            "email": "test@example.com",
            "password": "password123",  # Проверка, что пароль соответствует требованиям
            "chat_id": 1234567890,
        }
        response = self.client.post("/users/register/", self.user_data)
        self.assertEqual(response.status_code, 201)  # Проверяем, что пользователь был успешно создан

        self.user = User.objects.get(email=self.user_data["email"])
        self.token = Token.objects.get(user=self.user)

        # Принудительное прохождение аутентификации для следующих запросов
        self.client.force_authenticate(user=self.user)

        # Создаём объект habit для использования в тестах
        self.habit = Habit.objects.create(
            user=self.user,
            time=time(1, 0),
            reward="Some reward",
            duration=timedelta(seconds=120),
            is_pleasant=False,
        )

        # Создаем полезную привычку для теста
        self.unpleasant_habit = Habit.objects.create(
            user=self.user,
            time=time(2, 0),
            reward="Unpleasant reward",
            duration=timedelta(seconds=60),
            is_pleasant=False,
        )

    def test_clean_valid_duration(self):
        """Проверка, что clean не вызывает ошибку при корректном duration"""
        self.habit.clean()  # Вызываем метод clean

    def test_clean_invalid_duration(self):
        """Проверка, что clean вызывает ошибку при некорректном duration"""
        self.habit.duration = timedelta(seconds=130)  # Установим невалидное значение
        with self.assertRaises(ValidationError):
            self.habit.clean()  # Ожидаем ошибку

    def test_str_method(self):
        """Проверка, что метод __str__ возвращает корректную строку"""
        expected_str = f'Выполнить {self.habit.action} в {self.habit.time.strftime("%H:%M")} в {self.habit.location}'
        self.assertEqual(str(self.habit), expected_str)  # Проверяем ожидаемый результат

    def test_create_habit(self):
        """Тестируем создание привычки"""
        url = reverse("habits:habit-list-create")
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
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Проверяем, что ответ 201
        self.assertEqual(response.data["action"], "Завтрак")  # Проверяем, что действие совпадает

    def test_create_habit_with_invalid_data(self):
        """Тестируем создание привычки с неверными данными"""
        url = reverse("habits:habit-list-create")
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
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        response = self.client.post(url, data, format="json")
        response_content = response.content.decode("utf-8")

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )  # Проверяем, что ответ 400 за неправильные данные
        self.assertIn("У приятной привычки не может быть вознаграждения", str(response_content))

    def test_pleasant_habit_without_reward_or_related_habit(self):
        """Тест на создание приятной привычки с вознаграждением"""
        validator = CreateHabitValidator()
        attrs = {"is_pleasant": True, "reward": "Some reward", "related_habit": None}  # Здесь задано вознаграждение

        with self.assertRaises(ValidationError) as context:
            validator(attrs)  # Проверка работы валидатора
        self.assertEqual(str(context.exception.args[0]), "У приятной привычки не может быть вознаграждения")

    def test_useful_habit_without_reward_or_related_habit(self):
        """Тест на создание полезной привычки без вознаграждения и связанной привычки"""
        validator = CreateHabitValidator()
        attrs = {"is_pleasant": False, "reward": None, "related_habit": None}

        with self.assertRaises(ValidationError) as context:
            validator(attrs)  # Проверка работы валидатора
        self.assertEqual(
            str(context.exception.args[0]),
            "У полезной привычки должно быть либо вознаграждение, либо связанная привычка",
        )

    def test_useful_habit_with_both_reward_and_related_habit(self):
        """Тест на создание полезной привычки с вознаграждением и связанной привычкой"""
        validator = CreateHabitValidator()
        attrs = {
            "is_pleasant": False,
            "reward": "Some reward",
            "related_habit": 1,  # Предполагается, что связанная привычка с ID 1 существует
        }

        with self.assertRaises(ValidationError) as context:
            validator(attrs)  # Проверка работы валидатора
        self.assertEqual(
            str(context.exception.args[0]),
            "У полезной привычки должно быть либо вознаграждение, либо связанная привычка",
        )

    def test_create_pleasant_habit_with_related_habit(self):
        """Тестирует создание приятной привычки со связанной привычкой"""
        # Создаем другую привычку, чтобы использовать её как связанную
        related_habit = Habit.objects.create(
            user=self.user,
            time=time(2, 0),
            action="Related action",
            duration=timedelta(seconds=120),
            is_pleasant=True,  # Связанная привычка должна быть приятной
            reward="Some reward",  # Добавляем значение для reward
        )

        # Пытаемся создать привычку с is_pleasant=True и без related_habit
        with self.assertRaises(ValidationError) as context:
            habit = Habit(
                user=self.user,
                time=time(3, 0),
                action="Pleasant action",
                duration=timedelta(seconds=120),
                is_pleasant=True,
                reward="Pleasant reward",
                related_habit=related_habit,
            )
            habit.clean()  # Явно вызываем метод clean()

        # Проверяем сообщение об ошибке
        self.assertEqual(str(context.exception.args[0]), "У приятной привычки не может быть связанной привычки")

    def test_related_habit_not_pleasant(self):
        """Тест на создание полезной привычки с неприятной связанной привычкой"""
        # Создание связанной привычки
        related_habit = Habit.objects.create(
            user=self.user,
            time=time(1, 0),
            reward="Related reward",  # Здесь мы задаем значение для вознаграждения
            duration=timedelta(seconds=120),
            is_pleasant=False,
        )

        validator = CreateHabitValidator()
        attrs = {"is_pleasant": False, "reward": None, "related_habit": related_habit}

        with self.assertRaises(ValidationError) as context:
            validator(attrs)  # Проверка работы валидатора
        self.assertEqual(str(context.exception.args[0]), "Связанная привычка должна быть приятной")

    def test_update_habit_validator_is_pleasant_with_reward(self):
        """Тестируем, что при приятной привычке с вознаграждением выдается ошибка"""
        validator = UpdateHabitValidator(instance=self.habit)
        with self.assertRaises(ValidationError) as context:
            validator(
                {
                    "is_pleasant": True,
                    "reward": "Reward",
                }
            )
        # Изменение: используем context.exception для извлечения ошибок
        self.assertEqual(str(context.exception.args[0]), "У приятной привычки не может быть вознаграждения")

    def test_update_habit_validator_is_pleasant_with_related_habit(self):
        """Тестируем, что при приятной привычке со связанной привычкой выдается ошибка"""
        validator = UpdateHabitValidator(instance=self.habit)
        with self.assertRaises(ValidationError) as context:
            validator({"is_pleasant": True, "related_habit": self.habit})  # Используем текущую привычку как связанную
        self.assertEqual(str(context.exception.args[0]), "У приятной привычки не может быть связанной привычки")

    def test_update_habit_validator_unpleasant_without_reward_or_related_habit(self):
        """Тестируем, что если привычка полезная и нет вознаграждения или связанной привычки, выдается ошибка"""
        validator = UpdateHabitValidator(instance=self.habit)
        with self.assertRaises(ValidationError) as context:
            validator(
                {
                    "is_pleasant": False,  # Полезная привычка
                    "reward": None,
                    "related_habit": None,
                }
            )
        self.assertEqual(
            str(context.exception.args[0]),
            "У полезной привычки должно быть либо вознаграждение, либо связанная привычка",
        )

    def test_update_habit_validator_unpleasant_with_both_reward_and_related_habit(self):
        """Тестируем, что если привычка полезная и есть оба: вознаграждение и связанная привычка, выдается ошибка"""
        related_habit = Habit.objects.create(
            user=self.user, time=time(2, 0), reward="Related reward", duration=timedelta(seconds=120), is_pleasant=True
        )
        validator = UpdateHabitValidator(instance=self.habit)
        with self.assertRaises(ValidationError) as context:
            validator(
                {
                    "is_pleasant": False,
                    "reward": "Some Reward",
                    "related_habit": related_habit,
                }
            )
        self.assertEqual(
            str(context.exception.args[0]),
            "У полезной привычки должно быть либо вознаграждение, либо связанная привычка",
        )

    def test_update_habit_without_is_pleasant(self):
        """Тестирует обновление привычки без указания is_pleasant"""
        # Изменяем только reward, не указывая is_pleasant
        update_data = {
            "reward": "Updated reward",
        }

        # Создаём валидатор с существующим экземпляром привычки
        validator = UpdateHabitValidator(instance=self.habit)

        # Вызываем валидатор с обновлёнными данными
        validator(update_data)
        # Обновляем привычку, используя данные из update_data
        for key, value in update_data.items():
            setattr(self.habit, key, value)  # Обновляем атрибуты экземпляра
        self.habit.save()  # Сохраняем изменения в базе данных

        # Добавляем проверку, чтобы увидеть, что обновление прошло успешно
        self.habit.refresh_from_db()  # Обновляем экземпляр с базы
        self.assertEqual(self.habit.reward, "Updated reward")  # Проверяем новое значение

    def test_related_habit_validation(self):
        # Логика создания полезной привычки
        self.unpleasant_habit.is_pleasant = False
        self.unpleasant_habit.save()

        with self.assertRaises(ValidationError) as context:
            habit = Habit(
                user=self.user,
                time=time(3, 0),
                reward="Test reward",
                duration=timedelta(seconds=60),
                is_pleasant=False,
                related_habit=self.unpleasant_habit,
            )
            habit.clean()

        self.assertEqual(str(context.exception.args[0]), "Связанная привычка должна быть приятной")

    def test_habit_validation(self):
        # Удаление reward для проверки условия валидации
        self.unpleasant_habit.reward = None  # Убираем вознаграждение

        # Проверка валидации для unpleasant_habit без вознаграждения
        with self.assertRaises(ValidationError) as context:
            self.unpleasant_habit.clean()  # Запуск метода clean для проверки валидации

        # Проверяем ожидаемое сообщение об ошибке
        self.assertEqual(
            str(context.exception.args[0]),
            "У полезной привычки должно быть либо вознаграждение, либо связанная привычка",
        )


class TestHabitSerializer(unittest.TestCase):

    def test_update_validator(self):
        # Создаем экземпляр HabitSerializer с экземпляром
        instance = "some_habit_instance"
        serializer = HabitSerializer(instance=instance)

        # Проверяем, что валидатор установлен
        self.assertIsInstance(serializer.validators[0], UpdateHabitValidator)
        self.assertEqual(serializer.validators[0].instance, instance)

    def test_create_validator(self):
        # Создаем экземпляр HabitSerializer без экземпляра
        serializer = HabitSerializer()

        # Проверяем, что валидатор установлен для создания
        self.assertIsInstance(serializer.validators[0], CreateHabitValidator)
