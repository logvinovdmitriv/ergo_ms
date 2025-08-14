from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet, TaskViewSet, TaskCommentViewSet, TimeLogViewSet, UserViewSet,
    ProjectStatusViewSet, ProjectPriorityViewSet, TaskStatusViewSet, TaskPriorityViewSet,
    OrganizationViewSet, OrganizationInviteViewSet, TeamViewSet, UploadFileView)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'task-comments', TaskCommentViewSet)
router.register(r'time-logs', TimeLogViewSet)
router.register(r'users', UserViewSet)

# Статусы и приоритеты
router.register(r'project-statuses', ProjectStatusViewSet)
router.register(r'project-priorities', ProjectPriorityViewSet)
router.register(r'task-statuses', TaskStatusViewSet)
router.register(r'task-priorities', TaskPriorityViewSet)
router.register(r'organizations', OrganizationViewSet)
router.register(r'invites', OrganizationInviteViewSet, basename='organization-invite')
router.register(r'teams', TeamViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Подключаем стратегические проекты по ожидаемому клиентом префиксу
    path('strategic-projects/', include('src.modules.crm.strategic_projects.urls')),
    # Отдельная точка загрузки файлов для фронтенда (без префикса tasks)
    path('upload-file/', UploadFileView.as_view()),
]