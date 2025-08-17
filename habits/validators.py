from django.core.exceptions import ValidationError

from habits.models import Habit

class CreateHabitValidator:

    def __call__(self, attrs):
        self.validate_habit(attrs)

    def validate_habit(self, attrs):
        is_pleasant = attrs.get("is_pleasant")

        if is_pleasant:
            reward = attrs.get("reward")
            linked_habit = attrs.get("linked_habit")

            if reward:
                raise ValidationError(
                    "У приятной привычки не может быть вознаграждения"
                )
            if linked_habit:
                raise ValidationError(
                    "У приятной привычки не может быть связанной привычки"
                )
        else:
            reward = attrs.get("reward")
            linked_habit = attrs.get("linked_habit")

            if not reward and not linked_habit:
                raise ValidationError(
                    "У полезной привычки должно быть либо вознаграждение, либо связанная привычка"
                )
            elif reward and linked_habit:
                raise ValidationError(
                    "У полезной привычки должно быть либо вознаграждение, либо связанная привычка"
                )
            if linked_habit:
                existing_linked_habit = Habit.objects.get(id=attrs["linked_habit"].id)
                if not existing_linked_habit.is_pleasant:
                    raise ValidationError("Связанная привычка должна быть приятной")


class UpdateHabitValidator:
    def __init__(self, instance=None):
        self.instance = instance

    def __call__(self, attrs):
        self.validate_habit(attrs)

    def validate_habit(self, attrs):
        if "is_pleasant" in attrs:
            is_pleasant = attrs.get("is_pleasant")
        else:
            is_pleasant = self.instance.is_pleasant

        if "reward" in attrs:
            reward = attrs.get("reward")
        else:
            reward = self.instance.reward

        if "linked_habit" in attrs:
            linked_habit = attrs.get("linked_habit")
        else:
            linked_habit = self.instance.linked_habit

        if is_pleasant:
            if reward:
                raise ValidationError(
                    "У приятной привычки не может быть вознаграждения"
                )
            if linked_habit:
                raise ValidationError(
                    "У приятной привычки не может быть связанной привычки"
                )
        else:
            if not reward and not linked_habit:
                raise ValidationError(
                    "У полезной привычки должно быть либо вознаграждение, либо связанная привычка"
                )
            elif reward and linked_habit:
                raise ValidationError(
                    "У полезной привычки должно быть либо вознаграждение, либо связанная привычка"
                )
            if linked_habit:
                existing_linked_habit = Habit.objects.get(id=linked_habit.id)
                if not existing_linked_habit.is_pleasant:
                    raise ValidationError("Связанная привычка должна быть приятной")