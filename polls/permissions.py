from rest_framework.permissions import BasePermission

from accounts.models import Account


class IsAuthenticatedCompany(BasePermission):
    def has_permission(self, request, view):
        if bool(request.user and request.user.is_authenticated):
            if Account.objects.get(user_id=request.user.id).is_company:
                return True
        return False


class IsAuthenticatedUser(BasePermission):
    def has_permission(self, request, view):
        if bool(request.user and request.user.is_authenticated):
            if not Account.objects.get(user_id=request.user.id).is_company:
                return True
        return False


class IsSurveyOwner(BasePermission):
    def has_permission(self, request, view):
        if bool(request.user and request.user.is_authenticated):
            if Account.objects.get(user_id=request.user.id).is_company:
                return True
        return False
