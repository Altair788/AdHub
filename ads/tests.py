import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ads.models import Ad
from users.models import User


# Create your tests here.
class AdTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass", is_active=True
        )
        # Аутентифицируем клиент
        self.client.force_authenticate(user=self.user)

    def test_create_ad(self):
        """
        Тестирование создания объявления
        """
        data = {"title": "book", "price": 1200}

        url = reverse("ads:ads-create")

        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

        # 1 гипотеза
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 2 гипотеза
        response_data = response.json()
        self.assertEqual(response_data["id"], 1)
        self.assertEqual(response_data["title"], "book")
        self.assertEqual(response_data["price"], 1200)
        self.assertEqual(response_data["description"], "")
        self.assertEqual(response_data["author"], self.user.id)
        self.assertIsNone(response_data["image"])
        self.assertIn("createdAt", response_data)

        # 3 гипотеза - тест на то, что объект сохранен в БД
        ad = Ad.objects.get(title="book")
        self.assertEqual(ad.price, 1200)
        self.assertEqual(ad.author, self.user)

    def test_list_ad(self):
        """
        Тестирование вывода списка объявлений.
        """

        Ad.objects.create(title="yacht", price=650000, author=self.user)

        Ad.objects.create(title="car", price=250000, author=self.user)

        url = reverse("ads:ads-list")
        response = self.client.get(url)

        # 1 гипотеза
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2 гипотеза (структура ответа)
        response_data = response.json()

        # Проверяем количество объявлений в списке
        self.assertEqual(response_data["count"], 2)
        self.assertEqual(len(response_data["results"]), 2)

        # Проверяем содержимое первого объявления (чем новее тем выше, согласно ТЗ)
        self.assertEqual(response_data["results"][0]["title"], "car")
        self.assertEqual(response_data["results"][0]["price"], 250000)
        self.assertEqual(response_data["results"][0]["author"], self.user.id)

        # Проверяем содержимое второго объявления
        self.assertEqual(response_data["results"][1]["title"], "yacht")
        self.assertEqual(response_data["results"][1]["price"], 650000)
        self.assertEqual(response_data["results"][1]["author"], self.user.id)

    def test_retrieve_ad(self):
        """
        Тестирование просмотра 1 объявления
        """
        ad1 = Ad.objects.create(title="moto", price=120000, author=self.user)

        url = reverse("ads:ads-retrieve", kwargs={"pk": ad1.pk})

        response = self.client.get(url)

        # 1 гипотеза
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2 гипотеза (структура ответа)
        response_data = response.json()
        self.assertEqual(response_data["id"], ad1.id)
        self.assertEqual(response_data["title"], "moto")
        self.assertEqual(response_data["price"], 120000)
        self.assertEqual(response_data["author"], self.user.id)

    def test_retrieve_nonexistent_ad(self):
        """
        Тестирование попытки просмотра несуществующего объявления
        """
        url = reverse("ads:ads-retrieve", kwargs={"pk": 9999})
        response = self.client.get(url)

        # 1 гипотеза
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_ad(self):
        ad1 = Ad.objects.create(title="moto", price=120000, author=self.user)

        url = reverse("ads:ads-update", kwargs={"pk": ad1.pk})

        data = {"title": "car"}

        response = self.client.patch(
            url, data=json.dumps(data), content_type="application/json"
        )

        # 1 гипотеза
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2 гипотеза - проверка, что данные действительно обновились
        ad1.refresh_from_db()
        self.assertEqual(ad1.title, "car")

        # 3 гипотеза - проверка содержимого ответа (цена должна остаться прежней)
        response_data = response.json()
        self.assertEqual(response_data["title"], "car")
        self.assertEqual(response_data["price"], 120000)

    def test_put_ad(self):
        ad1 = Ad.objects.create(
            title="moto", price=120000, author=self.user, description="Old description"
        )

        url = reverse("ads:ads-update", kwargs={"pk": ad1.pk})

        data = {"title": "car", "price": 90000, "description": "New description"}

        response = self.client.put(
            url, data=json.dumps(data), content_type="application/json"
        )

        # 1 гипотеза
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2 гипотеза - проверка, что данные действительно обновились
        ad1.refresh_from_db()
        self.assertEqual(ad1.title, "car")
        self.assertEqual(ad1.price, 90000)
        self.assertEqual(ad1.description, "New description")

        # 3 гипотеза - проверка содержимого ответа (цена должна остаться прежней)
        response_data = response.json()
        self.assertEqual(response_data["title"], "car")
        self.assertEqual(response_data["price"], 90000)
        self.assertEqual(response_data["description"], "New description")

        # 4 гипотеза - проверка, что автор не изменился
        self.assertEqual(ad1.author, self.user)
        self.assertEqual(response_data["author"], self.user.id)

    def test_delete_ad(self):
        """
        Тестирование удаления объявления.
        """
        # Создаем объявление
        ad = Ad.objects.create(title="moto", price=120000, author=self.user)

        # Убедимся, что объявление существует в базе данных
        self.assertTrue(Ad.objects.filter(id=ad.id).exists())

        # URL для удаления объявления
        url = reverse("ads:ads-delete", kwargs={"pk": ad.pk})

        # Отправляем DELETE-запрос
        response = self.client.delete(url)

        # Проверяем статус ответа
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Проверяем, что объявление больше не существует в базе данных
        self.assertFalse(Ad.objects.filter(id=ad.id).exists())

    def test_filter_ads_by_title(self):
        """
        Проверяет фильтрацию объявлений по названию.
        """
        # Создаем несколько объявлений
        Ad.objects.create(
            title="Ноутбук Apple MacBook Pro", price=150000, author=self.user
        )
        Ad.objects.create(
            title="Смартфон Samsung Galaxy S21", price=80000, author=self.user
        )
        Ad.objects.create(
            title="Наушники Sony WH-1000XM4", price=25000, author=self.user
        )

        # Проверяем, что объявления созданы
        # ads = Ad.objects.all()
        # print("Объявления в базе:", ads)

        # Фильтруем объявления по ключевому слову "ноутбук"
        url = reverse("ads:ads-list")
        # регистронезависимый поиск
        response = self.client.get(url, {"title": "ноутбук"})

        # # Выводим ответ для отладки
        # print("Ответ фильтрации:", response.json())

        # 1 гипотеза
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2 гипотеза (структура ответа)
        response_data = response.json()
        # print(response_data)

        # Проверяем количество найденных объявлений
        self.assertEqual(response_data["count"], 1)
        self.assertEqual(len(response_data["results"]), 1)

        # Проверяем содержимое найденного объявления
        self.assertEqual(
            response_data["results"][0]["title"], "Ноутбук Apple MacBook Pro"
        )
        self.assertEqual(response_data["results"][0]["price"], 150000)
        self.assertEqual(response_data["results"][0]["author"], self.user.id)

        # Фильтруем объявления по ключевому слову "Samsung"
        response = self.client.get(url, {"title": "Samsung"})

        # 3 гипотеза
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 4 гипотеза (структура ответа)
        response_data = response.json()

        # Проверяем количество найденных объявлений
        self.assertEqual(response_data["count"], 1)
        self.assertEqual(len(response_data["results"]), 1)

        # Проверяем содержимое найденного объявления
        self.assertEqual(
            response_data["results"][0]["title"], "Смартфон Samsung Galaxy S21"
        )
        self.assertEqual(response_data["results"][0]["price"], 80000)
        self.assertEqual(response_data["results"][0]["author"], self.user.id)

        # Фильтруем объявления по ключевому слову, которого нет в названиях
        response = self.client.get(url, {"title": "несуществующий"})

        # 5 гипотеза
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 6 гипотеза (структура ответа)
        response_data = response.json()

        # Проверяем, что объявления не найдены
        self.assertEqual(response_data["count"], 0)
        self.assertEqual(len(response_data["results"]), 0)
