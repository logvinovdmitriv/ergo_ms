from rest_framework import serializers
from django.contrib.auth import get_user_model
from src.modules.crm.models import (
    Project, ProjectMember, Task, TaskComment, TaskAttachment, TimeLog,
    ProjectStatus, ProjectPriority, TaskStatus, TaskPriority,
    Organization, OrganizationMember, OrganizationInvite,
    Team, TeamMember, TaskAssignee
)

User = get_user_model()


class ProjectStatusSerializer(serializers.ModelSerializer):
    """Сериализатор статусов проектов"""
    
    class Meta:
        model = ProjectStatus
        fields = ['id', 'name', 'code', 'description', 'color', 'order', 'is_active', 'is_default', 'is_final', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ProjectPrioritySerializer(serializers.ModelSerializer):
    """Сериализатор приоритетов проектов"""
    
    class Meta:
        model = ProjectPriority
        fields = ['id', 'name', 'code', 'description', 'color', 'level', 'is_active', 'is_default', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class TaskStatusSerializer(serializers.ModelSerializer):
    """Сериализатор статусов задач"""
    
    class Meta:
        model = TaskStatus
        fields = ['id', 'name', 'code', 'description', 'color', 'order', 'is_active', 'is_default', 'is_final', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class TaskPrioritySerializer(serializers.ModelSerializer):
    """Сериализатор приоритетов задач"""
    
    class Meta:
        model = TaskPriority
        fields = ['id', 'name', 'code', 'description', 'color', 'level', 'is_active', 'is_default', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CRMUserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'email']


class OrganizationMemberSerializer(serializers.ModelSerializer):
    """Сериализатор участника организации"""
    user = CRMUserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    invited_by = CRMUserSerializer(read_only=True)

    class Meta:
        model = OrganizationMember
        fields = ['id', 'user', 'user_id', 'role', 'status', 'invited_by', 'invited_at', 'responded_at']
        read_only_fields = ['invited_by', 'invited_at', 'responded_at']
        
class OrganizationSerializer(serializers.ModelSerializer):
    """Сериализатор организации"""
    owner = CRMUserSerializer(read_only=True)
    memberships = OrganizationMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'description', 'logo_url', 'industry', 'website',
            'email', 'phone', 'country', 'timezone', 'address',
            'billing_name', 'billing_vat', 'billing_address',
            'owner', 'memberships', 'visibility', 'default_role', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'owner', 'created_at', 'updated_at']


class OrganizationInviteSerializer(serializers.ModelSerializer):
    """Сериализатор приглашения"""
    organization = OrganizationSerializer(read_only=True)
    invited_by = CRMUserSerializer(read_only=True)

    class Meta:
        model = OrganizationInvite
        fields = [
            'id', 'organization', 'email', 'role', 'token',
            'expires_at', 'status', 'invited_by', 'created_at'
        ]
        read_only_fields = ['token', 'status', 'invited_by', 'created_at', 'organization']

class ProjectMemberSerializer(serializers.ModelSerializer):
    """Сериализатор участника проекта"""
    user = CRMUserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ProjectMember
        fields = ['id', 'user', 'user_id', 'role', 'joined_at']


class ProjectSerializer(serializers.ModelSerializer):
    """Сериализатор проекта"""
    owner = CRMUserSerializer(read_only=True)
    manager = CRMUserSerializer(read_only=True)
    manager_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    memberships = ProjectMemberSerializer(many=True, read_only=True)
    organization = OrganizationSerializer(read_only=True)
    organization_id = serializers.IntegerField(write_only=True, required=False)
    team = serializers.SerializerMethodField(read_only=True)
    team_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    # Новые поля для статусов и приоритетов
    status_ref = ProjectStatusSerializer(read_only=True)
    priority_ref = ProjectPrioritySerializer(read_only=True)
    status_ref_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    priority_ref_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    # Дополнительные поля
    current_status = serializers.CharField(read_only=True)
    current_priority = serializers.CharField(read_only=True)
    status_display = serializers.CharField(read_only=True)
    priority_display = serializers.CharField(read_only=True)
    
    task_count = serializers.SerializerMethodField()
    completed_task_count = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'owner', 'manager', 'manager_id',
            'organization', 'organization_id', 'team', 'team_id', 'memberships', 'status', 'priority', 'start_date', 'end_date',
            'created_at', 'updated_at', 'color', 'task_count', 'completed_task_count',
            'progress', 'status_ref', 'priority_ref', 'status_ref_id', 'priority_ref_id',
            'current_status', 'current_priority', 'status_display', 'priority_display'
        ]
    
    def get_task_count(self, obj):
        return obj.tasks.count()
    
    def get_completed_task_count(self, obj):
        """Получить количество завершенных задач (учитываем новую и старую систему статусов)"""
        from django.db.models import Q
        
        # Фильтр для новой системы статусов (status_ref.is_final = True)
        new_system_filter = Q(status_ref__is_final=True, status_ref__is_active=True)
        
        # Фильтр для старой системы статусов (status = 'done')
        old_system_filter = Q(status='done')
        
        return obj.tasks.filter(new_system_filter | old_system_filter).count()
    
    def get_progress(self, obj):
        """Вычислить прогресс проекта в процентах"""
        total = obj.tasks.count()
        if total == 0:
            return 0
        
        completed = self.get_completed_task_count(obj)
        return round((completed / total) * 100)
    
    def create(self, validated_data):
        user = self.context['request'].user
        # Нормализуем пустые строки -> None
        for key in ['start_date', 'end_date']:
            if validated_data.get(key) == '':
                validated_data[key] = None
        organization_id = validated_data.pop('organization_id', None)
        team_id = validated_data.pop('team_id', None)

        organization = None
        # 1) Если явно передали organization_id — используем его
        if organization_id:
            try:
                organization = Organization.objects.get(id=organization_id)
            except Organization.DoesNotExist:
                raise serializers.ValidationError('Организация не найдена')
        # 2) Если organization_id не передан, но есть team_id — определим организацию по команде
        elif team_id:
            try:
                team = Team.objects.select_related('organization').get(id=team_id)
                organization = team.organization
            except Team.DoesNotExist:
                raise serializers.ValidationError('Команда не найдена')
        # 3) Иначе — недостаточно данных
        else:
            raise serializers.ValidationError('organization_id or team_id is required')

        # Проверяем, что пользователь состоит в организации (владелец или член)
        if not (
            organization.owner == user or
            OrganizationMember.objects.filter(organization=organization, user=user, status='accepted').exists()
        ):
            raise serializers.ValidationError('Вы не являетесь участником организации')

        validated_data['owner'] = user
        validated_data['organization'] = organization
        project = super().create(validated_data)

        # Привязываем команду, если указана, и она принадлежит той же организации
        if team_id:
            try:
                team = Team.objects.get(id=team_id, organization=organization)
                project.team = team
                project.save(update_fields=['team'])
                # Синхронизация участников команды в участники проекта
                team_user_ids = team.memberships.values_list('user_id', flat=True)
                existing_user_ids = set(project.memberships.values_list('user_id', flat=True))
                for uid in team_user_ids:
                    if uid not in existing_user_ids:
                        ProjectMember.objects.create(project=project, user_id=uid, role='member')
            except Team.DoesNotExist:
                # Команда из другой организации — игнорируем привязку
                pass

        return project
    def update(self, instance, validated_data):
        team_id = validated_data.pop('team_id', None)
        project = super().update(instance, validated_data)
        if team_id is not None:
            if team_id:
                try:
                    team = Team.objects.get(id=team_id, organization=project.organization)
                    project.team = team
                    project.save(update_fields=['team'])
                except Team.DoesNotExist:
                    pass
            else:
                project.team = None
                project.save(update_fields=['team'])
        return project

    def get_team(self, obj):
        if not getattr(obj, 'team', None):
            return None
        team = obj.team
        return {
            'id': team.id,
            'name': team.name,
            'manager': CRMUserSerializer(team.manager).data if team.manager else None,
        }

class TeamMemberSerializer(serializers.ModelSerializer):
    user = CRMUserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = TeamMember
        fields = ['id', 'user', 'user_id', 'role', 'joined_at']


class TeamSerializer(serializers.ModelSerializer):
    owner = CRMUserSerializer(read_only=True)
    manager = CRMUserSerializer(read_only=True)
    manager_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    organization = OrganizationSerializer(read_only=True)
    organization_id = serializers.IntegerField(write_only=True)
    memberships = TeamMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'description', 'organization', 'organization_id', 'owner', 'manager', 'manager_id',
            'status', 'created_at', 'updated_at', 'memberships'
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        organization_id = validated_data.pop('organization_id', None)
        if not organization_id:
            raise serializers.ValidationError('organization_id is required')
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise serializers.ValidationError('Организация не найдена')

        if not (organization.owner == user or OrganizationMember.objects.filter(organization=organization, user=user, status='accepted').exists()):
            raise serializers.ValidationError('Вы не являетесь участником организации')

        validated_data['organization'] = organization
        validated_data['owner'] = user
        return super().create(validated_data)
class ProjectListSerializer(serializers.ModelSerializer):
    """Сериализатор списка проектов"""
    owner = CRMUserSerializer(read_only=True)
    manager = CRMUserSerializer(read_only=True)
    organization = OrganizationSerializer(read_only=True)
    
    # Новые поля для статусов и приоритетов
    status_ref = ProjectStatusSerializer(read_only=True)
    priority_ref = ProjectPrioritySerializer(read_only=True)
    current_status = serializers.CharField(read_only=True)
    current_priority = serializers.CharField(read_only=True)
    status_display = serializers.CharField(read_only=True)
    priority_display = serializers.CharField(read_only=True)
    
    task_count = serializers.SerializerMethodField()
    completed_task_count = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'owner', 'manager', 'organization', 'status', 'priority',
            'start_date', 'end_date', 'created_at', 'color', 'task_count',
            'completed_task_count', 'progress', 'status_ref', 'priority_ref',
            'current_status', 'current_priority', 'status_display', 'priority_display'
        ]
    
    def get_task_count(self, obj):
        return obj.tasks.count()
    
    def get_completed_task_count(self, obj):
        """Получить количество завершенных задач (учитываем новую и старую систему статусов)"""
        from django.db.models import Q
        
        # Фильтр для новой системы статусов (status_ref.is_final = True)
        new_system_filter = Q(status_ref__is_final=True, status_ref__is_active=True)
        
        # Фильтр для старой системы статусов (status = 'done')
        old_system_filter = Q(status='done')
        
        return obj.tasks.filter(new_system_filter | old_system_filter).count()
    
    def get_progress(self, obj):
        """Вычислить прогресс проекта в процентах"""
        total = obj.tasks.count()
        if total == 0:
            return 0
        
        completed = self.get_completed_task_count(obj)
        return round((completed / total) * 100)


class TaskCommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария к задаче"""
    author = CRMUserSerializer(read_only=True)
    
    class Meta:
        model = TaskComment
        fields = ['id', 'content', 'author', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class TaskAttachmentSerializer(serializers.ModelSerializer):
    """Сериализатор прикрепленного файла"""
    uploaded_by = CRMUserSerializer(read_only=True)
    
    class Meta:
        model = TaskAttachment
        fields = ['id', 'file', 'filename', 'uploaded_by', 'uploaded_at']
    
    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class TimeLogSerializer(serializers.ModelSerializer):
    """Сериализатор учета времени"""
    user = CRMUserSerializer(read_only=True)
    
    class Meta:
        model = TimeLog
        fields = ['id', 'description', 'hours', 'date', 'user', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    """Сериализатор списка задач"""
    assignee = CRMUserSerializer(read_only=True)
    assignees = CRMUserSerializer(many=True, read_only=True)
    creator = CRMUserSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)

    # Новые поля для статусов и приоритетов
    status_ref = TaskStatusSerializer(read_only=True)
    priority_ref = TaskPrioritySerializer(read_only=True)
    current_status = serializers.CharField(read_only=True)
    current_priority = serializers.CharField(read_only=True)
    status_display = serializers.CharField(read_only=True)
    priority_display = serializers.CharField(read_only=True)

    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    parent_title = serializers.SerializerMethodField()
    parent_id = serializers.IntegerField(read_only=True)
    subtasks = serializers.SerializerMethodField()
    subtasks_count = serializers.IntegerField(read_only=True)

    comment_count = serializers.SerializerMethodField()
    attachment_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'assignee', 'creator',
            'assignees',
            'status', 'priority', 'start_date', 'due_date', 'completed_at',
            'created_at', 'updated_at', 'estimated_hours', 'actual_hours',
            'kanban_order', 'comment_count', 'attachment_count',
            'status_ref', 'priority_ref', 'current_status', 'current_priority',
            'status_display', 'priority_display', 'parent', 'parent_id', 'parent_title', 'subtasks', 'subtasks_count'
        ]

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_attachment_count(self, obj):
        return obj.attachments.count()
    
    def get_subtasks(self, obj):
        """Возвращает список подзадач для отображения в списке"""
        # Ограничиваем глубину для избежания бесконечной рекурсии
        subtasks = obj.subtasks.all()[:10]  # Максимум 10 подзадач
        # Используем упрощенный сериализатор для подзадач
        return [
            {
                'id': subtask.id,
                'title': subtask.title,
                'status': subtask.status,
                'priority': subtask.priority,
                'assignee': CRMUserSerializer(subtask.assignee).data if subtask.assignee else None,
                'due_date': subtask.due_date,
                'subtasks_count': subtask.subtasks.count()
            }
            for subtask in subtasks
        ]

    def get_parent_title(self, obj):
        try:
            return obj.parent.title if obj.parent_id else None
        except Exception:
            return None


class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор задачи"""
    assignee = CRMUserSerializer(read_only=True)
    assignees = CRMUserSerializer(many=True, read_only=True)
    creator = CRMUserSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)
    assignee_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    assignee_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    # Read-only список ID исполнителей для удобства клиента
    assignee_user_ids = serializers.SerializerMethodField(read_only=True)
    project_id = serializers.IntegerField(write_only=True)
    organization = OrganizationSerializer(read_only=True)
    organization_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    parent_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    subtasks = serializers.SerializerMethodField()
    assignee_links = serializers.SerializerMethodField()
    
    # Новые поля для статусов и приоритетов
    status_ref = TaskStatusSerializer(read_only=True)
    priority_ref = TaskPrioritySerializer(read_only=True)
    status_ref_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    priority_ref_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    # Дополнительные поля
    current_status = serializers.CharField(read_only=True)
    current_priority = serializers.CharField(read_only=True)
    status_display = serializers.CharField(read_only=True)
    priority_display = serializers.CharField(read_only=True)
    
    # Поля дат с дополнительной обработкой
    start_date = serializers.DateTimeField(required=False, allow_null=True)
    due_date = serializers.DateTimeField(required=False, allow_null=True)
    
    comments = TaskCommentSerializer(many=True, read_only=True)
    attachments = TaskAttachmentSerializer(many=True, read_only=True)
    time_logs = TimeLogSerializer(many=True, read_only=True)
    total_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'project_id', 'organization', 'organization_id', 'assignee', 'assignee_id',
            'assignee_ids',
            'assignees',
            'creator', 'status', 'priority', 'start_date', 'due_date', 'completed_at',
            'created_at', 'updated_at', 'estimated_hours', 'actual_hours', 'kanban_order',
            'comments', 'attachments', 'time_logs', 'total_time', 'parent', 'parent_id', 'subtasks',
            'status_ref', 'priority_ref', 'status_ref_id', 'priority_ref_id',
            'current_status', 'current_priority', 'status_display', 'priority_display',
            'assignee_links', 'assignee_user_ids'
        ]
    
    def get_total_time(self, obj):
        return sum(log.hours for log in obj.time_logs.all())

    def get_assignee_user_ids(self, obj):
        return list(obj.assignees.values_list('id', flat=True))
    
    def get_subtasks(self, obj):
        """Возвращает список подзадач для отображения в списке"""
        # Ограничиваем глубину для избежания бесконечной рекурсии
        subtasks = obj.subtasks.all()[:10]  # Максимум 10 подзадач
        # Используем упрощенный сериализатор для подзадач
        return [
            {
                'id': subtask.id,
                'title': subtask.title,
                'status': subtask.status,
                'priority': subtask.priority,
                'assignee': CRMUserSerializer(subtask.assignee).data if subtask.assignee else None,
                'due_date': subtask.due_date,
                'subtasks_count': subtask.subtasks.count()
            }
            for subtask in subtasks
        ]
    
    def validate(self, data):
        """Дополнительная валидация данных задачи"""
        # Проверяем что дата окончания не раньше даты начала
        if data.get('start_date') and data.get('due_date'):
            if data['due_date'] < data['start_date']:
                raise serializers.ValidationError(
                    "Дата окончания не может быть раньше даты начала"
                )
        # Проверяем, что оценка времени не отрицательная
        if data.get('estimated_hours') is not None:
            try:
                if float(data['estimated_hours']) < 0:
                    raise serializers.ValidationError("Оценка времени не может быть отрицательной")
            except (TypeError, ValueError):
                raise serializers.ValidationError("Некорректное значение оценки времени")
        # Если указан основной исполнитель, а список множественных исполнителей задан — приводим к согласованности
        assignee_id = data.get('assignee_id')
        assignee_ids = data.get('assignee_ids')
        if assignee_id and isinstance(assignee_ids, list) and assignee_id not in assignee_ids:
            assignee_ids.append(assignee_id)
            data['assignee_ids'] = assignee_ids
        
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        
        # Получаем project_id и organization_id
        project_id = validated_data.pop('project_id', None)
        organization_id = validated_data.pop('organization_id', None)
        assignee_ids = validated_data.pop('assignee_ids', None)
        
        if not project_id:
            raise serializers.ValidationError('project_id is required')
        
        try:
            project = Project.objects.get(id=project_id)
            # Автоматически устанавливаем organization из проекта
            organization = project.organization
        except Project.DoesNotExist:
            raise serializers.ValidationError('Проект не найден')
        
        # Проверяем права на проект
        if not (
            project.owner == user or 
            project.manager == user or
            project.team_members.filter(id=user.id).exists() or
            (organization.owner == user) or
            OrganizationMember.objects.filter(organization=organization, user=user, status='accepted').exists()
        ):
            raise serializers.ValidationError('У вас нет прав на создание задач в этом проекте')
        
        # Валидируем parent_id если указан
        parent_id = validated_data.pop('parent_id', None)
        if parent_id in ['', 0]:
            parent_id = None
        if parent_id:
            try:
                parent_task = Task.objects.get(id=parent_id)
                if parent_task.project_id != project_id:
                    raise serializers.ValidationError('Родительская задача должна принадлежать тому же проекту')
                validated_data['parent'] = parent_task
            except Task.DoesNotExist:
                raise serializers.ValidationError('Родительская задача не найдена')
        
        validated_data['project'] = project
        validated_data['creator'] = user
        validated_data['organization'] = organization
        
        # Защита от дублей названий внутри проекта (и той же ветки родителя)
        normalized_title = (validated_data.get('title') or '').strip()
        if normalized_title:
            q = Task.objects.filter(project_id=project.id)
            parent_pk = validated_data.get('parent').id if validated_data.get('parent') else None
            if parent_pk is None:
                q = q.filter(parent__isnull=True)
            else:
                q = q.filter(parent_id=parent_pk)
            # Сначала грубо по case-insensitive
            possibles = list(q.filter(title__iexact=normalized_title))
            # Дополнительная защита: сравнение по свернутым пробелам и регистру
            def norm(s: str) -> str:
                return ' '.join((s or '').split()).casefold()
            normalized_target = norm(normalized_title)
            for t in possibles or q[:50]:
                if norm(t.title) == normalized_target:
                    raise serializers.ValidationError({'title': 'Задача с таким названием уже существует в этом проекте/ветке'})

        # Гарантируем, что все исполнители состоят в проекте/команде (автодобавление)
        if assignee_ids:
            missing_user_ids = [
                uid for uid in assignee_ids
                if not ProjectMember.objects.filter(project=project, user_id=uid).exists()
            ]
            if missing_user_ids:
                # Добавляем в участники проекта
                for uid in missing_user_ids:
                    try:
                        ProjectMember.objects.create(project=project, user_id=uid, role='member')
                    except Exception:
                        pass
                # Синхронизируем с командой проекта, если есть
                if getattr(project, 'team', None):
                    for uid in missing_user_ids:
                        try:
                            TeamMember.objects.get_or_create(team=project.team, user_id=uid, defaults={'role': 'member'})
                        except Exception:
                            pass

        # Также проверим основного исполнителя
        primary_assignee_id = validated_data.get('assignee_id')
        if primary_assignee_id and not ProjectMember.objects.filter(project=project, user_id=primary_assignee_id).exists():
            try:
                ProjectMember.objects.create(project=project, user_id=primary_assignee_id, role='member')
            except Exception:
                pass
            if getattr(project, 'team', None):
                try:
                    TeamMember.objects.get_or_create(team=project.team, user_id=primary_assignee_id, defaults={'role': 'member'})
                except Exception:
                    pass

        task = super().create(validated_data)

        # Устанавливаем множественных исполнителей, если переданы
        if assignee_ids:
            users_qs = User.objects.filter(id__in=assignee_ids)
            task.assignees.set(users_qs)

            # Создаем записи TaskAssignee с ролью 'assignee' для синхронизации
            existing_links = set(
                TaskAssignee.objects.filter(task=task, role='assignee').values_list('user_id', flat=True)
            )
            target_ids = set(assignee_ids)
            to_create = target_ids - existing_links
            TaskAssignee.objects.bulk_create([
                TaskAssignee(task=task, user_id=uid, role='assignee', assigned_by=user)
                for uid in to_create
            ], ignore_conflicts=True)

        return task

    def get_assignee_links(self, obj):
        links = TaskAssignee.objects.filter(task=obj).select_related('user')
        return [
            {
                'user': CRMUserSerializer(link.user).data,
                'role': link.role,
                'assigned_at': link.assigned_at,
            }
            for link in links
        ]
    
    def update(self, instance, validated_data):
        """Обновление задачи с валидацией иерархии"""
        user = self.context['request'].user
        # Нормализуем пустые строки -> None
        for key in ['start_date', 'due_date']:
            if key in validated_data and validated_data.get(key) == '':
                validated_data[key] = None
        
        # Проверяем права на обновление
        if not (
            instance.creator == user or
            instance.assignee == user or
            instance.project.owner == user or
            instance.project.manager == user or
            instance.project.team_members.filter(id=user.id).exists() or
            (instance.organization and instance.organization.owner == user) or
            (instance.organization and OrganizationMember.objects.filter(organization=instance.organization, user=user, status='accepted').exists())
        ):
            raise serializers.ValidationError('У вас нет прав на обновление этой задачи')
        
        # Валидируем изменение parent_id
        new_parent_id = validated_data.pop('parent_id', None)
        if new_parent_id in ['', 0]:
            new_parent_id = None
        if new_parent_id is not None and new_parent_id != (instance.parent_id if instance.parent else None):
            if new_parent_id:
                try:
                    new_parent = Task.objects.get(id=new_parent_id)
                    if new_parent.project_id != instance.project_id:
                        raise serializers.ValidationError('Родительская задача должна принадлежать тому же проекту')
                    validated_data['parent'] = new_parent
                except Task.DoesNotExist:
                    raise serializers.ValidationError('Родительская задача не найдена')
            else:
                validated_data['parent'] = None
        
        assignee_ids = validated_data.pop('assignee_ids', None)
        # Если меняем список исполнителей — гарантируем членство (автодобавление)
        if assignee_ids is not None:
            missing_user_ids = [
                uid for uid in assignee_ids
                if not ProjectMember.objects.filter(project=instance.project, user_id=uid).exists()
            ]
            if missing_user_ids:
                for uid in missing_user_ids:
                    try:
                        ProjectMember.objects.create(project=instance.project, user_id=uid, role='member')
                    except Exception:
                        pass
                if getattr(instance.project, 'team', None):
                    for uid in missing_user_ids:
                        try:
                            TeamMember.objects.get_or_create(team=instance.project.team, user_id=uid, defaults={'role': 'member'})
                        except Exception:
                            pass

        # Аналогично проверяем возможную смену основного исполнителя
        primary_assignee_id = validated_data.get('assignee_id')
        if primary_assignee_id and not ProjectMember.objects.filter(project=instance.project, user_id=primary_assignee_id).exists():
            try:
                ProjectMember.objects.create(project=instance.project, user_id=primary_assignee_id, role='member')
            except Exception:
                pass
            if getattr(instance.project, 'team', None):
                try:
                    TeamMember.objects.get_or_create(team=instance.project.team, user_id=primary_assignee_id, defaults={'role': 'member'})
                except Exception:
                    pass

        # Защита от дублей названий внутри проекта (и той же ветки родителя) при обновлении
        if 'title' in validated_data or 'parent' in validated_data:
            new_title = (validated_data.get('title', instance.title) or '').strip()
            parent_obj = validated_data.get('parent', instance.parent)
            q = Task.objects.filter(project_id=instance.project_id)
            if parent_obj is None:
                q = q.filter(parent__isnull=True)
            else:
                q = q.filter(parent_id=parent_obj.id)
            q = q.exclude(id=instance.id)
            possibles = list(q.filter(title__iexact=new_title))
            def norm(s: str) -> str:
                return ' '.join((s or '').split()).casefold()
            new_norm = norm(new_title)
            for t in possibles or q[:50]:
                if norm(t.title) == new_norm:
                    raise serializers.ValidationError({'title': 'Задача с таким названием уже существует в этом проекте/ветке'})

        task = super().update(instance, validated_data)

        # Синхронизация исполнителей (M2M) с записями TaskAssignee (роль "assignee")
        if assignee_ids is not None:
            users_qs = User.objects.filter(id__in=assignee_ids)
            task.assignees.set(users_qs)

            # Создаем недостающие ссылки TaskAssignee с ролью 'assignee'
            existing_links = set(
                TaskAssignee.objects.filter(task=task, role='assignee').values_list('user_id', flat=True)
            )
            target_ids = set(assignee_ids)
            to_create = target_ids - existing_links
            to_delete = existing_links - target_ids

            TaskAssignee.objects.bulk_create([
                TaskAssignee(task=task, user_id=uid, role='assignee', assigned_by=user)
                for uid in to_create
            ], ignore_conflicts=True)

            if to_delete:
                TaskAssignee.objects.filter(task=task, role='assignee', user_id__in=list(to_delete)).delete()

        return task

class TaskCalendarSerializer(serializers.ModelSerializer):
    """Сериализатор задач для календаря"""
    assignee = CRMUserSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'assignee', 'status',
            'priority', 'start_date', 'due_date', 'created_at'
        ]


class TaskKanbanSerializer(serializers.ModelSerializer):
    """Сериализатор задач для канбан доски"""
    assignee = CRMUserSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'assignee', 'status',
            'priority', 'due_date', 'kanban_order', 'estimated_hours'
        ]