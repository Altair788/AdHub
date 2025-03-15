import json

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User

#  тестирование методов модели User


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="password123", is_active=True
        )

    def test_create_user(self):
        """
        Тест создания пользователя.
        """
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.check_password("password123"))
        self.assertTrue(self.user.is_active)

    def test_create_superuser(self):
        """
        Тест создания суперпользователя.
        """
        superuser = User.objects.create_superuser(
            email="admin@example.com", password="adminpassword"
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_generate_token(self):
        """
        Тест генерации токена.
        """
        self.user.generate_token()
        self.assertIsNotNone(self.user.token)


#  Тесты для регистрации пользователя


class UserRegisterAPIViewTest(APITestCase):
    def test_register_user(self):
        """
        Тест регистрации нового пользователя.
        """
        data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "phone": "+1234567890",
            "country": "USA",
        }

        response = self.client.post(
            "/users/register/", data=json.dumps(data), content_type="application/json"
        )

        # Проверяем статус ответа
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем, что пользователь создан
        user = User.objects.get(email="newuser@example.com")
        self.assertFalse(
            user.is_active
        )  # Пользователь должен быть неактивным по умолчанию


#  Тесты для подтверждения email


class EmailVerificationAPIViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="password123", token="testtoken"
        )

    def test_email_verification(self):
        """
        Тест подтверждения email.
        """
        response = self.client.get(f"/users/email-confirm/{self.user.token}/")

        # Проверяем статус ответа
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что пользователь активирован и токен удалён
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertIsNone(self.user.token)


#  Тесты для сброса пароля
class PasswordResetAPIViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="password123"
        )

    def test_password_reset_request(self):
        """
        Тест запроса на сброс пароля.
        """
        data = {"email": "test@example.com"}

        response = self.client.post(
            "/users/password-reset/",
            data=json.dumps(data),
            content_type="application/json",
        )
        # Проверяем статус ответа
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что токен сгенерирован
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.token)


class PasswordResetConfirmAPIViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="password123", token="testtoken"
        )

    def test_password_reset_confirm(self):
        """
        Тест подтверждения сброса пароля.
        """
        data = {"token": "testtoken", "new_password": "newpassword123"}

        response = self.client.post(
            "/users/password-reset-confirm/",
            data=json.dumps(data),
            content_type="application/json",
        )

        # Проверяем статус ответа
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что пароль обновлён и токен удалён
        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password("newpassword123"))
