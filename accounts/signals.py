from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from coupons.models import Coupon
from polls.models import Poll, PollAssignment
from .models import Account


@receiver(post_save, sender=User)
def create_account(sender, instance, created, **kwargs):
    """Create account after each correct registration"""
    if created:
        Account.objects.create(user=instance)


@receiver(post_save, sender=Account)
def assign_polls(sender, instance, created, **kwargs):
    """Auto assign polls from database to user that just created account"""
    if created:
        if not instance.is_company:
            for poll in Poll.objects.all():
                PollAssignment.objects.create(user=instance.user, poll=poll)
                Coupon.objects.create(user=instance.user).construct()
