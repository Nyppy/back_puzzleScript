from django.conf.urls import url

from rest_framework.routers import DefaultRouter

from . import views
from django.urls import re_path, include


router = DefaultRouter()
router.register('profile', views.ProfileViewSet)
router.register('file_manager', views.FileManagerViewSet)


urlpatterns = [
    re_path(r'^login/?$', views.LoginAPIView.as_view(), name='user_login'),
    re_path(r'^file/?$', views.FileView.as_view()),
    url(r'', include(router.urls)),
]
