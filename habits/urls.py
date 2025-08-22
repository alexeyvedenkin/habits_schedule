from django.urls import path

from .apps import HabitsConfig
from .views import HabitListCreateView, HabitRetrieveUpdateDestroyView, PublicHabitListView

app_name = HabitsConfig.name

urlpatterns = [
    path("habits/", HabitListCreateView.as_view(), name="habit-list-create"),  # Список привычек и создание
    path(
        "habits/<int:pk>/", HabitRetrieveUpdateDestroyView.as_view(), name="habit-detail"
    ),  # Получение, обновление и удаление
    path("habits/public/", PublicHabitListView.as_view(), name="public-habit-list"
         ),  # Маршрут для публичных привычек
]
