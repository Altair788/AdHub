import json

from django.core import signing, mail
from django.core.mail import EmailMessage
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
        Проверяет создание обычного пользователя.
        """
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.check_password("password123"))
        self.assertTrue(self.user.is_active)

    def test_create_superuser(self):
        """
        Проверяет создание суперпользователя.
        """
        superuser = User.objects.create_superuser(
            email="admin@example.com", password="adminpassword"
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_generate_token(self):
        """
        Проверяет генерацию токена для пользователя.
        """
        self.user.generate_token()
        self.assertIsNotNone(self.user.token)


#  Тесты для регистрации пользователя


class UserRegisterAPIViewTest(APITestCase):
    def test_register_user(self):
        """
        Проверяет регистрацию нового пользователя.
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
    """
    Проверяет подтверждение email пользователя.
    """
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
            email="test@example.com",
            password="password123",
            is_active=True
        )

        print(f"Пользователь в базе данных: {User.objects.all()}")  # Отладочный вывод

    def test_password_reset_request(self):
        """
        Проверяет запрос на сброс пароля:
        - Генерация токена.
        - Отправка email с инструкцией.
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

        # Проверяем, что сообщение содержит текст
        message = response.data.get('message', '')
        self.assertEqual(message, "Инструкция по сбросу пароля отправлена на ваш email.")

        # Проверяем, что письмо было отправлено
        outbox: list[EmailMessage] = mail.outbox
        # Должно быть одно письмо в outbox
        self.assertEqual(len(outbox), 1)

        # Проверяем содержимое письма
        email = outbox[0]
        self.assertEqual(email.subject, "Сброс пароля")
        self.assertEqual(email.to, ["test@example.com"])
        # Проверяем, что тело письма содержит ссылку
        self.assertIn("http://", email.body)

class PasswordResetConfirmAPIViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            token="testtoken",
            is_active=True
        )

        # Кодируем uid для использования в тестах
        self.uid = signing.dumps({"user_id": self.user.id})

    def test_password_reset_confirm(self):
        """
        Проверяет успешное подтверждение сброса пароля.
        """
        data = {
            "uid": self.uid,
            "token": "testtoken",
            "new_password": "newpassword123",
        }

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
        self.assertIsNone(self.user.token)

    def test_password_reset_confirm_invalid_uid(self):
        """
        Проверяет сброс пароля с неверным uid.
        """
        data = {
            "uid": "invalid_uid",
            "token": "testtoken",
            "new_password": "newpassword123",
        }

        response = self.client.post(
            "/users/password-reset-confirm/",
            data=json.dumps(data),
            content_type="application/json",
        )

        # Проверяем статус ответа
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # [ErrorDetail(string='Неверный идентификатор пользователя.', code='invalid')]
        self.assertEqual(response.data.get("uid")[0], "Неверный идентификатор пользователя.")

    def test_password_reset_confirm_invalid_token(self):
        """
        Проверяет сброс пароля с неверным токеном.
        """
        data = {
            "uid": self.uid,
            "token": "invalid_token",
            "new_password": "newpassword123",
        }

        response = self.client.post(
            "/users/password-reset-confirm/",
            data=json.dumps(data),
            content_type="application/json",
        )

        # Проверяем статус ответа
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("token")[0], "Неверный токен.")

    def test_password_reset_confirm_inactive_user(self):
        """
        Проверяет сброс пароля для неактивного пользователя.
        """
        self.user.is_active = False
        self.user.save()

        data = {
            "uid": self.uid,
            "token": "testtoken",
            "new_password": "newpassword123",
        }

        response = self.client.post(
            "/users/password-reset-confirm/",
            data=json.dumps(data),
            content_type="application/json",
        )

        # Проверяем статус ответа
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("uid")[0], "Пользователь не активен. Необходимо подтвердить email"
        )
