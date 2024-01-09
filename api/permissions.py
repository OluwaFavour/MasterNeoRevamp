from rest_framework import permissions
from talents.models import Talent
from jobs.models import Company


class IsTalentOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        if not isinstance(request.user, Talent):
            return False
        # Write permissions are only allowed to the talent of the experience.
        return obj.talent == request.user

class IsCompanyOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not isinstance(request.user, Company):
            return False
        
        # Write permissions are only allowed to the company of the job.
        return obj.company == request.user