from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from accounts.models import Account


class AccountModelTest(APITestCase):
    def setUp(self):
        self.username = 'test'
        self.password = 'pass'
        self.user = User.objects.create_superuser(self.username, 'testa@example.com', self.password)
        self.account = Account.objects.get(user=self.user)

    def test_add_points(self):
        self.account.add_points(210)
        self.assertEqual(self.account.points, 210)
