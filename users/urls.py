from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .apps import UsersConfig
from .views import UserViewSet


app_name = UsersConfig.name

router = SimpleRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(permission_classes=(AllowAny,)), name="token_refresh"),

]

urlpatterns += router.urls
