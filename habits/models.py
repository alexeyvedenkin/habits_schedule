from django.core.exceptions import ValidationError
from django.db import models

from config import settings
from habits.validators import CreateHabitValidator


class Habit(models.Model):
    # Пользователь — создатель привычки
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Место, в котором необходимо выполнять привычку
    location = models.CharField(max_length=100, verbose_name="Место")

    # Время, когда необходимо выполнять привычку
    time = models.TimeField()

    # Действие, представляющее собой привычку
    action = models.CharField(max_length=255, verbose_name="Действие")

    # Признак приятной привычки (булевое значение)
    is_pleasant = models.BooleanField(default=False, verbose_name="Признак приятной привычки")

    # Связанная привычка (может быть NULL)
    related_habit = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)

    # Периодичность (по умолчанию ежедневная)
    frequency = models.PositiveSmallIntegerField(default=1, verbose_name="Периодичность")

    # Вознаграждение после выполнения
    reward = models.CharField(max_length=255, blank=True, null=True, verbose_name="Вознаграждение")

    # Время на выполнение привычки
    duration = models.DurationField(verbose_name="Время на выполнение (в секундах)")

    # Признак публичности
    is_public = models.BooleanField(default=False, verbose_name="Публичность")

    # Владелец привычки
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_habits",
        verbose_name="Владелец привычки",
    )

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"

    def clean(self):
        """Определяет метод clean для валидации"""

        # Проверяем, что duration больше 0 и не более 120 секунд
        if self.duration.total_seconds() <= 0 or self.duration.total_seconds() > 120:
            raise ValidationError("Время на выполнение должно быть более 0, но не более 120 секунд.")

        if not self.is_pleasant and not self.reward and not self.related_habit:
            raise ValidationError("У полезной привычки должно быть либо вознаграждение, либо связанная привычка")

        if self.is_pleasant and self.related_habit:
            raise ValidationError("У приятной привычки не может быть связанной привычки")

        # Проверяем, связанная привычка должна быть приятной
        if self.related_habit and not self.related_habit.is_pleasant:
            raise ValidationError("Связанная привычка должна быть приятной")

        # Создаем валидатор для вознаграждения
        attrs = {"reward": self.reward, "is_pleasant": self.is_pleasant, "related_habit": self.related_habit}
        validator = CreateHabitValidator()
        validator(attrs)

    def __str__(self):
        """Форматирует строку с информацией о привычке"""
        return f'Выполнить {self.action} в {self.time.strftime("%H:%M")} в {self.location}'
