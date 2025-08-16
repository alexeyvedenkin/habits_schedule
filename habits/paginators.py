from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Пагинатор для модели Habit"""

    page_size = 5  # Количество объектов на странице
    page_size_query_param = "page_size"  # Позволяет пользователю задать размер страницы
    max_page_size = 10  # Максимально возможный размер страницы
