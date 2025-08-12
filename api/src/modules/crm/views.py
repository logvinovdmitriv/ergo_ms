from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from src.core.utils.mixins import SwaggerSafeMixin
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from src.modules.crm.models import (
    Project, ProjectMember, Task, TaskComment, TaskAttachment, TimeLog,
    ProjectStatus, ProjectPriority, TaskStatus, TaskPriority,
    Organization, OrganizationMember, OrganizationInvite,
    Team, TeamMember, TaskAssignee, TaskTree
)
from src.modules.crm.serializers import (
    ProjectSerializer, ProjectListSerializer, ProjectMemberSerializer,
    TaskSerializer, TaskListSerializer, TaskCalendarSerializer, TaskKanbanSerializer,
    TaskCommentSerializer, TaskAttachmentSerializer, TimeLogSerializer, CRMUserSerializer,
    ProjectStatusSerializer, ProjectPrioritySerializer, TaskStatusSerializer, TaskPrioritySerializer,
    OrganizationSerializer, OrganizationMemberSerializer, OrganizationInviteSerializer,
    TeamSerializer, TeamMemberSerializer
)
from src.modules.crm.permissions import TaskPermission, ProjectPermission, OrganizationPermission, TeamPermission


User = get_user_model()


class OrganizationViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    """ViewSet для управления организациями"""
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [OrganizationPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        user = self.get_safe_user() or self.request.user
        base_qs = Organization.objects.all() if user is None else Organization.objects.filter(
            Q(owner=user) | Q(memberships__user=user, memberships__status='accepted')
        ).distinct()
        return self.get_safe_queryset(base_qs)

    def perform_create(self, serializer):
        organization = serializer.save(owner=self.request.user)
        OrganizationMember.objects.create(
            organization=organization,
            user=self.request.user,
            role='owner',
            status='accepted',
            invited_by=self.request.user,
            invited_at=timezone.now(),
            responded_at=timezone.now()
        )

    def destroy(self, request, *args, **kwargs):
        organization = self.get_object()
        if organization.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        """Пригласить пользователя в организацию"""
        organization = self.get_object()
        # Проверяем права: только владелец или администратор
        if not (
            organization.owner == request.user or
            OrganizationMember.objects.filter(
                organization=organization,
                user=request.user,
                role__in=['owner', 'admin'],
                status='accepted'
            ).exists()
        ):
            return Response(status=status.HTTP_403_FORBIDDEN)

        email = request.data.get('email')
        role = request.data.get('role', organization.default_role)

        if not email:
            return Response({'error': 'email is required'}, status=status.HTTP_400_BAD_REQUEST)

        if role not in dict(OrganizationMember.ROLE_CHOICES) or role == 'owner':
            return Response({'error': 'invalid role'}, status=status.HTTP_400_BAD_REQUEST)

        invite = OrganizationInvite.objects.create(
            organization=organization,
            email=email,
            role=role,
            invited_by=request.user,
        )
        return Response({'token': invite.token, 'status': invite.status}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Список участников организации"""
        organization = self.get_object()
        if not (organization.owner == request.user or OrganizationMember.objects.filter(organization=organization, user=request.user, role__in=['owner', 'admin'], status='accepted').exists()):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = OrganizationMemberSerializer(organization.memberships.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch', 'delete'], url_path='members/(?P<user_id>[^/.]+)')
    def manage_member(self, request, pk=None, user_id=None):
        """Изменение роли или удаление участника"""
        organization = self.get_object()
        if not (organization.owner == request.user or OrganizationMember.objects.filter(organization=organization, user=request.user, role__in=['owner', 'admin'], status='accepted').exists()):
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            member = OrganizationMember.objects.get(organization=organization, user_id=user_id)
        except OrganizationMember.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'PATCH':
            role = request.data.get('role')
            if role not in dict(OrganizationMember.ROLE_CHOICES) or role == 'owner':
                return Response({'error': 'invalid role'}, status=status.HTTP_400_BAD_REQUEST)
            member.role = role
            member.save()
            return Response(OrganizationMemberSerializer(member).data)

        if member.role == 'owner':
            return Response({'error': 'cannot remove owner'}, status=status.HTTP_400_BAD_REQUEST)
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TeamViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    """Управление командами"""
    queryset = Team.objects.select_related('organization', 'owner', 'manager')
    serializer_class = TeamSerializer
    permission_classes = [TeamPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        # Доступны команды, где пользователь владелец/менеджер/участник через Membership
        return qs.filter(
            Q(owner=user) |
            Q(manager=user) |
            Q(memberships__user=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        team = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role', 'member')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        TeamMember.objects.update_or_create(team=team, user_id=user_id, defaults={'role': role})
        return Response({'message': 'Участник добавлен'})

    @action(detail=True, methods=['delete'])
    def remove_member(self, request, pk=None):
        team = self.get_object()
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        TeamMember.objects.filter(team=team, user_id=user_id).delete()
        return Response({'message': 'Участник удален'})


class OrganizationInviteViewSet(SwaggerSafeMixin, viewsets.ViewSet):
    """ViewSet для приглашений в организации"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        invites = OrganizationInvite.objects.filter(
            email=request.user.email, status='pending'
        ).filter(Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now()))
        serializer = OrganizationInviteSerializer(invites, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def accept(self, request):
        token = request.data.get('token')
        try:
            invite = OrganizationInvite.objects.get(token=token, email=request.user.email)
        except OrganizationInvite.DoesNotExist:
            return Response({'error': 'Инвайт не найден'}, status=status.HTTP_404_NOT_FOUND)
        if invite.expires_at and invite.expires_at < timezone.now():
            invite.status = 'expired'
            invite.save()
            return Response({'error': 'Инвайт просрочен'}, status=status.HTTP_410_GONE)
        invite.status = 'accepted'
        invite.responded_at = timezone.now()
        invite.save()
        OrganizationMember.objects.create(
            organization=invite.organization,
            user=request.user,
            role=invite.role,
            status='accepted',
            invited_by=invite.invited_by,
            invited_at=invite.created_at,
            responded_at=timezone.now()
        )
        return Response({'status': 'accepted'})

    @action(detail=False, methods=['post'])
    def decline(self, request):
        token = request.data.get('token')
        try:
            invite = OrganizationInvite.objects.get(token=token, email=request.user.email)
        except OrganizationInvite.DoesNotExist:
            return Response({'error': 'Инвайт не найден'}, status=status.HTTP_404_NOT_FOUND)
        invite.status = 'declined'
        invite.responded_at = timezone.now()
        invite.save()
        return Response({'status': 'declined'})


class ProjectStatusViewSet(viewsets.ModelViewSet):
    """ViewSet для управления статусами проектов"""
    queryset = ProjectStatus.objects.filter(is_active=True)
    serializer_class = ProjectStatusSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['order', 'name', 'created_at']
    ordering = ['order', 'name']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Получить только активные статусы"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """Получить статус по умолчанию"""
        try:
            default_status = self.get_queryset().get(is_default=True)
            serializer = self.get_serializer(default_status)
            return Response(serializer.data)
        except ProjectStatus.DoesNotExist:
            return Response({'error': 'Статус по умолчанию не найден'}, status=status.HTTP_404_NOT_FOUND)


class ProjectPriorityViewSet(viewsets.ModelViewSet):
    """ViewSet для управления приоритетами проектов"""
    queryset = ProjectPriority.objects.filter(is_active=True)
    serializer_class = ProjectPrioritySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['level', 'name', 'created_at']
    ordering = ['level', 'name']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Получить только активные приоритеты"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """Получить приоритет по умолчанию"""
        try:
            default_priority = self.get_queryset().get(is_default=True)
            serializer = self.get_serializer(default_priority)
            return Response(serializer.data)
        except ProjectPriority.DoesNotExist:
            return Response({'error': 'Приоритет по умолчанию не найден'}, status=status.HTTP_404_NOT_FOUND)


class TaskStatusViewSet(viewsets.ModelViewSet):
    """ViewSet для управления статусами задач"""
    queryset = TaskStatus.objects.filter(is_active=True)
    serializer_class = TaskStatusSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['order', 'name', 'created_at']
    ordering = ['order', 'name']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Получить только активные статусы"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def kanban_columns(self, request):
        """Получить статусы для колонок канбан (все активные статусы)"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """Получить статус по умолчанию"""
        try:
            default_status = self.get_queryset().get(is_default=True)
            serializer = self.get_serializer(default_status)
            return Response(serializer.data)
        except TaskStatus.DoesNotExist:
            return Response({'error': 'Статус по умолчанию не найден'}, status=status.HTTP_404_NOT_FOUND)


class TaskPriorityViewSet(viewsets.ModelViewSet):
    """ViewSet для управления приоритетами задач"""
    queryset = TaskPriority.objects.filter(is_active=True)
    serializer_class = TaskPrioritySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['level', 'name', 'created_at']
    ordering = ['level', 'name']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Получить только активные приоритеты"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """Получить приоритет по умолчанию"""
        try:
            default_priority = self.get_queryset().get(is_default=True)
            serializer = self.get_serializer(default_priority)
            return Response(serializer.data)
        except TaskPriority.DoesNotExist:
            return Response({'error': 'Приоритет по умолчанию не найден'}, status=status.HTTP_404_NOT_FOUND)


class ProjectViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    """ViewSet для управления проектами"""
    queryset = Project.objects.all()
    permission_classes = [ProjectPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'owner', 'manager']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'start_date', 'end_date', 'priority']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectSerializer
    
    def get_queryset(self):
        if self.is_swagger_fake_view():
            return Project.objects.none()
            
        user = self.get_safe_user()
        if not user:
            return Project.objects.none()
            
        queryset = super().get_queryset()

        # Показываем только проекты организаций, где пользователь является владельцем
        # или принятым участником
        queryset = queryset.filter(
            Q(organization__owner=user) |
            Q(organization__memberships__user=user, organization__memberships__status='accepted')
        ).filter(
            Q(owner=user) |
            Q(manager=user) |
            Q(team_members=user)
        ).distinct()
        
        # Дополнительный фильтр "Мои проекты" (оставляем для совместимости)
        my_projects = self.request.query_params.get('my_projects', None)
        if my_projects and my_projects.lower() == 'false':
            # Если явно указано false, показываем все доступные проекты
            queryset = super().get_queryset()
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Добавить участника в проект"""
        project = self.get_object()
        serializer = ProjectMemberSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # Проверяем, не является ли пользователь уже участником
                user_id = serializer.validated_data['user_id']
                if ProjectMember.objects.filter(project=project, user_id=user_id).exists():
                    return Response({'error': 'Пользователь уже является участником проекта'}, 
                                  status=status.HTTP_400_BAD_REQUEST)
                
                member = serializer.save(project=project)
                
                # Возвращаем полные данные участника
                response_serializer = ProjectMemberSerializer(member)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def remove_member(self, request, pk=None):
        """Удалить участника из проекта"""
        project = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            membership = ProjectMember.objects.get(project=project, user_id=user_id)
            membership.delete()
            return Response({'message': 'Участник удален из проекта'})
        except ProjectMember.DoesNotExist:
            return Response({'error': 'Участник не найден'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """Получить задачи проекта"""
        project = self.get_object()
        tasks = project.tasks.select_related('assignee', 'project').prefetch_related('assignees')
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Получить статистику проекта"""
        project = self.get_object()
        
        total_tasks = project.tasks.count()
        
        # Завершенные задачи с учетом новой и старой системы статусов
        completed_tasks = project.tasks.filter(
            Q(status_ref__is_final=True, status_ref__is_active=True) | Q(status='done')
        ).count()
        
        # Задачи в работе с учетом новой системы
        in_progress_tasks = project.tasks.filter(
            Q(status_ref__code='in_progress', status_ref__is_active=True) | Q(status='in_progress')
        ).count()
        
        # Просроченные задачи - которые не завершены и срок прошел
        overdue_tasks = project.tasks.filter(
            due_date__lt=timezone.now()
        ).exclude(
            Q(status_ref__is_final=True, status_ref__is_active=True) | Q(status='done')
        ).count()
        
        return Response({
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'overdue_tasks': overdue_tasks,
            'progress': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)
        })

    @action(detail=True, methods=['post'])
    def transfer(self, request, pk=None):
        """Перенести проект в другую команду той же организации"""
        project = self.get_object()
        new_team_id = request.data.get('team_id')
        sync_members = request.data.get('sync_members', True)
        if not new_team_id:
            return Response({'error': 'team_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            new_team = Team.objects.get(id=new_team_id)
        except Team.DoesNotExist:
            return Response({'error': 'Команда не найдена'}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем организацию
        if project.organization_id and new_team.organization_id and project.organization_id != new_team.organization_id:
            return Response({'error': 'Команда должна принадлежать той же организации'}, status=status.HTTP_400_BAD_REQUEST)

        project.team = new_team
        project.save(update_fields=['team'])

        if sync_members:
            team_user_ids = new_team.memberships.values_list('user_id', flat=True)
            existing_user_ids = set(project.memberships.values_list('user_id', flat=True))
            to_create = [uid for uid in team_user_ids if uid not in existing_user_ids]
            ProjectMember.objects.bulk_create([
                ProjectMember(project=project, user_id=uid, role='member') for uid in to_create
            ], ignore_conflicts=True)
        return Response({'ok': True})


class TaskViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    """
    ViewSet для управления задачами с поддержкой иерархии
    """
    queryset = (
        Task.objects
        .select_related('project', 'project__organization', 'assignee', 'creator')
        .prefetch_related('assignees', 'assignee_links__user')
    )
    serializer_class = TaskSerializer
    permission_classes = [TaskPermission]
    
    def get_queryset(self):
        """Возвращает queryset с учетом фильтров и иерархии"""
        queryset = super().get_queryset()
        
        # Фильтр по проекту
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Фильтр по организации
        organization_id = self.request.query_params.get('organization_id')
        if organization_id:
            queryset = queryset.filter(project__organization_id=organization_id)
        
        # Фильтр по статусу
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Фильтр по одиночному исполнителю (FK)
        assignee_param = self.request.query_params.get('assignee') or self.request.query_params.get('assigned_to')
        if assignee_param:
            queryset = queryset.filter(assignee_id=assignee_param)

        # Фильтр по множественным исполнителям (M2M)
        assignee_any = self.request.query_params.get('assignee_any')
        if assignee_any:
            queryset = queryset.filter(assignees__id=assignee_any)

        # Фильтр "мои задачи"
        my_tasks = self.request.query_params.get('my_tasks')
        if my_tasks in ['1', 'true', 'True', 'yes']:
            user = self.request.user
            queryset = queryset.filter(Q(assignee=user) | Q(creator=user))
        
        # Фильтр по родительской задаче (корневые задачи)
        parent_filter = self.request.query_params.get('parent_filter')
        if parent_filter == 'root':
            queryset = queryset.filter(parent__isnull=True)
        elif parent_filter == 'subtasks':
            queryset = queryset.filter(parent__isnull=False)
        
        return queryset.distinct()
    
    def get_serializer_class(self):
        """Выбирает сериализатор в зависимости от действия"""
        if self.action == 'list':
            return TaskListSerializer
        return TaskSerializer

    @swagger_auto_schema(
        operation_description="Список задач с фильтрами. Поддерживает одиночного исполнителя (assignee) и множественных (assignee_any). Фильтр parent_filter: 'root' или 'subtasks'.",
        manual_parameters=[
            openapi.Parameter('project_id', openapi.IN_QUERY, description='ID проекта', type=openapi.TYPE_INTEGER),
            openapi.Parameter('organization_id', openapi.IN_QUERY, description='ID организации', type=openapi.TYPE_INTEGER),
            openapi.Parameter('status', openapi.IN_QUERY, description='Статус задачи (устаревшее поле)', type=openapi.TYPE_STRING),
            openapi.Parameter('assignee', openapi.IN_QUERY, description='ID основного исполнителя (FK)', type=openapi.TYPE_INTEGER),
            openapi.Parameter('assigned_to', openapi.IN_QUERY, description='Алиас для assignee (устар.)', type=openapi.TYPE_INTEGER),
            openapi.Parameter('assignee_any', openapi.IN_QUERY, description='ID пользователя среди множественных исполнителей (M2M)', type=openapi.TYPE_INTEGER),
            openapi.Parameter('my_tasks', openapi.IN_QUERY, description='Показывать только мои задачи (true/false)', type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('parent_filter', openapi.IN_QUERY, description="Фильтр по иерархии: 'root' — только корневые, 'subtasks' — только подзадачи", type=openapi.TYPE_STRING, enum=['root', 'subtasks'])
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Создание задачи с валидацией иерархии"""
        # Делаем всю операцию атомарной: валидации + save + инициализация дерева + счетчики
        with transaction.atomic():
            # Получаем данные
            project_id = serializer.validated_data.get('project_id')
            parent_id = serializer.validated_data.get('parent_id')

            # Валидируем проект
            if project_id:
                try:
                    project = Project.objects.get(id=project_id)
                    # Автоматически устанавливаем organization из проекта
                    serializer.validated_data['organization'] = project.organization
                except Project.DoesNotExist:
                    raise ValidationError("Указанный проект не найден")

            # Валидируем родительскую задачу
            if parent_id:
                try:
                    parent_task = Task.objects.get(id=parent_id)

                    if parent_task.project_id != project_id:
                        raise ValidationError("Родительская задача должна принадлежать тому же проекту")

                    if self._would_create_cycle(parent_id, project_id):
                        raise ValidationError("Создание циклической ссылки между задачами невозможно")

                except Task.DoesNotExist:
                    raise ValidationError("Родительская задача не найдена")

            # Создаем задачу
            task = serializer.save()

            # Инициализация closure-таблицы
            self._init_task_tree(task)

            # Обновляем связанные задачи (счетчик)
            if parent_id:
                self._update_parent_relationships(task)
    
    def perform_update(self, serializer):
        """Обновление задачи с валидацией иерархии"""
        with transaction.atomic():
            instance = serializer.instance
            old_parent_id = instance.parent_id if instance.parent else None
            new_parent_id = serializer.validated_data.get('parent_id')

            # Проверяем изменение родителя
            if old_parent_id != new_parent_id:
                if new_parent_id:
                    # Валидируем нового родителя
                    try:
                        new_parent = Task.objects.get(id=new_parent_id)
                        if new_parent.project_id != instance.project_id:
                            raise ValidationError("Родительская задача должна принадлежать тому же проекту")

                        # Проверяем на циклические ссылки
                        if self._would_create_cycle(new_parent_id, instance.project_id, instance.id):
                            raise ValidationError("Создание циклической ссылки между задачами невозможно")

                    except Task.DoesNotExist:
                        raise ValidationError("Родительская задача не найдена")

            # Обновляем связи для старого родителя (пересчет количества подзадач у старого родителя)
            old_parent = Task.objects.filter(id=old_parent_id).first() if old_parent_id else None
            if old_parent:
                old_parent.subtasks_count = old_parent.subtasks.count()
                old_parent.save(update_fields=['subtasks_count'])

            # Обновляем задачу
            task = serializer.save()

            # Обновляем closure-таблицу при переносе
            if new_parent_id != old_parent_id:
                self._rebuild_task_tree_on_move(task)

            # Обновляем связи для нового родителя
            if new_parent_id and new_parent_id != old_parent_id:
                self._update_parent_relationships(task)
    
    def _would_create_cycle(self, parent_id, project_id, exclude_task_id=None):
        """Проверяет, не создаст ли назначение родителя циклическую ссылку"""
        if not parent_id:
            return False
        
        # Получаем всех предков потенциального родителя
        ancestors = set()
        current_id = parent_id
        
        while current_id:
            if current_id == exclude_task_id:
                return True  # Цикл обнаружен
            
            try:
                current_task = Task.objects.get(id=current_id, project_id=project_id)
                if current_id in ancestors:
                    return True  # Цикл обнаружен
                
                ancestors.add(current_id)
                current_id = current_task.parent_id
            except Task.DoesNotExist:
                break
        
        return False
    
    def _update_parent_relationships(self, task):
        """Обновляет связи родитель-потомок"""
        # Обновляем количество подзадач у родителя
        if task.parent:
            parent = task.parent
            parent.subtasks_count = parent.subtasks.count()
            parent.save(update_fields=['subtasks_count'])
        
        # Обновляем количество подзадач у старого родителя (если был)
        # Это будет обработано в perform_update

    # ---- Closure table helpers ----
    def _init_task_tree(self, task):
        TaskTree.objects.get_or_create(task=task, ancestor=task, defaults={'depth': 0})
        if task.parent_id:
            parent = task.parent
            parent_ancs = TaskTree.objects.filter(task=parent)
            bulk = [
                TaskTree(task=task, ancestor_id=pa.ancestor_id, depth=pa.depth + 1)
                for pa in parent_ancs
            ]
            TaskTree.objects.bulk_create(bulk, ignore_conflicts=True)

    def _rebuild_task_tree_on_move(self, node):
        # запрет цикла: новый родитель не может быть потомком текущего узла
        if node.parent_id and TaskTree.objects.filter(task=node.parent_id, ancestor=node).exists():
            raise ValidationError("Создание циклической ссылки между задачами невозможно")
        # ids поддерева
        subtree = list(TaskTree.objects.filter(ancestor=node).values_list('task_id', flat=True))
        old_anc_ids = set(TaskTree.objects.filter(task=node).values_list('ancestor_id', flat=True))
        # удалить связи к старым предкам (кроме внутрисубдеревных)
        TaskTree.objects.filter(task_id__in=subtree, ancestor_id__in=old_anc_ids).exclude(ancestor_id__in=subtree).delete()
        # добавить связи к новым предкам текущего родителя
        if node.parent_id:
            depth_map = dict(TaskTree.objects.filter(ancestor=node).values_list('task_id', 'depth'))
            new_ancs = list(TaskTree.objects.filter(task=node.parent))
            bulk = []
            for t_id, d in depth_map.items():
                for na in new_ancs:
                    bulk.append(TaskTree(task_id=t_id, ancestor_id=na.ancestor_id, depth=d + na.depth + 1))
            TaskTree.objects.bulk_create(bulk, ignore_conflicts=True)

    # ---- Hierarchy actions ----
    @action(detail=True, methods=['post'])
    @swagger_auto_schema(
        operation_description="Создать подзадачу для указанной задачи",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
                'assignee_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'assignee_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'priority': openapi.Schema(type=openapi.TYPE_STRING),
                'start_date': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                'due_date': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
            },
            required=['title']
        )
    )
    def subtasks(self, request, pk=None):
        parent = self.get_object()
        data = request.data.copy()
        data['project_id'] = parent.project_id
        data['parent_id'] = parent.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'])
    @swagger_auto_schema(
        operation_description="Переместить задачу под нового родителя",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'new_parent_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID новой родительской задачи (null для снятия)')
            }
        )
    )
    def move(self, request, pk=None):
        node = self.get_object()
        new_parent_id = request.data.get('new_parent_id', None)
        serializer = self.get_serializer(instance=node, data={'parent_id': new_parent_id}, partial=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            self.perform_update(serializer)
        return Response(self.get_serializer(node).data)

    @action(detail=True, methods=['get'])
    @swagger_auto_schema(operation_description="Получить путь (цепочку предков) для задачи")
    def path(self, request, pk=None):
        node = self.get_object()
        entries = TaskTree.objects.filter(task=node).exclude(ancestor=node).select_related('ancestor').order_by('-depth')
        path = [TaskListSerializer(e.ancestor).data for e in entries]
        return Response({'task_id': node.id, 'path': path})

    @action(detail=False, methods=['get'])
    @swagger_auto_schema(
        operation_description="Получить дерево задач проекта",
        manual_parameters=[
            openapi.Parameter('project_id', openapi.IN_QUERY, description='ID проекта', type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('root_id', openapi.IN_QUERY, description='ID корневой задачи (опционально)', type=openapi.TYPE_INTEGER),
            openapi.Parameter('depth', openapi.IN_QUERY, description='Глубина дерева (опционально)', type=openapi.TYPE_INTEGER)
        ]
    )
    def project_tree(self, request):
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response({'error': 'project_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        root_id = request.query_params.get('root_id')
        depth_param = request.query_params.get('depth')
        depth = int(depth_param) if depth_param is not None else None
        tasks = list(Task.objects.filter(project_id=project_id).select_related('assignee'))
        by_parent = {}
        for t in tasks:
            by_parent.setdefault(t.parent_id, []).append(t)
        def build(pid, d):
            res = []
            for t in by_parent.get(pid, []):
                data = TaskListSerializer(t).data
                if d is None or d > 0:
                    data['subtasks'] = build(t.id, None if d is None else d - 1)
                else:
                    data['subtasks'] = []
                res.append(data)
            return res
        tree = build(int(root_id), depth) if root_id else build(None, depth)
        return Response({'project_id': project_id, 'tree': tree})

    @action(detail=True, methods=['get'])
    @swagger_auto_schema(operation_description="Список назначений (TaskAssignee) по задаче с ролями")
    def assignees(self, request, pk=None):
        task = self.get_object()
        links = TaskAssignee.objects.filter(task=task).select_related('user')
        data = [
            {
                'user': CRMUserSerializer(link.user).data,
                'role': link.role,
                'assigned_at': link.assigned_at,
            }
            for link in links
        ]
        return Response(data)

    @action(detail=True, methods=['post'])
    @swagger_auto_schema(
        operation_description="Назначить пользователя на задачу с ролью",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'role': openapi.Schema(type=openapi.TYPE_STRING, enum=['owner', 'assignee', 'reviewer'])
            },
            required=['user_id']
        )
    )
    def add_assignee(self, request, pk=None):
        task = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role', 'assignee')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        # только члены команды проекта
        if not ProjectMember.objects.filter(project=task.project, user_id=user_id).exists():
            return Response({'error': 'Пользователь не состоит в команде проекта'}, status=status.HTTP_400_BAD_REQUEST)
        link, created = TaskAssignee.objects.get_or_create(task=task, user_id=user_id, role=role, defaults={'assigned_by': request.user})
        # Синхронизируем M2M исполнителей при роли 'assignee'
        if role == 'assignee':
            user_obj = User.objects.filter(id=user_id).only('id').first()
            if user_obj:
                task.assignees.add(user_obj)
        return Response({'ok': True, 'created': created})

    @action(detail=True, methods=['delete'])
    @swagger_auto_schema(
        operation_description="Снять назначение пользователя с задачи",
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, description='ID пользователя', type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('role', openapi.IN_QUERY, description="Роль для удаления ('assignee' удалит M2M исполнителя). Если не указать — удалятся все роли пользователя.", type=openapi.TYPE_STRING, enum=['owner', 'assignee', 'reviewer'])
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'role': openapi.Schema(type=openapi.TYPE_STRING, enum=['owner', 'assignee', 'reviewer'])
            }
        )
    )
    def remove_assignee(self, request, pk=None):
        task = self.get_object()
        user_id = request.query_params.get('user_id') or request.data.get('user_id')
        role = request.query_params.get('role') or request.data.get('role')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        q = TaskAssignee.objects.filter(task=task, user_id=user_id)
        if role:
            q = q.filter(role=role)
        deleted, _ = q.delete()
        # Синхронизируем M2M исполнителей, если удаляем роль 'assignee' или все роли
        if not role or role == 'assignee':
            # Проверим, осталась ли у пользователя роль 'assignee' на задаче
            still_assignee = TaskAssignee.objects.filter(task=task, user_id=user_id, role='assignee').exists()
            if not still_assignee:
                task.assignees.remove(user_id)
        return Response({'deleted': deleted})

    def destroy(self, request, *args, **kwargs):
        """Удаление задачи с обновлением счетчика подзадач у родителя"""
        task = self.get_object()
        parent = task.parent
        response = super().destroy(request, *args, **kwargs)
        if parent:
            parent.subtasks_count = parent.subtasks.count()
            parent.save(update_fields=['subtasks_count'])
        return response
    
    @action(detail=True, methods=['post'])
    def move_to_project(self, request, pk=None):
        """Перемещение задачи в другой проект"""
        task = self.get_object()
        new_project_id = request.data.get('project_id')
        
        if not new_project_id:
            return Response(
                {"error": "Не указан ID нового проекта"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            new_project = Project.objects.get(id=new_project_id)
            
            with transaction.atomic():
                # Перемещаем задачу и все её подзадачи
                self._move_task_tree(task, new_project)
                
                return Response({"message": "Задача успешно перемещена"})
                
        except Project.DoesNotExist:
            return Response(
                {"error": "Проект не найден"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _move_task_tree(self, task, new_project):
        """Рекурсивно перемещает задачу и все её подзадачи в новый проект"""
        # Обновляем проект и организацию
        task.project = new_project
        task.organization = new_project.organization
        task.save(update_fields=['project', 'organization'])
        
        # Перемещаем все подзадачи
        for subtask in task.subtasks.all():
            self._move_task_tree(subtask, new_project)
    
    @action(detail=True, methods=['get'])
    def hierarchy(self, request, pk=None):
        """Получение иерархии подзадач для задачи"""
        task = self.get_object()
        
        def build_hierarchy(task_obj):
            """Рекурсивно строит иерархию подзадач"""
            subtasks = []
            for subtask in task_obj.subtasks.all():
                subtask_data = TaskListSerializer(subtask).data
                subtask_data['subtasks'] = build_hierarchy(subtask)
                subtasks.append(subtask_data)
            
            return subtasks
        
        hierarchy_data = {
            'task': TaskListSerializer(task).data,
            'subtasks': build_hierarchy(task)
        }
        
        return Response(hierarchy_data)
    
    @action(detail=False, methods=['get'])
    def project_hierarchy(self, request):
        """Получение полной иерархии задач для проекта"""
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response(
                {"error": "Не указан ID проекта"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Получаем только корневые задачи проекта
        root_tasks = Task.objects.filter(
            project_id=project_id,
            parent__isnull=True
        ).select_related('project', 'assigned_to', 'created_by')
        
        def build_project_hierarchy():
            """Строит полную иерархию проекта"""
            hierarchy = []
            for root_task in root_tasks:
                task_data = TaskListSerializer(root_task).data
                task_data['subtasks'] = build_hierarchy(root_task)
                hierarchy.append(task_data)
            return hierarchy
        
        def build_hierarchy(task_obj):
            """Рекурсивно строит иерархию подзадач"""
            subtasks = []
            for subtask in task_obj.subtasks.all():
                subtask_data = TaskListSerializer(subtask).data
                subtask_data['subtasks'] = build_hierarchy(subtask)
                subtasks.append(subtask_data)
            
            return subtasks
        
        project_hierarchy = build_project_hierarchy()
        
        return Response({
            'project_id': project_id,
            'hierarchy': project_hierarchy
        })
    
    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """Получить задачи для календаря"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            # По умолчанию текущий месяц
            now = timezone.now()
            start_date = now.replace(day=1).date()
            end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        
        tasks = self.get_queryset().filter(
            Q(start_date__range=[start_date, end_date]) |
            Q(due_date__range=[start_date, end_date])
        )
        
        serializer = TaskCalendarSerializer(tasks, many=True)
        
        # Преобразуем в формат для календаря
        events = []
        for task in serializer.data:
            # Событие начала задачи
            if task['start_date']:
                events.append({
                    'id': f"start_{task['id']}",
                    'title': f"▶ {task['title']}",
                    'start': task['start_date'],
                    'backgroundColor': self.get_task_color(task['priority'], task['status']),
                    'task_id': task['id'],
                    'type': 'start',
                    'task_data': task
                })
            
            # Событие срока выполнения
            if task['due_date']:
                events.append({
                    'id': f"due_{task['id']}",
                    'title': f"⏰ {task['title']}",
                    'start': task['due_date'],
                    'backgroundColor': self.get_due_color(task['priority'], task['status']),
                    'task_id': task['id'],
                    'type': 'due',
                    'task_data': task
                })
        
        return Response({'events': events})
    
    def get_task_color(self, priority, status):
        """Получить цвет задачи для календаря"""
        if status == 'done':
            return '#28a745'  # Зеленый для выполненных
        elif status == 'cancelled':
            return '#6c757d'  # Серый для отмененных
        elif priority == 'urgent':
            return '#dc3545'  # Красный для срочных
        elif priority == 'high':
            return '#fd7e14'  # Оранжевый для высокого приоритета
        elif priority == 'medium':
            return '#007bff'  # Синий для среднего приоритета
        else:
            return '#6f42c1'  # Фиолетовый для низкого приоритета
    
    def get_due_color(self, priority, status):
        """Получить цвет срока выполнения"""
        if status == 'done':
            return '#28a745'
        elif priority == 'urgent':
            return '#dc3545'
        else:
            return '#ffc107'  # Желтый для сроков
    
    @action(detail=False, methods=['get'])
    def kanban(self, request):
        """Получить задачи для канбан доски"""
        project_id = request.query_params.get('project_id')
        priority = request.query_params.get('priority')
        assignee = request.query_params.get('assignee')
        ordering = request.query_params.get('ordering', 'kanban_order')
        
        queryset = self.get_queryset()
        
        # Применяем фильтры
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        if priority:
            queryset = queryset.filter(priority=priority)
            
        if assignee:
            queryset = queryset.filter(assignee_id=assignee)
        
        # Применяем сортировку
        ordering_fields = {
            'kanban_order': ['kanban_order', '-created_at'],
            '-created_at': ['-created_at'],
            'created_at': ['created_at'],
            'due_date': ['due_date', '-created_at'],
            '-due_date': ['-due_date', '-created_at'],
            'priority': ['priority_ref__level', 'priority', '-created_at'],
            '-priority': ['-priority_ref__level', '-priority', '-created_at'],
            'assignee': ['assignee__first_name', 'assignee__last_name', '-created_at'],
            '-assignee': ['-assignee__first_name', '-assignee__last_name', '-created_at']
        }
        
        # Применяем сортировку с fallback
        ordering_list = ordering_fields.get(ordering, ['kanban_order', '-created_at'])
        queryset = queryset.order_by(*ordering_list)
        
        # Получаем все активные статусы задач
        try:
            # Используем все активные статусы
            kanban_statuses = TaskStatus.objects.filter(is_active=True).order_by('order', 'name')
        except Exception:
            # Fallback: используем старые статусы
            kanban_statuses = []
        
        # Группируем по статусам
        kanban_data = {}
        
        if kanban_statuses:
            # Используем динамические статусы
            for status in kanban_statuses:
                tasks = queryset.filter(status=status.code)
                serializer = TaskKanbanSerializer(tasks, many=True)
                kanban_data[status.code] = serializer.data
        else:
            # Fallback к старым жестко заданным статусам
            fallback_statuses = ['todo', 'in_progress', 'review', 'done']
            for status_key in fallback_statuses:
                tasks = queryset.filter(status=status_key)
                serializer = TaskKanbanSerializer(tasks, many=True)
                kanban_data[status_key] = serializer.data
        
        return Response(kanban_data)
    
    @action(detail=True, methods=['post'])
    def update_kanban_order(self, request, pk=None):
        """Обновить порядок задач в канбан"""
        task = self.get_object()
        new_order = request.data.get('order')
        new_status = request.data.get('status')
        
        if new_order is not None:
            task.kanban_order = new_order
        
        if new_status:
            # Проверяем существование статуса в новой системе
            try:
                status_obj = TaskStatus.objects.get(code=new_status, is_active=True)
                task.status = new_status
                task.status_ref = status_obj
                
                # Если задача помечена как выполненная
                if status_obj.is_final and not task.completed_at:
                    task.completed_at = timezone.now()
                elif not status_obj.is_final:
                    task.completed_at = None
                
            except TaskStatus.DoesNotExist:
                # Fallback: проверяем по старым choices
                if new_status in dict(Task.TASK_STATUS_CHOICES):
                    task.status = new_status
                    
                    # Для обратной совместимости
                    if new_status == 'done' and not task.completed_at:
                        task.completed_at = timezone.now()
                    elif new_status != 'done':
                        task.completed_at = None
                else:
                    return Response({'error': f'Неверный статус: {new_status}'}, status=status.HTTP_400_BAD_REQUEST)
        
        task.save()
        return Response({'message': 'Порядок задач обновлен'})
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Изменить статус задачи"""
        task = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Task.TASK_STATUS_CHOICES):
            return Response({'error': 'Неверный статус'}, status=status.HTTP_400_BAD_REQUEST)
        
        task.status = new_status
        
        if new_status == 'done':
            task.completed_at = timezone.now()
        elif new_status == 'in_progress' and not task.start_date:
            task.start_date = timezone.now()
        
        task.save()
        return Response({'message': 'Статус задачи изменен'})
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Добавить комментарий к задаче"""
        task = self.get_object()
        serializer = TaskCommentSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(task=task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_time_log(self, request, pk=None):
        """Добавить учет времени"""
        task = self.get_object()
        serializer = TimeLogSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(task=task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def create_from_calendar(self, request):
        """Создать задачу из календаря"""
        data = request.data.copy()
        
        # Если не указан проект, пытаемся найти активный проект пользователя
        if not data.get('project_id'):
            active_project = Project.objects.filter(
                Q(owner=request.user) | Q(manager=request.user),
                status='active'
            ).first()
            
            if active_project:
                data['project_id'] = active_project.id
            else:
                return Response(
                    {'error': 'Необходимо указать проект'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = TaskSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskCommentViewSet(viewsets.ModelViewSet):
    """ViewSet для комментариев к задачам"""
    queryset = TaskComment.objects.all()
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        task_id = self.request.query_params.get('task_id')
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        return queryset


class TimeLogViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    """ViewSet для учета времени"""
    queryset = TimeLog.objects.all()
    serializer_class = TimeLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['task', 'user', 'date']
    ordering = ['-date', '-created_at']
    
    def get_queryset(self):
        if self.is_swagger_fake_view():
            return TimeLog.objects.none()
            
        user = self.get_safe_user()
        if not user:
            return TimeLog.objects.none()
            
        queryset = super().get_queryset()
        task_id = self.request.query_params.get('task_id')
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_time_logs(self, request):
        """Получить мои записи времени"""
        queryset = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для получения пользователей (только чтение)"""
    queryset = User.objects.filter(is_active=True)
    serializer_class = CRMUserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['username', 'first_name', 'last_name']
    ordering = ['first_name', 'last_name', 'username']