from rest_framework import permissions

"""
class UpdateOwnCart(permissions.BasePermission):
	\"""Allow user to edit their own profile\"""
    def has_permission(self, request, view):
        pass

	def has_object_permission(self, request, view, obj):
		\"""Check user is trying to edit their own profile\"""
		# SAFE_METHODS  = get methods as you are only reading an object,
		# not editting it. 
		# override this shit in the shop app and return False for users checking other users.
		if request.method in permissions.SAFE_METHODS:
			# if obj.id != request.user.id:
			# 	return False
			# the above logic for shop app so those asshole hackers cant steal other people's datas.
			return False

		# to understand the logic below:
		# 
		return False
"""
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
    
	
    
        

    
    