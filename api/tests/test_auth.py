from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

VALID_PASSWORD = "user124!B"
VALID_EMAIL = "user124!B@example.com"
VALID_FULLNAME = "user124!B"
ROLE_ADMIN = "admin"


# =============================================
# 1. Model Tests
# =============================================
class UserModelTest(TestCase):

    def test_create_user_success(self):
        user = User.objects.create_user(
            email=VALID_EMAIL,
            full_name=VALID_FULLNAME,
            password=VALID_PASSWORD,
        )
        self.assertEqual(user.email, "user124!B@example.com")
        self.assertEqual(user.role, "student")
        self.assertTrue(user.is_active)

    def test_create_user_requires_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="", full_name="Test", password=VALID_PASSWORD
            )

    def test_str_returns_email(self):
        user = User.objects.create_user(
            email="str@example.com", full_name="Test", password=VALID_PASSWORD
        )
        self.assertEqual(str(user), "str@example.com")

    def test_password_strength_valid(self):
        user = User()
        is_valid, msg = user.validate_password_strength("Secure123!")
        self.assertTrue(is_valid)

    def test_password_strength_too_short(self):
        user = User()
        is_valid, _ = user.validate_password_strength("Ab1!")
        self.assertFalse(is_valid)

    def test_password_strength_no_uppercase(self):
        user = User()
        is_valid, msg = user.validate_password_strength("secure123!")
        self.assertFalse(is_valid)
        self.assertIn("uppercase", msg)

    def test_password_strength_no_symbol(self):
        user = User()
        is_valid, _ = user.validate_password_strength("Secure1234")
        self.assertFalse(is_valid)


# =============================================
# 2. Serializer Tests
# =============================================
class UserRegistrationSerializerTest(TestCase):

    def _get_valid_data(self, **overrides):
        data = {
            "email": VALID_EMAIL,
            "full_name": VALID_FULLNAME,
            "role": ROLE_ADMIN,
            "password": VALID_PASSWORD,
            "password_confirm": VALID_PASSWORD,
        }
        data.update(overrides)
        return data

    def test_valid_registration(self):
        from api.serializers.user_serializers import UserRegistrationSerializer

        serializer = UserRegistrationSerializer(data=self._get_valid_data())
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_password_mismatch(self):
        from api.serializers.user_serializers import UserRegistrationSerializer

        serializer = UserRegistrationSerializer(
            data=self._get_valid_data(password_confirm="WrongPass!")
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_weak_password_rejected(self):
        from api.serializers.user_serializers import UserRegistrationSerializer

        serializer = UserRegistrationSerializer(
            data=self._get_valid_data(password="weakpass", password_confirm="weakpass")
        )
        self.assertFalse(serializer.is_valid())

    def test_duplicate_email_rejected(self):
        from api.serializers.user_serializers import UserRegistrationSerializer

        User.objects.create_user(
            email=VALID_EMAIL, full_name="Existing", password=VALID_PASSWORD
        )
        serializer = UserRegistrationSerializer(
            data=self._get_valid_data(email=VALID_EMAIL)
        )
        self.assertFalse(serializer.is_valid())


class UserLoginSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email=VALID_EMAIL, full_name=VALID_FULLNAME, password=VALID_PASSWORD
        )

    def test_valid_login(self):
        from api.serializers.user_serializers import UserLoginSerializer

        serializer = UserLoginSerializer(
            data={"email": VALID_EMAIL, "password": VALID_PASSWORD}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["user"], self.user)

    def test_wrong_password(self):
        from api.serializers.user_serializers import UserLoginSerializer

        serializer = UserLoginSerializer(
            data={"email": VALID_EMAIL, "password": "WrongPass!"}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    # def test_inactive_user_rejected(self):
    #     from api.serializers.user_serializers import UserLoginSerializer
    #     self.user.is_active = False
    #     self.user.save()
    #     serializer = UserLoginSerializer(
    #         data={"email": "login@example.com", "password": VALID_PASSWORD}
    #     )
    #     self.assertFalse(serializer.is_valid())


# =============================================
# 3. View Tests (API End-to-End)
# =============================================
class RegisterViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("register")  # 依你的 urls.py 調整

    def _valid_payload(self, **overrides):
        data = {
            "email": "newuser@example.com",
            "full_name": "New User",
            "role": "student",
            "password": VALID_PASSWORD,
            "password_confirm": VALID_PASSWORD,
        }
        data.update(overrides)
        return data

    def test_register_success_returns_201(self):
        response = self.client.post(self.url, self._valid_payload(), format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])

    def test_register_creates_user_in_db(self):
        self.client.post(self.url, self._valid_payload(), format="json")
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_register_missing_fields_returns_400(self):
        response = self.client.post(self.url, {"email": "x@x.com"}, format="json")
        self.assertEqual(response.status_code, 400)


class LoginViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("login")
        self.user = User.objects.create_user(
            email=VALID_EMAIL, full_name=VALID_FULLNAME, password=VALID_PASSWORD
        )

    def test_login_success_returns_tokens(self):
        response = self.client.post(
            self.url,
            {"email":VALID_EMAIL, "password": VALID_PASSWORD},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password_returns_400(self):
        response = self.client.post(
            self.url,
            {"email":VALID_EMAIL, "password": "WrongPass!"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    # def test_inactive_user_returns_403(self):
    #     self.user.is_active = False
    #     self.user.save()
    #     response = self.client.post(
    #         self.url,
    #         {"email": "user@example.com", "password": VALID_PASSWORD},
    #         format="json",
    #     )
    #     self.assertEqual(response.status_code, 403)


class LogoutViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("logout")  # 依你的 urls.py 調整
        self.user = User.objects.create_user(
            email=VALID_EMAIL, full_name=VALID_FULLNAME, password=VALID_PASSWORD
        )
        self.refresh = RefreshToken.for_user(self.user)

    def test_logout_requires_authentication(self):
        response = self.client.post(
            self.url, {"refresh": str(self.refresh)}, format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_logout_success_returns_205(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url, {"refresh": str(self.refresh)}, format="json"
        )
        self.assertEqual(response.status_code, 205)

    def test_logout_with_invalid_token_returns_400(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url, {"refresh": "invalid.token.here"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
