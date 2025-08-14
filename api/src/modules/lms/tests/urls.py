from django.urls import path, include
from rest_framework.routers import DefaultRouter
from src.modules.lms.views import LmsStatsViewSet, UserBadgesView

router = DefaultRouter()
router.register(r'stats', LmsStatsViewSet, basename='lms-stats')

urlpatterns = [
    path('api/lms/badges/', UserBadgesView.as_view()),
    path('api/lms/', include(router.urls)),
]
