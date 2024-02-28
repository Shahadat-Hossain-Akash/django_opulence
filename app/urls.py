from django.urls import path, include
from rest_framework import routers
from .views import (
    CategoryViewSet,
    TransactionViewSet,
    UserViewSet,
    UserRegister,
    UserLogin,
    UserLogout,
)

router = routers.DefaultRouter()
router.register(r"category", CategoryViewSet, basename="category")
router.register(r"transaction", TransactionViewSet, basename="transaction")
router.register(r"users", UserViewSet, basename="users")
router.register(r"register", UserRegister, basename="register")
router.register(r"login", UserLogin, basename="login")
router.register(r"logout", UserLogout, basename="logout")

urlpatterns = [
    path("", include(router.urls)),
]