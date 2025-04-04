from rest_framework.pagination import PageNumberPagination


class AdPaginator(PageNumberPagination):
    page_size = 4
    page_size_query_param = "page_size"
    max_page_size = 4
