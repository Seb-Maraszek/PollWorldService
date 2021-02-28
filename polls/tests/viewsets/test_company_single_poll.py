from random import random, randrange

from django.contrib.auth.models import User
from rest_framework.exceptions import ErrorDetail
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_200_OK
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework.utils.serializer_helpers import ReturnDict

from accounts.models import Account
from polls.models import Question, QuestionOption, Poll, PollAssignment, Answer
from polls.tests.viewsets.testing_data import get_model_fields
from polls.views import CompanySinglePollViewSet, UserSinglePollViewSet


class CompanySinglePollViewSetTest(APITestCase):
    def setUp(self):
        self.username = 'tester'
        self.password = 'password'
        self.company = User.objects.create_superuser('company', 'test@example.com', 'company_pass')
        self.user = User.objects.create_superuser(self.username, 'test@example.com', self.password)
        Account.objects.filter(user=self.company).update(is_company=True)

        self.poll = Poll.objects.create(user=self.company,
                                        name="poll",
                                        short_description="short",
                                        description="long")
        self.single_option_question = Question.objects.create(poll=self.poll, type='SINGLE')
        self.text_option_question = Question.objects.create(poll=self.poll, type='TEXT', required=False)
        self.multi_option_question = Question.objects.create(poll=self.poll, type='MULTI', required=False)

        self.first_option = QuestionOption.objects.create(question=self.single_option_question, name="Opcja1")
        self.second_option = QuestionOption.objects.create(question=self.single_option_question, name="Opcja2")
        self.third_option = QuestionOption.objects.create(question=self.single_option_question, name="Opcja3")

        self.forth_option = QuestionOption.objects.create(question=self.multi_option_question, name="Opcja4")
        self.fifth_option = QuestionOption.objects.create(question=self.multi_option_question, name="Opcja5")
        self.sixth_option = QuestionOption.objects.create(question=self.multi_option_question, name="Opcja6")

    def test_retrieve(self):
        factory = APIRequestFactory()
        view = CompanySinglePollViewSet.as_view({'get': 'retrieve'})
        api_request = factory.get('')
        force_authenticate(api_request, user=self.company)
        response = view(api_request, pk=self.poll.id)

        self.assertEqual(list(response.data), get_model_fields(self.poll))
        self.assertEqual(response.data['id'], self.poll.id)
        self.assertIsInstance(response.data, ReturnDict)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_retrieve_not_found(self):
        factory = APIRequestFactory()
        view = CompanySinglePollViewSet.as_view({'get': 'retrieve'})
        api_request = factory.get('')
        force_authenticate(api_request, user=self.company)
        response = view(api_request, pk=self.poll.id + 1)

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_retrieve_fake_user(self):
        Account.objects.filter(user=self.user).update(is_company=True)
        factory = APIRequestFactory()
        view = CompanySinglePollViewSet.as_view({'get': 'retrieve'})
        api_request = factory.get('')
        force_authenticate(api_request, user=self.user)
        response = view(api_request, pk=self.poll.id)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_answers_stats(self):
        first_option_appearances = randrange(50)
        second_option_appearances = randrange(50)
        for i in range(first_option_appearances):
            Answer.objects.create(user=self.user,
                                  question=self.single_option_question).set_options(options=[self.first_option.id])
        for i in range(second_option_appearances):
            Answer.objects.create(user=self.user,
                                  question=self.single_option_question).set_options(options=[self.second_option.id])

        factory = APIRequestFactory()
        view = CompanySinglePollViewSet.as_view({'get': 'answers_popularity'})
        api_request = factory.get('')
        force_authenticate(api_request, user=self.company)
        response = view(api_request, pk=self.poll.id)

        self.assertEqual(first_option_appearances, response.data[0]['options'][0]['popularity'])
        self.assertEqual(second_option_appearances, response.data[0]['options'][1]['popularity'])
