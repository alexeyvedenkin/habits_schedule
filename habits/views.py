from rest_framework import generics, permissions

from .models import Habit
from .paginators import CustomPagination
from .permissions import IsOwner
from .serializers import HabitSerializer


class HabitListCreateView(generics.ListCreateAPIView):
    """Представление для получения списка привычек и создания новой привычки"""

    queryset = Habit.objects.all()  # Получаем все привычки
    serializer_class = HabitSerializer  # Используем сериализатор для Habit
    pagination_class = CustomPagination  # Используем пагинатор для Habit

    def perform_create(self, serializer):
        """Автоматически устанавливает текущего пользователя как владельца привычки"""
        serializer.save(owner=self.request.user)  # Сохраняем привычку с текущим пользователем как владельцем

    def get_queryset(self):
        # Возвращаем только привычки текущего пользователя
        return self.queryset.filter(owner=self.request.user)

    # Применяем разрешение
    permission_classes = [permissions.IsAuthenticated]


class HabitRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Представление для получения, обновления и удаления привычки по ID"""

    queryset = Habit.objects.all()  # Получаем привычки
    serializer_class = HabitSerializer  # Используем сериализатор для Habit

    permission_classes = [permissions.IsAuthenticated, IsOwner]  # Проверяем, является ли пользователь владельцем


class PublicHabitListView(generics.ListAPIView):
    """Представление для получения списка публичных привычек"""
    queryset = Habit.objects.filter(is_public=True)  # Фильтруем только публичные привычки
    serializer_class = HabitSerializer  # Используем сериализатор для Habit
    pagination_class = CustomPagination  # Используем пагинатор для Habit
