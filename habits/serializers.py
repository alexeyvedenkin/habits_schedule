from rest_framework import serializers

from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit  # Используем модель Habit
        fields = "__all__"  # Включаем все поля модели
