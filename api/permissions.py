from rest_framework import permissions
from talents.models import Talent
from jobs.models import Company


class IsTalentOrReadOnly(permissions.BasePermission):
    """
    Custom permission class that allows read-only access to any request,
    but only allows write access to the talent of the experience.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to access the object.

        Args:
            request (HttpRequest): The request being made.
            view (View): The view handling the request.
            obj (object): The object being accessed.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        if not isinstance(request.user, Talent):
            return False

        return obj.talent == request.user

class IsCompanyOrReadOnly(permissions.BasePermission):
    """
    Custom permission class that allows read-only access to all users,
    but write access only to the company that owns the object.
    """
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to access the object.

        Args:
            request (HttpRequest): The request object.
            view (View): The view object.
            obj (object): The object being accessed.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        if not isinstance(request.user, Company):
            return False
        
        # Write permissions are only allowed to the company of the job.
        return obj.company == request.user