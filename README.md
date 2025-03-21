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

- Django 4.2.2
- Django REST Framework
- PostgreSQL
- Simple JWT
- CORS headers
- Swagger (drf-yasg)
- Redoc
- Docker
- pytest
- Poetry
- Celery
- Redis
- Gunicorn
- drf-spectacular (для API документации)
- django-filter
- djangorestframework-camel-case
- Pillow (для работы с изображениями)
- Coverage (для анализа покрытия кода тестами)
- Loguru (для улучшенного логирования)

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

### Команда `fill_db` (Fill Database)
Для заполнения базы данных тестовыми данными выполните:

```bash
python manage.py fill_db
```

Эта команда создает:
- Двух тестовых пользователей (один с ролью администратора, другой - обычный пользователь)
- Несколько тестовых объявлений
- Несколько тестовых отзывов

После выполнения команда выводит информацию о созданных пользователях, их ролях и количестве созданных объектов.

**Примечание:** Перед повторным выполнением команды `fill_db` рекомендуется очистить базу данных от предыдущих тестовых записей во избежание дублирования данных.

### Создание и загрузка фикстур

Для создания фикстуры групп пользователей выполните:

```bash
python3 manage.py dumpdata auth.group --indent 2 > users/fixtures/groups.json
```

Эта команда создаст файл `groups.json` в директории `users/fixtures/` с данными о группах пользователей.

Для загрузки данных из созданной фикстуры в базу данных используйте команду:

```bash
python3 manage.py loaddata users/fixtures/groups.json
```

Эта команда загрузит группы пользователей из файла `groups.json` в базу данных.

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

1. У вас должны быть установлены Docker и Docker Compose.

Перед запуском контейнеров убедитесь, что в .env у вас POSTGRES_HOST=db
2. Запустите контейнеры:
   ```bash
   docker-compose up -d
   ```

3. Приложение будет доступно по адресу `http://localhost:80`.

---

## API Документация

Документация API доступна по адресу `/swagger/` или `/redoc/` после запуска сервера.

---

## Тестирование
Текущее покрытие тестами составляет 97% кода проекта.
Для запуска тестов вы можете использовать следующие команды:

1. Запуск всех тестов:
```bash
python3 manage.py test
```

2. Запуск тестов для конкретного приложения (например, для приложения 'ads'):
```bash
python3 manage.py test ads
```

3. Запуск тестов с покрытием кода:
```bash
coverage run --source='.' manage.py test
```

4. Просмотр отчета о покрытии кода:
```bash
coverage report
```

5. Запуск отдельного теста:
```bash
python3 manage.py test ads.tests.AdTestCase.test_create_ad
```
---

## Ключевые особенности проекта

- **Усиленная система безопасности**:
  - Использование закодированных UID вместо простых ID для идентификации объектов.
  - Токен-аутентификация с переменным токеном для повышенной безопасности.
  - Шифрование паролей пользователей перед сохранением в базу данных.

- **Оптимизация для фронтенд-разработки**:
  - Вывод данных API в формате camelCase для удобства интеграции с фронтендом.

- **Гибкая архитектура API**:
  - Использование generic views Django REST Framework для поддержки частичного обновления объектов (PATCH и PUT запросы).

- **Надежная валидация данных**:
  - Двухуровневая валидация: на уровне модели (в методе clean) и на уровне API (в валидаторах).

---

## Автор
Telegram @eslobodyanik