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

    
        

    
    