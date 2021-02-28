"""PollWorldService URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from accounts.views import AccountViewSet
from coupons.views import CouponsViewSet
from polls.views import UserPollsViewSet, CompanyPollsViewSet, CompanySinglePollViewSet, UserSinglePollViewSet

router = routers.SimpleRouter()
router.register(r'accounts', AccountViewSet, basename='accounts')
router.register(r'company/polls', CompanyPollsViewSet, basename='company/polls')
router.register(r'company/poll', CompanySinglePollViewSet,  basename='company/poll')

router.register(r'user/polls', UserPollsViewSet, basename='user/polls')
router.register(r'user/poll', UserSinglePollViewSet,  basename='user/poll')
router.register(r'user/coupons', CouponsViewSet, basename='user/coupons')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]

urlpatterns += router.urls
