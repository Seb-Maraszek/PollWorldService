from django.contrib.auth.models import User
from rest_framework.status import HTTP_200_OK
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from accounts.models import Account
from accounts.tests.testing_data import correct_company
from accounts.views import AccountViewSet
from accounts.variables import fields_company, fields_user


class AccountViewSetTest(APITestCase):
    def setUp(self):
        self.username = 'tester'
        self.password = 'password'
        self.user = User.objects.create_superuser(self.username, 'test@example.com', self.password)
        self.account = Account.objects.get(user=self.user)

    def test_account(self):
        factory = APIRequestFactory()
        view = AccountViewSet.as_view({'get': 'account'})
        api_request = factory.get('')
        force_authenticate(api_request, user=self.user)
        response = view(api_request)
        self.assertEqual(self.account.id, response.data['id'])
        self.assertEqual(list(response.data.keys()), fields_user)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_account_company(self):
        self.account.is_company = True
        self.account.save()
        factory = APIRequestFactory()
        view = AccountViewSet.as_view({'get': 'account'})
        api_request = factory.get('')
        force_authenticate(api_request, user=self.user)
        response = view(api_request)
        self.assertEqual(list(response.data.keys()), fields_company)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_company(self):
        factory = APIRequestFactory()
        view = AccountViewSet.as_view({'post': 'company'})
        api_request = factory.post('/account/company/', data=correct_company, format='json')
        force_authenticate(api_request, user=self.user)
        response = view(api_request)
        company_account = Account.objects.get(user=self.user)
        self.assertEqual(company_account.is_company, True)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_user(self):
        factory = APIRequestFactory()
        view = AccountViewSet.as_view({'post': 'user'})
        api_request = factory.post('/account/user/', data=correct_company, format='json')
        force_authenticate(api_request, user=self.user)
        response = view(api_request)
        company_account = Account.objects.get(user=self.user)
        self.assertEqual(company_account.is_company, False)
        self.assertEqual(response.status_code, HTTP_200_OK)
