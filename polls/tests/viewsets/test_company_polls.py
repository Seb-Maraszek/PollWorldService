from django.contrib.auth.models import User
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from accounts.models import Account
from polls.models import Poll, Question, QuestionOption, PollAssignment
from polls.tests.viewsets.testing_data import mock_survey, mock_survey_incorrect_fields, \
    mock_survey_incorrect_options_single, mock_survey_incorrect_options_text
from polls.views import CompanyPollsViewSet


class CompanyPollsViewSetTest(APITestCase):
    def setUp(self):
        self.username = 'tester'
        self.password = 'password'
        self.company = User.objects.create_superuser('company', 'test@example.com', 'company_pass')
        Account.objects.filter(user=self.company).update(is_company=True)
        self.user = User.objects.create_superuser(self.username, 'test@example.com', self.password)

        self.poll = Poll.objects.create(user=self.company,
                                        name="poll",
                                        short_description="short",
                                        description="long")

    def test_list(self):
        factory = APIRequestFactory()
        view = CompanyPollsViewSet.as_view({'get': 'list'})
        api_request = factory.get('')
        force_authenticate(api_request, user=self.company)
        response = view(api_request)

        self.assertEqual(response.data[0]['user'], self.company.username)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_list_wrong_user(self):
        factory = APIRequestFactory()
        view = CompanyPollsViewSet.as_view({'get': 'list'})
        api_request = factory.get('')
        force_authenticate(api_request, user=self.user)
        response = view(api_request)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_create(self):
        user_polls_size_before = len(Poll.objects.filter(user=self.company))
        factory = APIRequestFactory()
        view = CompanyPollsViewSet.as_view({'post': 'create'})
        api_request = factory.post('/create/', mock_survey, format='json')
        force_authenticate(api_request, user=self.company)
        response = view(api_request)
        user_polls_size_now = len(Poll.objects.filter(user=self.company))

        self.assertEqual(user_polls_size_before + 1, user_polls_size_now)
        self.assertEqual(PollAssignment.objects.last().poll.name, response.data['name'])
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_create_incorrect_fields(self):
        user_polls_size_before = len(Poll.objects.filter(user=self.company))
        factory = APIRequestFactory()
        view = CompanyPollsViewSet.as_view({'post': 'create'})
        api_request = factory.post('/create/', mock_survey_incorrect_fields, format='json')
        force_authenticate(api_request, user=self.company)
        response = view(api_request)
        user_polls_size_now = len(Poll.objects.filter(user=self.company))

        self.assertEqual(user_polls_size_before, user_polls_size_now)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_create_incorrect_options(self):
        user_polls_size_before = len(Poll.objects.filter(user=self.company))
        factory = APIRequestFactory()
        view = CompanyPollsViewSet.as_view({'post': 'create'})
        api_request = factory.post('/create/', mock_survey_incorrect_options_single, format='json')
        force_authenticate(api_request, user=self.company)
        response = view(api_request)
        user_polls_size_now = len(Poll.objects.filter(user=self.company))
        self.assertEqual(user_polls_size_before, user_polls_size_now)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        user_polls_size_before = len(Poll.objects.filter(user=self.company))
        factory = APIRequestFactory()
        view = CompanyPollsViewSet.as_view({'post': 'create'})
        api_request = factory.post('/create/', mock_survey_incorrect_options_text, format='json')
        force_authenticate(api_request, user=self.company)
        response = view(api_request)
        user_polls_size_now = len(Poll.objects.filter(user=self.company))
        self.assertEqual(user_polls_size_before, user_polls_size_now)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)


