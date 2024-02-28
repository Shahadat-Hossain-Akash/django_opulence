from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

def custom_validation(data):
    email = data.get("email", "").strip()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not email:
        raise ValidationError("Email is required")
    if User.objects.filter(email=email).exists():
        raise ValidationError("Email is already in use. Please choose another one.")

    if not username:
        raise ValidationError("Username is required")

    if not password:
        raise ValidationError("Password is required")

    return data
