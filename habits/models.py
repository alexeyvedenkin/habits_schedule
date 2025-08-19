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
    reward = models.CharField(max_length=255, verbose_name="Вознаграждение")

    # Время на выполнение привычки
    duration = models.DurationField(verbose_name="Время на выполнение (в секундах)")

    # Признак публичности
    is_public = models.BooleanField(default=False, verbose_name="Публичность")

    # Владелец привычки
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_habits",
        blank=True,
        null=True,
        verbose_name="Владелец привычки",
    )

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"

    def clean(self):
        """ Определяет метод clean для валидации """

        # Проверяем, что duration больше 0 и не более 120 секунд
        if self.duration.total_seconds() <= 0 or self.duration.total_seconds() > 120:
            raise ValidationError("Время на выполнение должно быть более 0, но не более 120 секунд.")

        # Создаём экземпляр валидатора для создания привычки
        validator = CreateHabitValidator()
        # Собираем данные в атрибуты (в формате словаря)
        attrs = {"reward": self.reward, "is_pleasant": self.is_pleasant, "linked_habit": self.related_habit}
        # Вызываем валидатор
        validator(attrs)

    def __str__(self):
        """ Форматирует строку с информацией о привычке """
        return f'Выполнить {self.action} в {self.time.strftime("%H:%M")} в {self.location}'
