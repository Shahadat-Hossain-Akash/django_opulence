from datetime import datetime
from app.models import Category, Transaction
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


class MonthField(serializers.Field):
    def to_representation(self, value):
        if isinstance(value, datetime):
            return value.month
        return value


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField()

    def check_user(self, validated_data):
        user = authenticate(
            email=validated_data["email"], password=validated_data["password"]
        )

        if not user:
            raise serializers.ValidationError("Email or password is incorrect")
        return user


class CategorySerializer(serializers.ModelSerializer):

    transaction_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ["name", "transaction_count"]

    def get_transaction_count(self, obj):
        return obj.transaction_count


class TransactionSerializer(serializers.ModelSerializer):

    month = serializers.SerializerMethodField(method_name="get_month")
    category = serializers.CharField(error_messages={"blank": "Select a category type"})

    def validate_category(self, value):
        if not Category.objects.filter(name=value.lower()).exists():
            raise serializers.ValidationError("Category does not exist!")
        return value

    def create(self, validated_data):
        user = self.context["user"]
        category_name = validated_data.pop("category").lower()
        category = Category.objects.get(name=category_name)

        return Transaction.objects.create(
            user=user, category=category, **validated_data
        )

    def get_month(self, obj):
        return obj.created_at.month

    class Meta:
        model = Transaction
        fields = ["id", "category", "title", "amount", "created_at", "month"]
