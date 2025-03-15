import secrets

from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.
    """

    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    tg_id = serializers.IntegerField(allow_null=True, required=False)
    tg_nick = serializers.CharField(allow_null=True, required=False)
    first_name = serializers.CharField(allow_null=True, required=False)
    last_name = serializers.CharField(allow_null=True, required=False)
    token = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    phone = serializers.CharField(allow_null=True, required=False)
    country = serializers.CharField(allow_null=True, required=False)
    role = serializers.CharField(read_only=True)
    image = serializers.ImageField(
        # Поле может быть пустым
        allow_null=True,
        # Необязательно для заполнения
        required=False,
        # Возвращать полный URL (если настроен MEDIA_URL)
        use_url=True,
    )

    def create(self, validated_data):
        email = validated_data.get("email")

        # Проверка на существование пользователя с таким же email
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"email": ["Пользователь с такой почтой уже существует."]}
            )

        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        # Пользователь не активен до подтверждения email
        user.is_active = False
        # Генерация токена для подтверждения email
        user.token = secrets.token_hex(16)
        user.save()
        return user

    class Meta:
        model = User
        fields = (
            "id",  # Только для чтения
            "email",  # Обязателен для заполнения
            "password",  # Только для записи
            "tg_id",  # Не обязателен для заполнения
            "tg_nick",  # Не обязателен для заполнения
            "first_name",  # Не обязателен для заполнения
            "last_name",  # Не обязателен для заполнения
            "token",  # Только для чтения
            "is_active",  # Только для чтения
            "phone",  # Не обязателен для заполнения
            "country",  # Не обязателен для заполнения
            "image",  # Не обязателен для заполнения
            "role",  # Только для чтения
        )


class PasswordResetSerializer(serializers.Serializer):
    """
    Сериализатор для отправки email на сброс пароля
    Этот сериализатор проверяет, существует ли пользователь с указанным email,
    и генерирует токен для сброса пароля
    """

    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email не найден.")
        return value

    def save(self):
        user = User.objects.get(email=self.validated_data["email"])
        # Генерация токена для сброса пароля
        user.token = secrets.token_hex(16)
        user.save()
        return user


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Сериализатор для подтверждения сброса пароля
    Этот сериализатор принимает токен и новый пароль,
    проверяет их и обновляет пароль пользователя
    """

    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if not User.objects.filter(token=data["token"]).exists():
            raise serializers.ValidationError("Неверный токен.")
        return data

    def save(self):
        user = User.objects.get(token=self.validated_data["token"])
        user.set_password(self.validated_data["new_password"])
        # Удаляем токен после успешного сброса пароля
        user.token = None
        user.save()
