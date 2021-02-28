from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from accounts.models import Account
from accounts.serializers import accountUserSerializer, accountCompanySerializer


class AccountViewSet(viewsets.GenericViewSet):
    """
    Update and retrieve account data
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_object_or_404(Account.objects.all(), user=self.request.user)

    @action(detail=False, methods=['get'])
    def account(self, request):
        """Get account data for user/company from request"""
        account = self.get_queryset()
        if account.is_company:
            serializer = accountCompanySerializer(account)
        else:
            serializer = accountUserSerializer(account)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def company(self, request):
        """Add account data about company, switch account type to company"""
        serializer = accountCompanySerializer(self.get_queryset(), request.data)
        if serializer.is_valid():
            account = serializer.save()
            account.make_company()
            return Response(serializer.data)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def user(self, request):
        """Add account data for user, switch account type to user"""
        serializer = accountUserSerializer(self.get_queryset(), request.data)
        if serializer.is_valid():
            account = serializer.save()
            account.make_user()
            return Response(serializer.data)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
