from rest_framework import generics

from .models import Habit
from .paginators import CustomPagination
from .serializers import HabitSerializer


class HabitListCreateView(generics.ListCreateAPIView):
    """Представление для получения списка привычек и создания новой привычки"""

    queryset = Habit.objects.all()  # Получаем все привычки
    serializer_class = HabitSerializer  # Используем сериализатор для Habit
    pagination_class = CustomPagination  # Используем пагинатор для Habit


class HabitRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Представление для получения, обновления и удаления привычки по ID"""

    queryset = Habit.objects.all()  # Получаем привычки
    serializer_class = HabitSerializer  # Используем сериализатор для Habit
