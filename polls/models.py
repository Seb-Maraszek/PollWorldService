import datetime
from django.db import models
from collections import Counter
# Create your models here.
from django.contrib.auth.models import User
from django.utils.timezone import now

from accounts.models import Account


class Poll(models.Model):
    """Model for single poll, that stores basic information about poll such as description, category etc.
      price, time_needed and assigned_users are filled automatically after adding questions related with
      instance.
     'user' is a company user that owns poll"""
    class Category(models.TextChoices):
        SPORT = "SPORT",
        POLITICS = "POLITICS",
        LIFE_STYLE = "LIFE_STYLE",
        BUSINESS = "BUSINESS",

    user = models.ForeignKey(User, related_name='polls', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)
    category = models.CharField(choices=Category.choices, max_length=100)
    short_description = models.TextField(max_length=100)
    description = models.TextField(max_length=500)
    time_needed = models.DurationField(default=datetime.timedelta(seconds=10))
    rating = models.FloatField(default=3)
    assigned_users = models.ManyToManyField(User, related_name='assigned_polls', through='PollAssignment')


class PollAssignment(models.Model):
    """Assignment model that maps user with poll and stores time of assignment and completion"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    assigned_date = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateTimeField(null=True)

    class Meta:
        unique_together = ("user", "poll")

    def complete(self):
        """Method used after user correctly fills given poll, that sets completion time."""
        self.completed_date = now()
        self.save()


class Question(models.Model):
    """Model for single question for poll"""
    QUESTION_TYPES = [
        ('SINGLE', 'single_choice'),
        ('MULTI', 'multi_choice'),
        ('TEXT', 'text')
    ]
    poll = models.ForeignKey(Poll, related_name='questions', on_delete=models.CASCADE)
    type = models.TextField(choices=QUESTION_TYPES)
    name = models.TextField(max_length=500)
    required = models.BooleanField(default=True)

    def question_time_and_price(self):
        """Method that returns points and time needed for question each type. It is used to calculate
        whole poll points and time needed."""
        if self.type == 'SINGLE':
            return {"seconds": datetime.timedelta(seconds=15), "points": 10}
        elif self.type == 'MULTI':
            return {"seconds": datetime.timedelta(seconds=30), "points": 20}
        elif self.type == 'TEXT':
            return {"seconds": datetime.timedelta(seconds=60), "points": 30}

    def generate_options_from_names(self, options):
        """Helper method that allows us to generate options for closed question from list of strings"""
        for option in options:
            QuestionOption.objects.create(name=option, question=self)
        self.save()


class Answer(models.Model):
    """Model for answer to single question"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE, null=True)
    text_answer = models.TextField(max_length=500, null=True)

    def set_options(self, options):
        """Helper method that sets answer options for closed question from list of IDs."""
        optionSet = QuestionOption.objects.filter(id__in=options)
        self.questionoption_set.set(optionSet)
        self.save()


class QuestionOption(models.Model):
    """Model for single option for closed question"""
    name = models.CharField(max_length=100)
    question = models.ForeignKey(Question, null=True, on_delete=models.CASCADE)
    answer = models.ManyToManyField(Answer)

    @property
    def popularity(self):
        """Return in how many answers is this QuestionOption used"""
        return self.answer.all().count()
