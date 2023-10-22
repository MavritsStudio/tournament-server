from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsPersonalOrReadOnlyPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return (
            request.user
            and request.user.is_authenticated
            and obj == request.user
        )


class IsTeamMateOrReadOnlyPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return (
            request.user
            and request.user.is_authenticated
            and request.user in obj.mates
        )

