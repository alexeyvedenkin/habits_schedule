from django.db import models
from django.contrib.auth.models import User

from habits.validators import validate_reward_or_related_habit, validate_related_habit, validate_pleasant_habit


class Habit(models.Model):
    # Пользователь — создатель привычки
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Место, в котором необходимо выполнять привычку
    location = models.CharField(max_length=100)

    # Время, когда необходимо выполнять привычку
    time = models.TimeField()

    # Действие, представляющее собой привычку
    action = models.CharField(max_length=255)

    # Признак приятной привычки (булевое значение)
    is_pleasant = models.BooleanField(default=False)

    # Связанная привычка (может быть NULL)
    related_habit = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    # Периодичность (по умолчанию ежедневная)
    frequency = models.IntegerField(default=1)  # Частота в днях

    # Вознаграждение после выполнения
    reward = models.CharField(max_length=255)

    # Время на выполнение привычки
    duration = models.DurationField()

    # Признак публичности
    is_public = models.BooleanField(default=False)

    def clean(self):
        """ Определяет метод clean для валидации """
        validate_reward_or_related_habit(self.reward, self)
        validate_related_habit(self)
        validate_pleasant_habit(self)

    def __str__(self):
        """ Форматирует строку с информацией о привычке """
        return f'Выполнить {self.action} в {self.time.strftime("%H:%M")} в {self.location}'
