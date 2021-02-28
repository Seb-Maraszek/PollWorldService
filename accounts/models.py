from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    """
    Model account, used for storing data about user or company,
    auto created after registration process.
    """
    class LivingPlace(models.IntegerChoices):
        VILLAGE = 1
        TOWN = 2
        CITY = 3

    is_company = models.BooleanField(default=False)

    points = models.IntegerField(null=True, default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # personal
    name = models.CharField(max_length=50, null=True)
    age = models.IntegerField(null=True)
    sex = models.BooleanField(null=True)

    # details
    profession = models.CharField(max_length=50, null=True)
    place_of_residence = models.IntegerField(choices=LivingPlace.choices, null=True)

    # physical
    height = models.IntegerField(null=True)
    weight = models.IntegerField(null=True)
    fitness_level = models.IntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(5)])

    def make_user(self):
        self.is_company = False
        self.save()

    def make_company(self):
        self.is_company = True
        self.save()

    def add_points(self, value):
        self.points = self.points + value
        self.save()

    def subtract_points(self, value):
        self.points = self.points - value
        self.save()
