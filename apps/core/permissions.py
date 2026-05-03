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


class IsAdminOrAuthenticatedReadOnly(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if getattr(user, "role", None) == "admin":
            return True

        return request.method in ("GET", "HEAD", "OPTIONS")


class AvailabilitySlotAccess(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        role = getattr(user, "role", None)
        if role == "admin":
            return True
        if role == "provider":
            return request.method in ("GET", "HEAD", "OPTIONS", "POST", "PUT", "PATCH", "DELETE")
        return request.method in ("GET", "HEAD", "OPTIONS")

    def has_object_permission(self, request, view, obj):
        user = request.user
        role = getattr(user, "role", None)
        if role == "admin":
            return True

        provider = getattr(obj, "provider", None)
        if role == "provider" and provider and provider.user_id == user.id:
            return True

        return request.method in ("GET", "HEAD", "OPTIONS")


class BookingRoleAccess(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        role = getattr(user, "role", None)
        if role == "admin":
            return True
        if role == "provider":
            if request.method == "POST" and getattr(view, "action", None) == "cancel":
                return True
            return request.method in ("GET", "HEAD", "OPTIONS")
        if role == "client":
            if request.method == "POST" and getattr(view, "action", None) == "cancel":
                return True
            return request.method in ("GET", "HEAD", "OPTIONS", "POST")
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        role = getattr(user, "role", None)
        if role == "admin":
            return True

        action = getattr(view, "action", None)
        if action == "cancel" and request.method == "POST":
            if role == "provider" and getattr(obj, "provider", None) and obj.provider.user_id == user.id:
                return True
            if role == "client" and getattr(obj, "client_id", None) == user.id:
                return True
            return False

        if role == "provider" and getattr(obj, "provider", None) and obj.provider.user_id == user.id:
            return request.method in ("GET", "HEAD", "OPTIONS")
        if role == "client" and getattr(obj, "client_id", None) == user.id:
            return request.method in ("GET", "HEAD", "OPTIONS")
        return False
