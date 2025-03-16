from django.urls import path

from ads.apps import AdsConfig
from ads.views import AdListAPIView, AdCreateAPIView, AdRetrieveAPIView, AdUpdateAPIView, AdDestroyAPIView

app_name = AdsConfig.name

urlpatterns = [
    path("", AdListAPIView.as_view(), name="ads-list"),
    path("create/", AdCreateAPIView.as_view(), name="ads-create"),
    path("<int:pk>/", AdRetrieveAPIView.as_view(), name="ads-retrieve"),
    path(
        "update/<int:pk>/", AdUpdateAPIView.as_view(), name="ads-update"
    ),
    path(
        "delete/<int:pk>/",
        AdDestroyAPIView.as_view(),
        name="ads-delete",
    ),
]
