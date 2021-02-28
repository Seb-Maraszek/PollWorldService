from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework.utils.serializer_helpers import ReturnList

from coupons.models import Coupon
from polls.models import Poll, PollAssignment
from polls.views import UserPollsViewSet


class UserPollViewSetTests(APITestCase):
    def setUp(self):
        self.username = 'tester'
        self.password = 'password'
        self.company = User.objects.create_superuser('company', 'test@example.com', 'company_pass')
        self.user = User.objects.create_superuser(self.username, 'test@example.com', self.password)
        self.poll = Poll.objects.create(user=self.company,
                                        name="poll",
                                        short_description="short",
                                        description="long")

        self.poll_second = Poll.objects.create(user=self.company,
                                               name="poll2",
                                               short_description="short2",
                                               description="long2")

    def perform_request(self):
        factory = APIRequestFactory()
        view = UserPollsViewSet.as_view({'get': 'list'})
        api_request = factory.get('')
        force_authenticate(api_request, user=self.user)
        return view(api_request)

    def test_list(self):
        response = self.perform_request()

        self.assertIsInstance(response.data, ReturnList)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.status_code, 200)

    def test_one_item(self):
        self.poll.delete()
        response = self.perform_request()
        self.assertIsInstance(response.data, ReturnList)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.status_code, 200)

    def test_no_items(self):
        self.poll.delete()
        self.poll_second.delete()
        response = self.perform_request()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
