from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
import re


class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")
        return self.create_user(email, full_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = [
        ("student", "Student"),
        ("staff", "Staff"),
        ("admin", "Admin"),
    ]

    email = models.EmailField(unique=True, max_length=254)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    # is_superuser 由 PermissionsMixin 提供，不需重複定義
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["email"], name="idx_users_email"),
            models.Index(fields=["role"], name="idx_users_role"),
        ]

    def __str__(self):
        return self.email


    def validate_password_strength(self, password):
        """
        Verify password strength (NFR-1):
            - At least 8 characters
            - Contains uppercase and lowercase letters
            - Contains numbers and symbols
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters"

        if not re.search(r"[A-Z]", password):
            return False, "Password must contain uppercase letters"

        if not re.search(r"[a-z]", password):
            return False, "Password must contain lowercase letters"

        if not re.search(r"[0-9]", password):
            return False, "Password must contain numbers"

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain symbols"

        return True, "Password is strong"


# TODO: pending — confirm if this logic is needed
# class PasswordResetToken(models.Model):
#     """Password reset Token"""
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     token = models.CharField(max_length=255, unique=True)
#     is_used = models.BooleanField(default=False)
#     expires_at = models.DateTimeField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         db_table = "password_reset_tokens"
