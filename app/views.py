from django.contrib.auth import get_user_model, login, logout
from django.core.exceptions import ValidationError
from django.db.models import Case, DecimalField, F, Sum, Value, When
from django.middleware.csrf import get_token
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, serializers, status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .filters import TransactionFilter
from .models import Category, Transaction
from .serializers import (
    CategorySerializer,
    TransactionSerializer,
    UserLoginSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)
from .validations import custom_validation
from django.db.models import Count, Q

User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAdminUser,)

    def get_queryset(self):
        user = User
        return user.objects.all()

    serializer_class = UserSerializer


class UserRegister(
    viewsets.GenericViewSet,
    generics.ListCreateAPIView,
):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer

    def create(self, request):
        try:
            clean_data = custom_validation(request.data)
        except ValidationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=clean_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        return Response({}, status=status.HTTP_200_OK)


class UserLogin(
    viewsets.GenericViewSet,
    generics.CreateAPIView,
):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (SessionAuthentication,)
    serializer_class = UserLoginSerializer
    
    def get_queryset(self):
        return None

    def create(self, request):
        csrf_token = get_token(request)
        headers = {"token": csrf_token}
        serializer = self.get_serializer(
            data=request.data,
        )
        if serializer.is_valid(raise_exception=True):
            user = serializer.check_user(request.data)
            login(request, user)
            data = serializer.data
            data.update(headers) 
            return Response(data, status=status.HTTP_200_OK,)


class UserLogout(
    viewsets.GenericViewSet,
    generics.CreateAPIView,
):
    authentication_classes = [SessionAuthentication,]
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.Serializer

    def create(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ModelViewSet):

    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAdminUser,)
    
    def get_queryset(self):
        user = self.request.user
        queryset = Category.objects.annotate(
            transaction_count=Count('transaction', filter=Q(transaction__user=user))
        )
        return queryset



class TransactionViewSet(viewsets.ModelViewSet):

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = [
        "title",
    ]
    ordering_fields = ["created_at", "amount", "month"]
    filterset_fields = [
        "category",
    ]
    filterset_class = TransactionFilter

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.select_related("user", "category").filter(
            user_id=user.id
        )

    def get_paginated_response(self, data):
        queryset = self.get_queryset()

        balance_info = queryset.aggregate(
            income=Sum(
                Case(
                    When(category__name="income", then=F("amount")),
                    default=Value(0),
                    output_field=DecimalField(),
                )
            ),
            expense=Sum(
                Case(
                    When(category__name="expense", then=F("amount")),
                    default=Value(0),
                    output_field=DecimalField(),
                )
            ),
        )

        total_income = balance_info["income"] or 0
        total_expenses = balance_info["expense"] or 0

        balance = total_income - total_expenses
        response = {
            "income": total_income,
            "expense": total_expenses,
            "balance": balance,
            "transactions": data,
        }
        return super().get_paginated_response(response)

    def get_serializer_context(self):
        return {"user": self.request.user}

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not self.request.user.is_authenticated:
            return Response(
                "Sign up is required for this action",
                status=status.HTTP_401_UNAUTHORIZED,
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    serializer_class = TransactionSerializer
