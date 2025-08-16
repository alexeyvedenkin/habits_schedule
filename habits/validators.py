from django.core.exceptions import ValidationError


def validate_reward_or_related_habit(value, habit):
    """Проверяет, что только одно из полей заполнено: вознаграждение или связанная привычка."""
    if habit.reward and habit.related_habit:
        raise ValidationError("Можно заполнить только одно из двух полей: вознаграждение или связанная привычка.")


def validate_duration(value):
    """Проверяет, что время выполнения не больше 120 секунд."""
    if value.total_seconds() > 120:
        raise ValidationError("Время на выполнение не должно превышать 120 секунд.")


def validate_related_habit(habit):
    """Проверяет, чтобы связанная привычка была приятной."""
    if habit.related_habit and not habit.related_habit.is_pleasant:
        raise ValidationError("Связанная привычка должна быть приятной.")


def validate_pleasant_habit(habit):
    """Проверяет, что у приятной привычки нет вознаграждения и связанной привычки."""
    if habit.is_pleasant and (habit.reward or habit.related_habit):
        raise ValidationError("У приятной привычки не должно быть вознаграждения или связанной привычки.")


def validate_frequency(value):
    """Проверяет, что привычку нельзя выполнять реже, чем 1 раз в 7 дней."""
    if value < 7:
        raise ValidationError("Периодичность выполнения привычки не может быть меньше 7 дней.")
