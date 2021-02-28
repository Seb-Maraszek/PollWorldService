from django.contrib.auth.models import User
from django.shortcuts import render, get_list_or_404, get_object_or_404

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_402_PAYMENT_REQUIRED

from accounts.models import Account
from coupons.models import Coupon
from coupons.serializers import ownedCouponSerializer, toBuyCouponSerializer
from polls.permissions import IsAuthenticatedUser


class CouponsViewSet(viewsets.GenericViewSet):
    """Buy and retrieve coupons for logged user"""
    permission_classes = [IsAuthenticatedUser]
    queryset = None

    def get_queryset(self):
        if self.kwargs:
            return get_object_or_404(Coupon.objects.filter(user_id=self.request.user.id, id=int(self.kwargs['pk'])))
        if 'owned' in str(self.request):
            return get_list_or_404(Coupon.objects.filter(user_id=-self.request.user.id, is_unlocked=True))
        else:
            return get_list_or_404(Coupon.objects.filter(user_id=self.request.user.id, is_unlocked=False))

    @action(detail=False, methods=['get'])
    def owned(self, request):
        """Get list of owned coupons for current user"""
        coupons = self.get_queryset()
        serializer = ownedCouponSerializer(coupons, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def buy(self, request, pk=None):
        """Check if user has points, and if coupon is available, then buy coupon"""
        coupon = self.get_queryset()
        if coupon.is_unlocked:
            return Response("This coupon is already bought", status=HTTP_400_BAD_REQUEST)
        else:
            if Account.objects.get(user=coupon.user).points < coupon.price:
                return Response("Not enough points to buy this coupon!", status=HTTP_402_PAYMENT_REQUIRED)
            coupon.unlock()
            serializer = ownedCouponSerializer(coupon)
            return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def tobuy(self, request):
        """""Get list of coupons available to buy for current user"""
        coupons = self.get_queryset()
        serializer = toBuyCouponSerializer(coupons, many=True)
        return Response(serializer.data)
