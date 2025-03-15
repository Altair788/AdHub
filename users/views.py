import secrets

from django.core.mail import send_mail
from django.core import signing
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from config.settings import DEFAULT_FROM_EMAIL
from users.models import User
from users.serializers import (PasswordResetConfirmSerializer,
                               PasswordResetSerializer, UserSerializer)


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.save()


class UserListAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]


class UserRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]


#  поддерживает как put так и putch
class UserUpdateAPIView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]


class UserDestroyAPIView(generics.DestroyAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]


class UserRegisterAPIView(CreateAPIView):
    """
    Представление для регистрации нового пользователя.

    - Принимает email, пароль и другие данные пользователя.
    - Создаёт нового пользователя с полем `is_active=False`.
    - Генерирует токен для подтверждения email.
    - Отправляет письмо со ссылкой для подтверждения email.
    """

    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save()

        # Генерация токена
        user.token = secrets.token_hex(16)
        user.save()

        # Отправка письма с подтверждением email
        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{user.token}/"

        send_mail(
            subject="Подтверждение почты",
            message=f"Привет! Перейдите по ссылке для подтверждения почты: {url}",
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )


class PasswordResetAPIView(APIView):
    """
    Представление для запроса сброса пароля.

    Обрабатывает POST-запросы для инициации процесса сброса пароля:
    - Проверяет существование и активность пользователя по email.
    - Генерирует уникальный токен для сброса пароля.
    - Создает закодированный uid на основе ID пользователя.
    - Отправляет email со ссылкой для сброса пароля, содержащей uid и токен.

    Attributes:
        permission_classes (tuple): Разрешения доступа (AllowAny).

    Note:
        uid кодируется с использованием django.core.signing для безопасности.
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        print(f"Данные запроса: {request.data}")  # Отладочный вывод
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()  # Генерация токена
        print(f"Пользователь найден: {user.email}, ID: {user.id}")  # Отладочный вывод

        # Проверка, активен ли пользователь
        if not user.is_active:
            return Response(
                {"error": "Пользователь не активен. Подтвердите email для восстановления пароля."},
                status=HTTP_400_BAD_REQUEST,
            )

        # Кодируем user.id в uid
        uid = signing.dumps({"user_id": user.id})
        print(f"Закодированный uid: {uid}")  # Отладочный вывод

        host = request.get_host()
        url = f"http://{host}/users/password-reset-confirm/{uid}/{user.token}/"
        print(f"Ссылка для сброса пароля: {url}")  # Отладочный вывод

        send_mail(
            subject="Сброс пароля",
            message=f"Для сброса пароля перейдите по ссылке: {url}",
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return Response(
            {"message": "Инструкция по сбросу пароля отправлена на ваш email."}
        )


class PasswordResetConfirmAPIView(APIView):
    """
    Представление для подтверждения сброса пароля.

    - Принимает токен и новый пароль.
    - Проверяет корректность токена.
    - Устанавливает новый пароль пользователю.
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()  # Сохранение нового пароля

        return Response({"message": "Пароль успешно изменён."})


class EmailVerificationAPIView(APIView):
    """
    Представление для подтверждения email.

    - Принимает токен из ссылки, отправленной на email пользователя.
    - Активирует пользователя (`is_active=True`) при успешной проверке токена.
    - Удаляет токен после успешного подтверждения.
    """

    permission_classes = (AllowAny,)

    def get(self, request, token):
        # Пытаемся найти пользователя с указанным токеном
        user = get_object_or_404(User, token=token)

        if user.is_active:
            return Response(
                {"error": "Email уже подтверждён."}, status=HTTP_400_BAD_REQUEST
            )

        # Активируем пользователя и удаляем токен
        user.is_active = True
        user.token = None
        user.save()

        return Response({"message": "Email успешно подтверждён!"}, status=HTTP_200_OK)
