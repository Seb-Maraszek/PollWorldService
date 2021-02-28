from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
# Create your views here.
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK

from accounts.models import Account
from polls.models import Poll, PollAssignment, Question
from polls.permissions import IsAuthenticatedUser, IsAuthenticatedCompany
from polls.serializers import pollSerializer, questionWithPollSerializer, questionWithOptionSerializer, \
    answerSerializer, \
    questionStatsSerializer


class UserPollsViewSet(viewsets.GenericViewSet):
    """Methods for User to operate on list of available polls"""
    permission_classes = [IsAuthenticatedUser]

    def get_queryset(self):
        return PollAssignment.objects.filter(user=self.request.user)

    def list(self, request):
        """List all polls for current user"""
        polls = [item.poll for item in self.get_queryset().filter(completed_date=None)]
        serializer = pollSerializer(polls, many=True)
        return Response(serializer.data)


class UserSinglePollViewSet(viewsets.GenericViewSet):
    """Methods for User to operate on a single Poll which ID is passed in request URL
     that is assigned to user."""
    permission_classes = [IsAuthenticatedUser]

    def get_queryset(self):
        return get_object_or_404(PollAssignment.objects.filter(user=self.request.user,
                                                               poll_id=int(self.kwargs['pk'])))

    def retrieve(self, request, pk=None):
        """Get basic information about a poll with given ID"""
        pollAssignment = self.get_queryset()
        poll = Poll.objects.get(id=pollAssignment.poll_id)
        serializer = pollSerializer(poll)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """Get questions for poll with given ID"""
        pollAssignment = self.get_queryset()
        poll = Poll.objects.get(id=pollAssignment.poll_id)
        questions = Question.objects.filter(poll=poll)
        serializer = questionWithOptionSerializer(questions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def answer(self, request, pk=None):
        """Post answers for poll with given ID"""
        pollAssignment = self.get_queryset()
        poll = Poll.objects.get(id=pollAssignment.poll_id)
        required_questions = list(Question.objects.filter(poll=poll, required=True))
        serializer = answerSerializer(data=request.data, many=True, context={"user": request.user})
        if serializer.is_valid():
            answers = serializer.save()
            for answer in answers:
                if answer.question in required_questions:
                    required_questions.remove(answer.question)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        if required_questions:
            return Response("Not all required questions were answered", status=HTTP_400_BAD_REQUEST)
        Account.objects.get(user=request.user).add_points(poll.price)
        pollAssignment.complete()
        return Response("Survey completed!", status=HTTP_200_OK)


class CompanyPollsViewSet(viewsets.GenericViewSet):
    """Methods for Company to operate on their polls"""
    permission_classes = [IsAuthenticatedCompany]

    def get_queryset(self):
        return get_list_or_404(Poll.objects.all(), user=self.request.user)

    def list(self, request):
        """Get all created by Company Polls"""
        polls = self.get_queryset()
        serializer = pollSerializer(polls, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Create new poll"""
        serializer = questionWithPollSerializer(data=request.data, context={"user": request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class CompanySinglePollViewSet(viewsets.GenericViewSet):
    """Methods for Company to operate on poll with given ID"""
    permission_classes = [IsAuthenticatedCompany]

    def get_queryset(self):
        return get_object_or_404(Poll.objects.all(), user=self.request.user, id=int(self.kwargs['pk']))

    def retrieve(self, request, pk=None):
        """Get basic information about Poll"""
        poll = self.get_queryset()
        serializer = pollSerializer(poll)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def answers_popularity(self, request, pk=None):
        """Get all questions and options for questions in that poll,
        with information how many times each option was selected in answer"""
        poll = self.get_queryset()
        question_list = Question.objects.filter(poll=poll)
        serializer = questionStatsSerializer(question_list, many=True)
        return Response(serializer.data)
