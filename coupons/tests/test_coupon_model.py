from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from coupons.models import Coupon


class CouponModelTest(APITestCase):
    def setUp(self):
        self.username = 'test'
        self.password = 'pass'
        self.user = User.objects.create_superuser(self.username, 'testa@example.com', self.password)

    def tearDown(self):
        self.user.delete()

    def test_construct(self):
        coupon = Coupon.objects.create(user=self.user)
        coupon.construct()
        self.assertIn(coupon.price, range(100, 301))
        self.assertIn(coupon.company, [x for x, _ in Coupon.COUPON_COMPANIES])
        self.assertEqual(len(coupon.code), 10)
        self.assertIn(coupon.description,
                      [str(coupon.price // value) + message for message, value in Coupon.COUPON_DESCRIPTIONS])

    def test_unlock(self):
        coupon = Coupon.objects.create(user=self.user)
        self.assertEqual(coupon.is_unlocked, False)
        coupon.unlock()
        self.assertEqual(coupon.is_unlocked, True)
