from rest_framework.serializers import ModelSerializer

from habits.models import Habit
from habits.validators import CreateHabitValidator, UpdateHabitValidator
from users.models import User


class HabitSerializer(ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ("user",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            self.validators = [UpdateHabitValidator(instance=self.instance)]
        else:
            self.validators = [CreateHabitValidator()]


class UserSimpleSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name"]


class PublicHabitSerializer(ModelSerializer):
    user = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Habit
        fields = [
            "id",
            "time",
            "action",
            "is_pleasant",
            "frequency",
            "duration",
            "user",
        ]