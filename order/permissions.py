from rest_framework import permissions


class OrderPermissions(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'client') and request.user.client == obj.client:
            return True
        elif hasattr(request.user, 'supplier') and request.user.supplier == obj.supplier:
            return True
        return False


class LineItemPermissions(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'client') and request.user.client == obj.order.client:
            return True
        elif hasattr(request.user, 'supplier') and request.user.supplier == obj.order.supplier:
            return True
        return False