import random
import string

from django.contrib.auth.models import User
from django.db import models

from accounts.models import Account


class Coupon(models.Model):
    """Model for Coupon, that stores data about both locked and unlocked Coupon."""

    COUPON_COMPANIES = [
        ('ALLEGRO', 'Allegro'),
        ('BONPRIX', 'bonprix'),
        ('ŻABKA', 'Żabka'),
        ('DECATHLON', 'decathlon'),
        ('SPOTIFY', 'spotify'),
        ('EOBUWIE', 'eobuwie'),
        ('SFD', 'sklep_sfd'),
        ('IKEA', 'ikea'),
        ('ZARA', 'zara')
    ]
    COUPON_DESCRIPTIONS = [
        ('% zniżki na cały asortyment', 25),
        ('% zniżki w czwartek', 20),
        ('% zniżki w środe', 20),
        ('% zniżki we wtorek', 20),
        ('% zniżki w weekend', 20),
        (' produkt gratis', 100),
        (' złotych na karcie podarunkowej', 25)
    ]
    is_unlocked = models.BooleanField(default=False)
    user = models.ForeignKey(User, related_name="coupons", on_delete=models.CASCADE)
    price = models.IntegerField(default=0)
    code = models.CharField(max_length=10)
    company = models.CharField(choices=COUPON_COMPANIES, max_length=20)
    description = models.CharField(max_length=50)

    def unlock(self):
        """Unlock coupon for user, subtract points from his account"""
        account = Account.objects.get(user_id=self.user_id)
        account.subtract_points(self.price)
        self.is_unlocked = True
        self.save()

    def construct(self):
        """Generate coupon with random but reasonable data"""
        description = random.randint(0, len(self.COUPON_DESCRIPTIONS) - 1)
        company = random.randint(0, len(self.COUPON_COMPANIES) - 1)
        self.company = self.COUPON_COMPANIES[company][0]
        self.price = random.randint(100, 300)
        self.description = ''.join(str(self.price // self.COUPON_DESCRIPTIONS[description][1])) + (
            str(self.COUPON_DESCRIPTIONS[description][0]))
        self.code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        self.save()
