from rest_framework.permissions import BasePermission


class HasRole(BasePermission):
    allowed_roles: set[str] = set()

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return getattr(user, "role", None) in self.allowed_roles


class IsAdmin(HasRole):
    allowed_roles = {"admin"}


class IsProvider(HasRole):
    allowed_roles = {"provider"}


class IsClient(HasRole):
    allowed_roles = {"client"}
