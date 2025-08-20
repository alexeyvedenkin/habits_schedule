import unittest
from datetime import timedelta, time

from django.urls import reverse
from rest_framework import status
# from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from habits.models import Habit
from habits.serializers import HabitSerializer
from habits.validators import UpdateHabitValidator, CreateHabitValidator
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

        # Создаём объект habit для использования в тестах
        self.habit = Habit.objects.create(
            user=self.user,
            time=time(1, 0),
            reward="Some reward",  # Теперь мы добавляем вознаграждение
            duration=timedelta(seconds=120),
            is_pleasant=False  # Устанавливаем is_pleasant в True
        )

    def test_clean_valid_duration(self):
        """ Проверка, что clean не вызывает ошибку при корректном duration """
        try:
            self.habit.clean()  # Вызываем метод clean
        except ValidationError:
            self.fail("clean() вызвал ValidationError при корректном duration.")

    def test_clean_invalid_duration(self):
        """ Проверка, что clean вызывает ошибку при некорректном duration """
        self.habit.duration = timedelta(seconds=130)  # Установим невалидное значение
        with self.assertRaises(ValidationError):
            self.habit.clean()  # Ожидаем ошибку

    def test_str_method(self):
        """ Проверка, что метод __str__ возвращает корректную строку """
        expected_str = f'Выполнить {self.habit.action} в {self.habit.time.strftime("%H:%M")} в {self.habit.location}'
        self.assertEqual(str(self.habit), expected_str)  # Проверяем ожидаемый результат

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

    def test_pleasant_habit_without_reward_or_related_habit(self):
        """Тест на создание приятной привычки с вознаграждением"""
        validator = CreateHabitValidator()
        attrs = {
            "is_pleasant": True,
            "reward": "Some reward",  # Здесь задано вознаграждение
            "related_habit": None
        }

        with self.assertRaises(ValidationError) as context:
            validator(attrs)  # Проверка работы валидатора
        self.assertEqual(str(context.exception.args[0]), "У приятной привычки не может быть вознаграждения")

    def test_useful_habit_without_reward_or_related_habit(self):
        """Тест на создание полезной привычки без вознаграждения и связанной привычки"""
        validator = CreateHabitValidator()
        attrs = {
            "is_pleasant": False,
            "reward": None,
            "related_habit": None
        }

        with self.assertRaises(ValidationError) as context:
            validator(attrs)  # Проверка работы валидатора
        self.assertEqual(str(context.exception.args[0]),
                         "У полезной привычки должно быть либо вознаграждение, либо связанная привычка")

    def test_useful_habit_with_both_reward_and_related_habit(self):
        """Тест на создание полезной привычки с вознаграждением и связанной привычкой"""
        validator = CreateHabitValidator()
        attrs = {
            "is_pleasant": False,
            "reward": "Some reward",
            "related_habit": 1  # Предполагается, что связанная привычка с ID 1 существует
        }

        with self.assertRaises(ValidationError) as context:
            validator(attrs)  # Проверка работы валидатора
        self.assertEqual(str(context.exception.args[0]),
                         "У полезной привычки должно быть либо вознаграждение, либо связанная привычка")

    def test_related_habit_not_pleasant(self):
        """Тест на создание полезной привычки с неприятной связанной привычкой"""
        # Создание связанной привычки
        related_habit = Habit.objects.create(
            user=self.user,
            time=time(1, 0),
            reward="Related reward",  # Здесь мы задаем значение для вознаграждения
            duration=timedelta(seconds=120),
            is_pleasant=False
        )

        validator = CreateHabitValidator()
        attrs = {
            "is_pleasant": False,
            "reward": None,
            "related_habit": related_habit
        }

        with self.assertRaises(ValidationError) as context:
            validator(attrs)  # Проверка работы валидатора
        self.assertEqual(str(context.exception.args[0]), "Связанная привычка должна быть приятной")

    def test_update_habit_validator_is_pleasant_with_reward(self):
        """Тестируем, что при приятной привычке с вознаграждением выдается ошибка"""
        validator = UpdateHabitValidator(instance=self.habit)
        with self.assertRaises(ValidationError) as context:
            validator({
                "is_pleasant": True,
                "reward": "Reward",
            })
        # Изменение: используем context.exception для извлечения ошибок
        self.assertEqual(str(context.exception.args[0]), "У приятной привычки не может быть вознаграждения")

    def test_update_habit_validator_is_pleasant_with_related_habit(self):
        """Тестируем, что при приятной привычке со связанной привычкой выдается ошибка"""
        validator = UpdateHabitValidator(instance=self.habit)
        with self.assertRaises(ValidationError) as context:
            validator({
                "is_pleasant": True,
                "related_habit": self.habit  # Используем текущую привычку как связанную
            })
        self.assertEqual(str(context.exception.args[0]), "У приятной привычки не может быть связанной привычки")

    def test_update_habit_validator_unpleasant_without_reward_or_related_habit(self):
        """Тестируем, что если привычка полезная и нет вознаграждения или связанной привычки, выдается ошибка"""
        validator = UpdateHabitValidator(instance=self.habit)
        with self.assertRaises(ValidationError) as context:
            validator({
                "is_pleasant": False,  # Полезная привычка
                "reward": None,
                "related_habit": None,
            })
        self.assertEqual(str(context.exception.args[0]), "У полезной привычки должно быть либо вознаграждение, либо связанная привычка")

    def test_update_habit_validator_unpleasant_with_both_reward_and_related_habit(self):
        """Тестируем, что если привычка полезная и есть оба: вознаграждение и связанная привычка, выдается ошибка"""
        related_habit = Habit.objects.create(
            user=self.user,
            time=time(2, 0),
            reward="Related reward",
            duration=timedelta(seconds=120),
            is_pleasant=True
        )
        validator = UpdateHabitValidator(instance=self.habit)
        with self.assertRaises(ValidationError) as context:
            validator({
                "is_pleasant": False,
                "reward": "Some Reward",
                "related_habit": related_habit,
            })
        self.assertEqual(str(context.exception.args[0]), "У полезной привычки должно быть либо вознаграждение, либо связанная привычка")


class TestHabitSerializer(unittest.TestCase):

    def test_update_validator(self):
        # Создаем экземпляр HabitSerializer с экземпляром
        instance = "some_habit_instance"  # замените на фактический объект
        serializer = HabitSerializer(instance=instance)

        # Проверяем, что валидатор установлен
        self.assertIsInstance(serializer.validators[0], UpdateHabitValidator)
        self.assertEqual(serializer.validators[0].instance, instance)

    def test_create_validator(self):
        # Создаем экземпляр HabitSerializer без экземпляра
        serializer = HabitSerializer()

        # Проверяем, что валидатор установлен для создания
        self.assertIsInstance(serializer.validators[0], CreateHabitValidator)




# class ValidationError(Exception):
#     """Определение исключения для ошибок валидации."""
#     pass


# class Habit:
#     """Простая модель привычки для тестирования."""
#     def __init__(self, id, is_pleasant):
#         self.id = id
#         self.is_pleasant = is_pleasant
#
#
#     def test_update_habit_validator(self):
#         # Создаем пример привычки
#         instance = Habit(id=1, is_pleasant=False)
#         validator = UpdateHabitValidator(instance)
#
#         # Тест 1: валидные данные
#         try:
#             validator({"is_pleasant": False, "reward": "test reward"})
#             print("Тест 1 пройден.")
#         except ValidationError as e:
#             print(f"Тест 1 не пройден: {e}")
#
#         # Тест 2: ошибка о недопустимом вознаграждении
#         try:
#             validator({"is_pleasant": True, "reward": "test reward"})
#             print("Тест 2 не пройден.")  # Не должно успешно пройти
#         except ValidationError:
#             print("Тест 2 пройден.")
#
#         # Тест 3: ошибка о недопустимой связанной привычке
#         try:
#             validator({"is_pleasant": True, "linked_habit": Habit(2, True)})
#             print("Тест 3 не пройден.")  # Не должно успешно пройти
#         except ValidationError:
#             print("Тест 3 пройден.")
