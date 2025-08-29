from django.core.exceptions import ValidationError


class CreateHabitValidator:

    def __call__(self, attrs):
        self.validate_habit(attrs)

    def validate_habit(self, attrs):
        from habits.models import Habit

        is_pleasant = attrs.get("is_pleasant")

        if is_pleasant:
            reward = attrs.get("reward")
            related_habit = attrs.get("related_habit")

            if related_habit:
                raise ValidationError("У приятной привычки не может быть связанной привычки")
            if reward:
                raise ValidationError("У приятной привычки не может быть вознаграждения")

        else:
            reward = attrs.get("reward")
            related_habit_id = attrs.get("related_habit")

            if not reward and not related_habit_id:
                raise ValidationError("У полезной привычки должно быть либо вознаграждение, либо связанная привычка")
            elif reward and related_habit_id:
                raise ValidationError("У полезной привычки должно быть либо вознаграждение, либо связанная привычка")
            if related_habit_id:
                existing_related_habit = Habit.objects.get(id=attrs["related_habit"].id)
                if not existing_related_habit.is_pleasant:
                    raise ValidationError("Связанная привычка должна быть приятной")


class UpdateHabitValidator:
    def __init__(self, instance=None):
        self.instance = instance

    def __call__(self, attrs):
        self.validate_habit(attrs)

    def validate_habit(self, attrs):
        from habits.models import Habit

        if "is_pleasant" in attrs:
            is_pleasant = attrs.get("is_pleasant")
        else:
            is_pleasant = self.instance.is_pleasant

        if "reward" in attrs:
            reward = attrs.get("reward")
        else:
            reward = self.instance.reward

        if "related_habit" in attrs:
            related_habit = attrs.get("related_habit")
        else:
            related_habit = self.instance.related_habit

        if is_pleasant:
            if related_habit:  # Сначала проверяем на связанную привычку
                raise ValidationError("У приятной привычки не может быть связанной привычки")
            if reward:  # Проверка на вознаграждение
                raise ValidationError("У приятной привычки не может быть вознаграждения")
        else:
            if not reward and not related_habit:
                raise ValidationError("У полезной привычки должно быть либо вознаграждение, либо связанная привычка")
            elif reward and related_habit:
                raise ValidationError("У полезной привычки должно быть либо вознаграждение, либо связанная привычка")
            if related_habit:
                existing_related_habit = Habit.objects.get(id=related_habit.id)
                if not existing_related_habit.is_pleasant:
                    raise ValidationError("Связанная привычка должна быть приятной")
