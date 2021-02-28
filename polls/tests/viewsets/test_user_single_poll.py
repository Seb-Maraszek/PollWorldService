from django.contrib.auth.models import User
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

from polls.models import Poll, PollAssignment, Question, QuestionOption
from polls.tests.viewsets.testing_data import incorrect_answer_first, incorrect_answer_second, correct_answer, \
    get_model_fields
from polls.views import UserSinglePollViewSet


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
        view = UserSinglePollViewSet.as_view({'get': 'retrieve'})
        api_request = factory.get('')
        force_authenticate(api_request, user=self.user)
        response = view(api_request, pk=self.poll.id)

        self.assertEqual(list(response.data), get_model_fields(self.poll))
        self.assertEqual(response.data['id'], self.poll.id)
        self.assertIsInstance(response.data, ReturnDict)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_not_found(self):
        factory = APIRequestFactory()
        view = UserSinglePollViewSet.as_view({'get': 'retrieve'})
        api_request = factory.get('')
        force_authenticate(api_request, user=self.user)
        response = view(api_request, pk=self.poll.id + 1)

        self.assertEqual(response.status_code, 404)

    def test_retrieve_fake_user(self):
        fake_user = User.objects.create_superuser("fake", "fake@wp.pl", "fake")
        fake_assignment = PollAssignment.objects.get(user=fake_user, poll_id=self.poll.id)
        fake_assignment.delete()

        factory = APIRequestFactory()
        view = UserSinglePollViewSet.as_view({'get': 'retrieve'})
        api_request = factory.get('')
        force_authenticate(api_request, user=fake_user)
        response = view(api_request, pk=self.poll.id)

        self.assertIsNotNone(PollAssignment.objects.get(user=self.user, poll_id=self.poll.id))
        self.assertIsInstance(response.data['detail'], ErrorDetail)
        self.assertEqual(response.status_code, 404)

    def test_questions(self):
        factory = APIRequestFactory()
        view = UserSinglePollViewSet.as_view({'get': 'questions'})
        api_request = factory.get('')
        force_authenticate(api_request, user=self.user)
        response = view(api_request, pk=self.poll.id)

        self.assertIsInstance(response.data, ReturnList)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.status_code, 200)

    def test_questions_single(self):
        self.single_option_question.delete()
        self.multi_option_question.delete()

        factory = APIRequestFactory()
        view = UserSinglePollViewSet.as_view({'get': 'questions'})
        api_request = factory.get('')
        force_authenticate(api_request, user=self.user)
        response = view(api_request, pk=self.poll.id)

        self.assertIsInstance(response.data, ReturnList)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.status_code, 200)

    def test_questions_zero(self):
        self.single_option_question.delete()
        self.text_option_question.delete()
        self.multi_option_question.delete()

        factory = APIRequestFactory()
        view = UserSinglePollViewSet.as_view({'get': 'questions'})
        api_request = factory.get('')
        force_authenticate(api_request, user=self.user)
        response = view(api_request, pk=self.poll.id)

        self.assertIsInstance(response.data, ReturnList)
        self.assertEqual(len(response.data), 0)
        self.assertEqual(response.status_code, 200)

    def test_answer(self):
        factory = APIRequestFactory()
        view = UserSinglePollViewSet.as_view({'post': 'answer'})
        api_request = factory.post('/answer/', correct_answer(question_id=self.single_option_question.id,
                                                              option_ids=[self.first_option.id]), format='json')
        force_authenticate(api_request, user=self.user)
        response = view(api_request, pk=self.poll.id)
        self.assertEqual(response.status_code, 200)

    def test_answer_wrong_data(self):
        self.text_option_question.delete()
        factory = APIRequestFactory()
        view = UserSinglePollViewSet.as_view({'post': 'answer'})
        api_request = factory.post('/answer/', incorrect_answer_first(question_id=self.single_option_question.id,
                                                                      option_ids=[self.first_option.id]), format='json')
        force_authenticate(api_request, user=self.user)
        response = view(api_request, pk=self.poll.id)
        self.assertEqual(response.status_code, 400)

        api_request = factory.post('/answer/', incorrect_answer_second(question_id=self.single_option_question.id,
                                                                       option_ids=[self.first_option.id]), format='json')
        force_authenticate(api_request, user=self.user)
        response = view(api_request, pk=self.poll.id)
        self.assertEqual(response.status_code, 400)

    def test_multiple_answers_to_single_field(self):
        factory = APIRequestFactory()
        view = UserSinglePollViewSet.as_view({'post': 'answer'})
        api_request = factory.post('/answer/', incorrect_answer_first(question_id=self.single_option_question.id,
                                                                      option_ids=[self.first_option.id, self.second_option.id]), format='json')
        force_authenticate(api_request, user=self.user)
        response = view(api_request, pk=self.poll.id)
        self.assertEqual(response.status_code, 400)

    def test_answers_to_text_field(self):
        factory = APIRequestFactory()
        view = UserSinglePollViewSet.as_view({'post': 'answer'})
        api_request = factory.post('/answer/', incorrect_answer_first(question_id=self.text_option_question.id,
                                                                      option_ids=[self.first_option.id, self.second_option.id]), format='json')
        force_authenticate(api_request, user=self.user)
        response = view(api_request, pk=self.poll.id)
        self.assertEqual(response.status_code, 400)

    def test_wrong_options(self):
        factory = APIRequestFactory()
        view = UserSinglePollViewSet.as_view({'post': 'answer'})
        api_request = factory.post('/answer/', incorrect_answer_first(question_id=self.single_option_question.id,
                                                                      option_ids=[self.first_option.id, self.second_option.id]), format='json')
        force_authenticate(api_request, user=self.user)
        response = view(api_request, pk=self.poll.id)
        self.assertEqual(response.status_code, 400)

    def test_missing_required(self):
        factory = APIRequestFactory()
        view = UserSinglePollViewSet.as_view({'post': 'answer'})
        api_request = factory.post('/answer/', incorrect_answer_first(question_id=self.multi_option_question.id,
                                                                      option_ids=[self.fifth_option.id]), format='json')
        force_authenticate(api_request, user=self.user)
        response = view(api_request, pk=self.poll.id)

        self.assertEqual(response.status_code, 400)
        self.assertIn('required', str(response.data))
