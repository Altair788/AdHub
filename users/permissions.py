from rest_framework import permissions


class CanViewAPI(permissions.BasePermission):
    """
    Разрешение для просмотра API только администраторам.
    """

    def has_permission(self, request, view):
        return request.user.is_staff
