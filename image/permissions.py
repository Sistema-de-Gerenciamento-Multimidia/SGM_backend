from rest_framework.permissions import BasePermission


class IsUserOrAdmin(BasePermission):
    
    def has_permission(self, request, view):
        """Verifica se o usuário está autenticado"""
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        """Permite acesso se o usuário for o próprio ou um admin"""
        return bool(request.user == obj.user or request.user.is_staff)
