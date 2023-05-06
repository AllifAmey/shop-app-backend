from rest_framework import permissions


class UpdateOwnCart(permissions.BasePermission):
    """Allow user to edit their own cart"""

    def has_permission(self, request, view):
        """Check if the user if authenticated for the request"""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check has permissions for manipulating their cart."""
        if request.method in permissions.SAFE_METHODS:
            return obj.user == request.user
        return obj.user == request.user


class UpdateOwnOrder(permissions.BasePermission):
    """Allow user to edit their order unless """

    def has_permission(self, request, view):
        """Check if the user if authenticated for the request"""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check has permissions for manipulating their order."""
        if request.method in permissions.SAFE_METHODS:
            """If user is staff then by default allow them to change order"""
            if request.user.is_staff:
                return True
            else:
                return obj.user == request.user
        if request.user.is_staff:
            return True
        else:
            return obj.user == request.user
