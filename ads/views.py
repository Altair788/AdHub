from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from ads.models import Ad
from ads.paginations import AdPaginator
from ads.serializers import AdSerializer
from users.permissions import IsAdmin, IsAuthor


class AdCreateAPIView(generics.CreateAPIView):
    serializer_class = AdSerializer
    queryset = Ad.objects.all()
    permission_classes = (IsAdmin | IsAuthenticated,)

    def perform_create(self, serializer):
        ad = serializer.save()
        ad.author = self.request.user
        ad.save()


class AdListAPIView(generics.ListAPIView):
    serializer_class = AdSerializer
    queryset = Ad.objects.all()
    pagination_class = AdPaginator
    permission_classes = ()


class AdRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = AdSerializer
    queryset = Ad.objects.all()
    permission_classes = (IsAuthenticated | IsAdmin,)


class AdUpdateAPIView(generics.UpdateAPIView):
    serializer_class = AdSerializer
    queryset = Ad.objects.all()
    permission_classes = (
        IsAuthenticated,
        IsAdmin | IsAuthor,
    )


class AdDestroyAPIView(generics.DestroyAPIView):
    serializer_class = AdSerializer
    queryset = Ad.objects.all()
    permission_classes = (
        IsAuthenticated,
        IsAdmin | IsAuthor,
    )
