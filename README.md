# Платформа объявлений

## Описание проекта

Данный проект представляет собой backend-часть для сайта объявлений. Реализован с использованием Django и Django REST Framework (DRF), предоставляя API для взаимодействия с клиентской частью.

## Основные функции

- **Авторизация и аутентификация пользователей**: Реализована с использованием Simple JWT.
- **Распределение ролей**: Пользователи могут иметь роли "пользователь" или "админ".
- **Восстановление пароля**: Через электронную почту.
- **Управление объявлениями**: CRUD операции для объявлений с разграничением прав доступа.
- **Отзывы**: Возможность оставлять отзывы под объявлениями.
- **Поиск**: Поиск объявлений по названию.
- **Авторизация через email**:
    - Регистрация с подтверждением email.
    - Авторизация через email и пароль.
    - Сброс пароля с отправкой ссылки на email.
- **API в формате camelCase**:
    Все эндпоинты возвращают данные в формате camelCase для удобства работы с фронтендом.

## Технологии

- Django
- Django REST Framework
- PostgreSQL
- Simple JWT
- CORS headers
- Swagger
- Docker
- pytest
- Poetry

---

## Модели

### Модель пользователя
- `first_name` — имя пользователя (строка).
- `last_name` — фамилия пользователя (строка).
- `phone` — телефон для связи (строка).
- `email` — электронная почта пользователя (используется в качестве логина).
- `role` — роль пользователя (доступные значения: `user`, `admin`).
- `image` — аватарка пользователя.

### Модель объявления
- `title` — название товара.
- `price` — цена товара (целое число).
- `description` — описание товара.
- `author` — пользователь, создавший объявление.
- `created_at` — время и дата создания объявления.

### Модель отзыва
- `text` — текст отзыва.
- `author` — пользователь, оставивший отзыв.
- `ad` — объявление, под которым оставлен отзыв.
- `created_at` — время и дата создания отзыва.

---

## Права доступа

- **Анонимный пользователь**:
  - Может получать список объявлений.
- **Пользователь**:
  - Может получать список объявлений, создавать объявления, редактировать и удалять свои объявления.
  - Может оставлять, редактировать и удалять свои отзывы.
- **Администратор**:
  - Может редактировать и удалять любые объявления и отзывы.

---

## Установка и настройка

### 1. Установка зависимостей
Убедитесь, что у вас установлен Python версии **3.12**. Для установки зависимостей используйте [Poetry](https://python-poetry.org/):

```bash
poetry install
```

### 2. Настройка переменных окружения
Скопируйте файл `.env.example` в `.env`:

```bash
cp .env.example .env
```

Заполните файл `.env` следующими значениями:

```plaintext
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_PASSWORD=adminpassword123
NORMAL_USER_EMAIL=user@example.com
NORMAL_USER_PASSWORD=userpassword123
TELEGRAM_BOT_TOKEN=ваш_токен_бота
REDIS_URL=redis://127.0.0.1:6379/0
```

### 3. Запуск сервера разработки
```bash
python manage.py runserver
```

---

## Кастомные команды

### Команда `csu.py` (Create Super User)
Для автоматического создания суперпользователя и обычного пользователя выполните:

```bash
python manage.py csu
```

Эта команда создаёт двух пользователей на основе значений из `.env`:
1. Суперпользователь: `SUPERUSER_EMAIL` и `SUPERUSER_PASSWORD`.
2. Обычный пользователь: `NORMAL_USER_EMAIL` и `NORMAL_USER_PASSWORD`.

Если пользователи уже существуют, команда уведомит об этом.

---

## Установка и запуск

1. Клонируйте репозиторий:
   ```bash
   git clone git@github.com:Altair788/AdHub.git
   cd AdHub
   ```

2. Установите Poetry, если он еще не установлен:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Инициализируйте и установите зависимости с помощью Poetry:
   ```bash
   poetry install
   ```

4. Активируйте виртуальное окружение:
   ```bash
   poetry shell
   ```

5. Настройте переменные окружения в файле `.env`.

6. Примените миграции:
   ```bash
   python manage.py migrate
   ```

7. Запустите сервер:
   ```bash
   python manage.py runserver
   ```

---

## Запуск с использованием Docker

1. Убедитесь, что у вас установлены Docker и Docker Compose.

2. Запустите контейнеры:
   ```bash
   docker-compose up -d
   ```

3. Приложение будет доступно по адресу `http://localhost:8000`.

---

## API Документация

Документация API доступна по адресу `/swagger/` после запуска сервера.

---

## Эндпоинты

### Пользователи
- `POST /register/` — регистрация пользователя.
- `POST /email-confirm/` — подтверждение email.
- `POST /password-reset/` — запрос на сброс пароля.
- `POST /password-reset-confirm/` — подтверждение сброса пароля.
- `GET /users/` — получение списка пользователей.
- `GET /users/{id}/` — получение информации о пользователе.
- `PUT /users/{id}/` — обновление информации о пользователе.
- `DELETE /users/{id}/` — удаление пользователя.
- `POST /login/` — получение JWT токенов (логин).
- `POST /token/refresh/` — обновление JWT токена.

### Объявления
- `GET /ads/` — получение списка объявлений с пагинацией (4 объекта на страницу).
- `POST /ads/` — создание нового объявления.
- `GET /ads/{id}/` — получение информации о конкретном объявлении.
- `PUT /ads/{id}/` — обновление объявления.
- `DELETE /ads/{id}/` — удаление объявления.
- `GET /ads/?search={query}` — поиск объявлений по названию.

### Отзывы
- `GET /ads/{id}/reviews/` — получение списка отзывов для объявления.
- `POST /ads/{id}/reviews/` — создание отзыва для объявления.
- `PUT /ads/{id}/reviews/{review_id}/` — обновление отзыва.
- `DELETE /ads/{id}/reviews/{review_id}/` — удаление отзыва.

---

## Тестирование

Для запуска тестов используйте команду:
```bash
pytest
```

---

## Структура проекта

```
AdHub/
│
├── ads/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── tests.py
│
├── users/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── tests.py
│
├── config/
│   ├── settings.py
│   └── urls.py
│
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

---

## Настройка удаленного сервера и деплой

1. Обновите систему:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. Установите Docker, следуя [официальной инструкции](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository).

3. Настройте файрвол:
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   sudo ufw status
   ```

4. Настройте GitHub Secrets в настройках репозитория (Settings -> Secrets and variables -> Actions):
   - Данные базы данных: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`
   - Настройки Django: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
   - Доступ к Docker Hub: `DOCKER_HUB_USERNAME`, `DOCKER_HUB_ACCESS_TOKEN`
   - SSH-доступ: `SSH_USER`, `SSH_KEY`, `SERVER_IP`
   - Настройки Celery: `CELERY_BROKER_URL`, `CELERY_BACKEND`
   - Настройки email: 
     - `EMAIL_HOST`
     - `EMAIL_PORT`
     - `EMAIL_HOST_USER`
     - `EMAIL_HOST_PASSWORD`
     - `EMAIL_USE_SSL`
     - `EMAIL_USE_TLS`
   - Настройки Telegram-бота: 
     - `TELEGRAM_BOT_TOKEN`
   - Настройки для создания пользователей: 
     - `SUPERUSER_EMAIL`
     - `SUPERUSER_PASSWORD`
     - `NORMAL_USER_EMAIL`
     - `NORMAL_USER_PASSWORD`

5. Запуск CI/CD:
   - Push изменений в репозиторий автоматически запустит GitHub Actions workflow.
   - Workflow выполнит линтинг, тесты, сборку Docker-образа и деплой на сервер.

6. Проверка деплоя:
   После завершения workflow приложение будет доступно по IP-адресу сервера на порту 80.

---

## Доступ к развернутому приложению

Вы можете получить доступ к административной панели приложения по следующему адресу:

[http://130.193.54.21/admin/login/?next=/admin/](http://130.193.54.21/admin/login/?next=/admin/)

**Важно:** Этот URL предоставляет доступ к административной панели приложения. Убедитесь, что вы используете соответствующие учетные данные для входа.

---

## Автор
Telegram @eslobodyanik