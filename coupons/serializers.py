from rest_framework import serializers

from coupons.models import Coupon


class ownedCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        exclude = ['price', 'user', 'is_unlocked']


class toBuyCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        exclude = ['code', 'user', 'is_unlocked']
