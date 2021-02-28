from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from coupons.models import Coupon
from .models import Account, Poll, PollAssignment, Question


@receiver(post_save, sender=Poll)
def auto_assign_to_all(sender, instance, created, **kwargs):
    """After poll is saved, assign it automatically to all users.
       Generate coupons for coupons to buy"""
    if created:
        for account in Account.objects.all():
            if not account.is_company:
                PollAssignment.objects.create(user=account.user, poll=instance)
                Coupon.objects.create(user=account.user).construct()


@receiver(post_save, sender=Question)
def update_poll_data(sender, instance, created, **kwargs):
    """After each Poll Question is saved, add time and points to its poll."""
    if created:
        poll = instance.poll
        poll.time_needed += instance.question_time_and_price()["seconds"]
        poll.price += instance.question_time_and_price()["points"]
        poll.save()
