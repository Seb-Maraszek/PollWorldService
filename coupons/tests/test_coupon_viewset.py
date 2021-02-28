from django.contrib.auth.models import User
from rest_framework.status import HTTP_402_PAYMENT_REQUIRED, HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate
from rest_framework.utils.serializer_helpers import ReturnList

from accounts.models import Account
from coupons.models import Coupon
from coupons.views import CouponsViewSet


class CouponsViewSetTests(APITestCase):
    def setUp(self):
        self.username = 'tester'
        self.password = 'password'
        self.user = User.objects.create_superuser(self.username, 'test@example.com', self.password)
        self.fake_user = User.objects.create_superuser(self.username + 'f', 'test@example.com' + 'f',
                                                       self.password + 'f')
        self.account = Account.objects.get(user=self.user)
        self.coupon = Coupon.objects.create(user=self.user, price=10)

    def tearDown(self):
        self.user.delete()

    def test_owned(self):
        factory = APIRequestFactory()
        view = CouponsViewSet.as_view({'get': 'owned'})
        api_request = factory.get('')
        force_authenticate(api_request, user=self.user)
        response = view(api_request)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_buying(self):
        self.account.add_points(10)
        factory = APIRequestFactory()
        view = CouponsViewSet.as_view({'post': 'buy'})
        api_request = factory.post('')
        force_authenticate(api_request, user=self.user)
        response = view(api_request, pk=self.coupon.id)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_buying_without_points(self):
        self.account.points = self.coupon.price - 1
        factory = APIRequestFactory()
        view = CouponsViewSet.as_view({'post': 'buy'})
        api_request = factory.post('')
        force_authenticate(api_request, user=self.user)
        response = view(api_request, pk=self.coupon.id)
        self.assertEqual(response.status_code, HTTP_402_PAYMENT_REQUIRED)

    def test_buying_fail(self):
        factory = APIRequestFactory()
        self.coupon.unlock()
        view = CouponsViewSet.as_view({'post': 'buy'})
        api_request = factory.post('')
        force_authenticate(api_request, user=self.user)
        response = view(api_request, pk=self.coupon.id)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_coupons_to_buy(self):
        factory = APIRequestFactory()
        view = CouponsViewSet.as_view({'get': 'tobuy'})
        api_request = factory.get('')
        force_authenticate(api_request, user=self.user)
        response = view(api_request)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(type(response.data), ReturnList)

    def test_fake_user(self):
        factory = APIRequestFactory()
        api_request = factory.get('')
        force_authenticate(api_request, user=self.fake_user)

        view = CouponsViewSet.as_view({'get': 'owned'})
        response = view(api_request)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

        view = CouponsViewSet.as_view({'get': 'tobuy'})
        response = view(api_request)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

        api_request = factory.post('')
        force_authenticate(api_request, user=self.fake_user)
        view = CouponsViewSet.as_view({'post': 'buy'})
        response = view(api_request)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
