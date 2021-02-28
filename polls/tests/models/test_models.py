from unittest import TestCase

from django.contrib.auth.models import User
from django.utils.timezone import now
from rest_framework.test import APITestCase
import datetime

from polls.models import PollAssignment, Poll, Question, QuestionOption, Answer


class PollAssignmentModelTest(APITestCase):
    def setUp(self):
        self.username = 'test'
        self.password = 'pass'
        self.user = User.objects.create_superuser(self.username, 'testa@example.com', self.password)
        self.company = User.objects.create_superuser(self.username + 'f', 'testa@example.comf', self.password)
        self.poll = Poll.objects.create(user=self.company)

    def test_complete(self):
        pollAssignment = PollAssignment.objects.get(user=self.user, poll=self.poll)
        self.assertEqual(pollAssignment.completed_date, None)
        pollAssignment.complete()
        difference = now() - pollAssignment.completed_date
        self.assertAlmostEqual(difference.seconds, 0)


class QuestionModelTest(APITestCase):
    def setUp(self):
        self.username = 'test'
        self.password = 'pass'
        self.user = User.objects.create_superuser(self.username, 'testa@example.com', self.password)
        self.company = User.objects.create_superuser(self.username + 'f', 'testa@example.comf', self.password)
        self.poll = Poll.objects.create(user=self.company)
        self.question = Question.objects.create(poll=self.poll, required=False, name="Name", type='SINGLE')

    def test_time_and_price(self):
        self.question.type = "SINGLE"
        self.assertEqual(self.question.question_time_and_price()['seconds'], datetime.timedelta(seconds=15))
        self.assertEqual(self.question.question_time_and_price()['points'], 10)

        self.question.type = "MULTI"
        self.assertEqual(self.question.question_time_and_price()['seconds'], datetime.timedelta(seconds=30))
        self.assertEqual(self.question.question_time_and_price()['points'], 20)

        self.question.type = "TEXT"
        self.assertEqual(self.question.question_time_and_price()['seconds'], datetime.timedelta(seconds=60))
        self.assertEqual(self.question.question_time_and_price()['points'], 30)

    def test_generate_options_from_names(self):
        options = ["Option", "Option2", "Option3"]
        self.question.generate_options_from_names(options)
        options_from_database = [option.name for option in QuestionOption.objects.filter(question=self.question)]
        self.assertEqual(options_from_database, options)


class AnswerModelTest(APITestCase):
    def setUp(self):
        self.username = 'test'
        self.password = 'pass'
        self.user = User.objects.create_superuser(self.username, 'testa@example.com', self.password)
        self.company = User.objects.create_superuser(self.username + 'f', 'testa@example.comf', self.password)
        self.poll = Poll.objects.create(user=self.company)
        self.question = Question.objects.create(poll=self.poll, required=False, name="Name", type='MULTI')
        self.question.generate_options_from_names(['Opcja1', 'Opcja2'])

    def test_set_options(self):
        answer = Answer.objects.create(user=self.user, question=self.question)
        options_ids = [option.id for option in QuestionOption.objects.filter(question=self.question)]
        answer.set_options(options_ids)

        self.assertTrue(
            {'answer': answer.id} in QuestionOption.objects.filter(question=self.question, id__in=options_ids).values(
                'answer'))
