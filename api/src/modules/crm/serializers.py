from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Project, ProjectMember, Task, TaskComment, TaskAttachment, TimeLog,
    ProjectStatus, ProjectPriority, TaskStatus, TaskPriority,
    Organization, OrganizationMember, OrganizationInvite
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
    user_id = serializers.IntegerField(write_only=True, required=False)
    invited_by = CRMUserSerializer(read_only=True)

    class Meta:
        model = OrganizationMember
        fields = ['id', 'user', 'user_id', 'role', 'status', 'invited_by', 'invited_at', 'responded_at']
        read_only_fields = ['invited_by', 'invited_at', 'responded_at']

class OrganizationSerializer(serializers.ModelSerializer):
    # READ
    owner = CRMUserSerializer(read_only=True)
    memberships = OrganizationMemberSerializer(many=True, read_only=True)
    my_role = serializers.SerializerMethodField(read_only=True)
    members_count = serializers.SerializerMethodField(read_only=True)

    # WRITE
    owner_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    # «Мягкие» поля — разрешаем пустые, но logo_url ниже преобразуем к '', чтобы не было NULL
    logo_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    website = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    country = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    timezone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    industry = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    billing_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    billing_vat = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    billing_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    visibility = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    default_role = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    status = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'description', 'logo_url', 'industry', 'website',
            'email', 'phone', 'country', 'timezone', 'address',
            'billing_name', 'billing_vat', 'billing_address',
            'owner', 'owner_id', 'memberships', 'my_role', 'members_count',
            'visibility', 'default_role', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    # ----- computed -----
    def get_my_role(self, obj):
        req = self.context.get('request')
        user = getattr(req, 'user', None)
        if not user or not user.is_authenticated:
            return None
        if obj.owner_id == user.id:
            return 'owner'
        rel = obj.memberships.filter(user_id=user.id, status='accepted').only('role').first()
        return rel.role if rel else None

    def get_members_count(self, obj):
        return obj.memberships.count()

    # ----- validators -----
    def validate_default_role(self, value):
        # пустое — не трогаем поле
        if value in (None, ''):
            return None
        # если прилетел "owner" — тихо переводим в member
        if value == 'owner':
            return 'member'
        allowed = {'member', 'admin', 'viewer'}
        if value not in allowed:
            # можно тоже схлопнуть в member, но оставлю явную ошибку:
            raise serializers.ValidationError(
                'Недопустимое значение. Разрешено: member, admin, viewer.'
            )
        return value


    # ----- helpers -----
    @staticmethod
    def _normalize_soft_fields(data: dict) -> dict:
        """
        Не допускаем NULL там, где в БД NOT NULL. Превращаем None -> '' для logo_url (и опционально для других).
        """
        if 'logo_url' in data and data['logo_url'] is None:
            data['logo_url'] = ''  # чтобы не ловить IntegrityError на NOT NULL
        return data

    # ----- update / transfer owner -----
    def update(self, instance, validated_data):
        # перенос владельца
        new_owner_id = validated_data.pop('owner_id', None)
        req = self.context.get('request')
        if new_owner_id is not None and new_owner_id != instance.owner_id:
            if not req or not (req.user.is_superuser or req.user.id == instance.owner_id):
                raise serializers.ValidationError({'owner_id': 'Только владелец или суперпользователь могут менять владельца.'})
            try:
                new_owner = User.objects.get(pk=new_owner_id)
            except User.DoesNotExist:
                raise serializers.ValidationError({'owner_id': 'Пользователь не найден.'})
            instance.owner = new_owner
            instance.save(update_fields=['owner'])
            OrganizationMember.objects.update_or_create(
                organization=instance, user=new_owner,
                defaults={'role': 'owner', 'status': 'accepted'}
            )

        validated_data = self._normalize_soft_fields(validated_data)
        return super().update(instance, validated_data)

    def create(self, validated_data):
        owner_id = validated_data.pop('owner_id', None)
        validated_data = self._normalize_soft_fields(validated_data)
        obj = super().create(validated_data)
        if owner_id:
            try:
                owner = User.objects.get(pk=owner_id)
            except User.DoesNotExist:
                raise serializers.ValidationError({'owner_id': 'Пользователь не найден.'})
            obj.owner = owner
            obj.save(update_fields=['owner'])
            OrganizationMember.objects.update_or_create(
                organization=obj, user=owner,
                defaults={'role': 'owner', 'status': 'accepted'}
            )
        return obj


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
            'organization', 'organization_id', 'memberships', 'status', 'priority', 'start_date', 'end_date',
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
        organization_id = validated_data.pop('organization_id', None)
        if not organization_id:
            raise serializers.ValidationError('organization_id is required')
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise serializers.ValidationError('Организация не найдена')

        if not (organization.owner == user or OrganizationMember.objects.filter(organization=organization, user=user, status='accepted').exists()):
            raise serializers.ValidationError('Вы не являетесь участником организации')

        validated_data['owner'] = user
        validated_data['organization'] = organization
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

    comment_count = serializers.SerializerMethodField()
    attachment_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'assignee', 'creator',
            'status', 'priority', 'start_date', 'due_date', 'completed_at',
            'created_at', 'updated_at', 'estimated_hours', 'actual_hours',
            'kanban_order', 'comment_count', 'attachment_count',
            'status_ref', 'priority_ref', 'current_status', 'current_priority',
            'status_display', 'priority_display', 'parent'
        ]

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_attachment_count(self, obj):
        return obj.attachments.count()


class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор задачи"""
    assignee = CRMUserSerializer(read_only=True)
    creator = CRMUserSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)
    assignee_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    project_id = serializers.IntegerField(write_only=True)
    organization = OrganizationSerializer(read_only=True)
    organization_id = serializers.IntegerField(write_only=True)
    parent = TaskListSerializer(read_only=True)
    parent_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    subtasks = TaskListSerializer(many=True, read_only=True)

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
            'creator', 'status', 'priority', 'start_date', 'due_date', 'completed_at',
            'created_at', 'updated_at', 'estimated_hours', 'actual_hours', 'kanban_order',
            'comments', 'attachments', 'time_logs', 'total_time', 'parent', 'parent_id', 'subtasks',
            'status_ref', 'priority_ref', 'status_ref_id', 'priority_ref_id',
            'current_status', 'current_priority', 'status_display', 'priority_display'
        ]

    def get_total_time(self, obj):
        return sum(log.hours for log in obj.time_logs.all())

    def validate(self, data):
        """Дополнительная валидация данных задачи"""
        # Проверяем что дата окончания не раньше даты начала
        if data.get('start_date') and data.get('due_date'):
            if data['due_date'] < data['start_date']:
                raise serializers.ValidationError(
                    "Дата окончания не может быть раньше даты начала"
                )

        return data

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

        project_id = validated_data.pop('project_id', None)
        try:
            project = Project.objects.get(id=project_id, organization=organization)
        except Project.DoesNotExist:
            raise serializers.ValidationError('Проект не найден в организации')

        validated_data['project'] = project
        validated_data['creator'] = user
        validated_data['organization'] = organization
        return super().create(validated_data)

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