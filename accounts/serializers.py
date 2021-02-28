from rest_framework import serializers
from .models import Account
from .variables import fields_company, fields_user


class accountUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = fields_user
        read_only_fields = ['user_id', 'points', 'id']


class accountCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = fields_company
