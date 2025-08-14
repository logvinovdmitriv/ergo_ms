from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings
from datetime import timedelta
import secrets

User = get_user_model()

class ProjectStatus(models.Model):
    """Статусы проектов"""
    name = models.CharField(max_length=100, verbose_name='Название статуса')
    code = models.CharField(max_length=50, unique=True, verbose_name='Код статуса')
    description = models.TextField(blank=True, verbose_name='Описание')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='Цвет')
    order = models.IntegerField(default=0, verbose_name='Порядок сортировки')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_default = models.BooleanField(default=False, verbose_name='По умолчанию')
    is_final = models.BooleanField(default=False, verbose_name='Финальный статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Статус проекта'
        verbose_name_plural = 'Статусы проектов'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class ProjectPriority(models.Model):
    """Приоритеты проектов"""
    name = models.CharField(max_length=100, verbose_name='Название приоритета')
    code = models.CharField(max_length=50, unique=True, verbose_name='Код приоритета')
    description = models.TextField(blank=True, verbose_name='Описание')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='Цвет')
    level = models.IntegerField(default=1, verbose_name='Уровень приоритета')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_default = models.BooleanField(default=False, verbose_name='По умолчанию')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Приоритет проекта'
        verbose_name_plural = 'Приоритеты проектов'
        ordering = ['level', 'name']

    def __str__(self):
        return self.name


class TaskStatus(models.Model):
    """Статусы задач"""
    name = models.CharField(max_length=100, verbose_name='Название статуса')
    code = models.CharField(max_length=50, unique=True, verbose_name='Код статуса')
    description = models.TextField(blank=True, verbose_name='Описание')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='Цвет')
    order = models.IntegerField(default=0, verbose_name='Порядок сортировки')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_default = models.BooleanField(default=False, verbose_name='По умолчанию')
    is_final = models.BooleanField(default=False, verbose_name='Финальный статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Статус задачи'
        verbose_name_plural = 'Статусы задач'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class TaskPriority(models.Model):
    """Приоритеты задач"""
    name = models.CharField(max_length=100, verbose_name='Название приоритета')
    code = models.CharField(max_length=50, unique=True, verbose_name='Код приоритета')
    description = models.TextField(blank=True, verbose_name='Описание')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='Цвет')
    level = models.IntegerField(default=1, verbose_name='Уровень приоритета')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_default = models.BooleanField(default=False, verbose_name='По умолчанию')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Приоритет задачи'
        verbose_name_plural = 'Приоритеты задач'
        ordering = ['level', 'name']

    def __str__(self):
        return self.name

# Организации

class Organization(models.Model):
    """Организация в CRM"""
    VISIBILITY_CHOICES = [
        ('private', 'private'),
        ('by_invite', 'by_invite'),
    ]
    ROLE_CHOICES = [
        ('member', 'member'),
        ('viewer', 'viewer'),
    ]
    STATUS_CHOICES = [
        ('active', 'active'),
        ('archived', 'archived'),
    ]

    name = models.CharField(max_length=255, verbose_name='Название организации')
    slug = models.SlugField(unique=True, blank=True, verbose_name='Слаг')
    description = models.TextField(blank=True, verbose_name='Описание')
    logo_url = models.URLField(blank=True, verbose_name='Логотип')
    industry = models.CharField(max_length=255, blank=True, verbose_name='Отрасль')
    website = models.URLField(blank=True, verbose_name='Сайт')
    email = models.EmailField(blank=True, verbose_name='Email')
    phone = models.CharField(max_length=50, blank=True, verbose_name='Телефон')
    country = models.CharField(max_length=100, blank=True, verbose_name='Страна')
    timezone = models.CharField(max_length=50, blank=True, verbose_name='Часовой пояс')
    address = models.CharField(max_length=255, blank=True, verbose_name='Адрес')
    billing_name = models.CharField(max_length=255, blank=True, verbose_name='Плательщик')
    billing_vat = models.CharField(max_length=50, blank=True, verbose_name='НДС')
    billing_address = models.CharField(max_length=255, blank=True, verbose_name='Адрес для счетов')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_organizations', verbose_name='Владелец')
    members = models.ManyToManyField(User, through='OrganizationMember', related_name='organizations', through_fields=('organization', 'user'), verbose_name='Участники')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='by_invite', verbose_name='Видимость')
    default_role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member', verbose_name='Роль по умолчанию')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Гарантируем уникальный slug. Если slug уже задан (например, при создании),
        # мы его сохраняем, лишь при конфликте добавляем суффикс -2, -3, ...
        base_slug = self.slug or slugify(self.name) or 'organization'
        candidate = base_slug
        suffix = 1
        # Исключаем текущий объект при проверке, чтобы не трогать slug при обновлении
        while Organization.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
            suffix += 1
            candidate = f"{base_slug}-{suffix}"
        self.slug = candidate
        super().save(*args, **kwargs)


class OrganizationMember(models.Model):
    """Участник организации"""

    ROLE_CHOICES = [
        ('owner', 'owner'),
        ('admin', 'admin'),
        ('member', 'member'),
        ('viewer', 'viewer'),
    ]
    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('accepted', 'accepted'),
        ('declined', 'declined'),
        ('revoked', 'revoked'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='organization_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member', verbose_name='Роль')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='organization_invites_sent',
        verbose_name='Кем приглашён',
    )
    invited_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата приглашения')
    responded_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата ответа')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Участник организации'
        verbose_name_plural = 'Участники организаций'
        unique_together = ['organization', 'user']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.organization.name}"


class Team(models.Model):
    """Команда внутри организации"""
    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('archived', 'Архивирована'),
    ]

    name = models.CharField(max_length=255, verbose_name='Название команды')
    description = models.TextField(blank=True, verbose_name='Описание')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='teams', verbose_name='Организация')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_teams', verbose_name='Владелец команды')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_teams', verbose_name='Менеджер команды')
    members = models.ManyToManyField(User, through='TeamMember', related_name='teams', verbose_name='Участники')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class TeamMember(models.Model):
    """Участник команды"""
    ROLE_CHOICES = [
        ('member', 'Участник'),
        ('lead', 'Лидер'),
        ('observer', 'Наблюдатель'),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member', verbose_name='Роль')
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата присоединения')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Участник команды'
        verbose_name_plural = 'Участники команд'
        unique_together = ['team', 'user']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.team.name}"
class OrganizationInvite(models.Model):
    """Приглашение в организацию"""

    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('accepted', 'accepted'),
        ('declined', 'declined'),
        ('expired', 'expired'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='invites')
    email = models.EmailField(verbose_name='Email')
    role = models.CharField(
        max_length=20,
        choices=OrganizationMember.ROLE_CHOICES,
        default='member',
        verbose_name='Роль'
    )
    token = models.CharField(max_length=64, unique=True, editable=False)
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='Истекает')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organization_invites', verbose_name='Пригласивший')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    responded_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата ответа')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Приглашение в организацию'
        verbose_name_plural = 'Приглашения в организации'

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_hex(16)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} -> {self.organization.name}"
      
class Project(models.Model):
    """Общий проект (не стратегический)"""
    PROJECT_STATUS_CHOICES = [
        ('planning', 'Планирование'),
        ('active', 'Активный'),
        ('on_hold', 'Приостановлен'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('urgent', 'Срочный'),
    ]
    name = models.CharField(max_length=255, verbose_name='Название проекта')
    description = models.TextField(blank=True, verbose_name='Описание')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='projects', null=True, blank=True, verbose_name='Организация')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects', verbose_name='Владелец проекта')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_projects', verbose_name='Менеджер проекта')
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='projects', verbose_name='Команда')
    team_members = models.ManyToManyField(User, through='ProjectMember', related_name='project_teams', verbose_name='Участники команды')

    # Новые поля с внешними ключами
    status_ref = models.ForeignKey(ProjectStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects', verbose_name='Статус (новый)')
    priority_ref = models.ForeignKey(ProjectPriority, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects', verbose_name='Приоритет (новый)')

    # Старые поля для обратной совместимости
    status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES, default='planning', verbose_name='Статус')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name='Приоритет')

    start_date = models.DateField(null=True, blank=True, verbose_name='Дата начала')
    end_date = models.DateField(null=True, blank=True, verbose_name='Дата окончания')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='Цвет проекта')  # Для календаря

    class Meta:
        app_label = 'crm'
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def current_status(self):
        """Получить текущий статус (приоритет новому полю)"""
        return self.status_ref.code if self.status_ref else self.status

    @property
    def current_priority(self):
        """Получить текущий приоритет (приоритет новому полю)"""
        return self.priority_ref.code if self.priority_ref else self.priority

    @property
    def status_display(self):
        """Получить отображаемое название статуса"""
        return self.status_ref.name if self.status_ref else dict(self.PROJECT_STATUS_CHOICES).get(self.status, self.status)

    @property
    def priority_display(self):
        """Получить отображаемое название приоритета"""
        return self.priority_ref.name if self.priority_ref else dict(self.PRIORITY_CHOICES).get(self.priority, self.priority)


class ProjectMember(models.Model):
    """Участник проекта"""
    ROLE_CHOICES = [
        ('member', 'Участник'),
        ('lead', 'Ведущий'),
        ('observer', 'Наблюдатель'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member', verbose_name='Роль')
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата присоединения')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Участник проекта'
        verbose_name_plural = 'Участники проектов'
        unique_together = ['project', 'user']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.project.name}"


class Task(models.Model):
    """Задача"""
    # Обратная совместимость - старые choices остаются как fallback
    TASK_STATUS_CHOICES = [
        ('todo', 'К выполнению'),
        ('in_progress', 'В работе'),
        ('review', 'На проверке'),
        ('done', 'Выполнено'),
        ('cancelled', 'Отменено'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('urgent', 'Срочный'),
    ]

    title = models.CharField(max_length=255, verbose_name='Название задачи')
    description = models.TextField(blank=True, verbose_name='Описание')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', verbose_name='Проект')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True, verbose_name='Организация')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks', verbose_name='Исполнитель')
    assignees = models.ManyToManyField(User, blank=True, related_name='multi_assigned_tasks', verbose_name='Исполнители')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks', verbose_name='Создатель')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks', verbose_name='Родительская задача')
    # Новые поля с внешними ключами
    status_ref = models.ForeignKey(TaskStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name='Статус (новый)')
    priority_ref = models.ForeignKey(TaskPriority, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name='Приоритет (новый)')

    # Старые поля для обратной совместимости
    status = models.CharField(max_length=20, choices=TASK_STATUS_CHOICES, default='todo', verbose_name='Статус')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name='Приоритет')
    start_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата начала')
    due_date = models.DateTimeField(null=True, blank=True, verbose_name='Срок выполнения')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата завершения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Оценка времени (часы)')
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Фактическое время (часы)')
    kanban_order = models.IntegerField(default=0, verbose_name='Порядок в канбан')
    subtasks_count = models.IntegerField(default=0, verbose_name='Количество подзадач')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['kanban_order', '-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['project', 'due_date']),
            models.Index(fields=['project', 'parent']),
        ]

    def __str__(self):
        return self.title

    @property
    def current_status(self):
        """Получить текущий статус (приоритет новому полю)"""
        return self.status_ref.code if self.status_ref else self.status

    @property
    def current_priority(self):
        """Получить текущий приоритет (приоритет новому полю)"""
        return self.priority_ref.code if self.priority_ref else self.priority

    @property
    def status_display(self):
        """Получить отображаемое название статуса"""
        return self.status_ref.name if self.status_ref else dict(self.TASK_STATUS_CHOICES).get(self.status, self.status)

    @property
    def priority_display(self):
        """Получить отображаемое название приоритета"""
        return self.priority_ref.name if self.priority_ref else dict(self.PRIORITY_CHOICES).get(self.priority, self.priority)


class TaskComment(models.Model):
    """Комментарий к задаче"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments', verbose_name='Задача')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_comments', verbose_name='Автор')
    content = models.TextField(verbose_name='Содержание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Комментарий к задаче'
        verbose_name_plural = 'Комментарии к задачам'
        ordering = ['created_at']

    def __str__(self):
        return f"Комментарий к {self.task.title}"


class TaskAttachment(models.Model):
    """Прикрепленный файл к задаче"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments', verbose_name='Задача')
    file = models.FileField(upload_to='task_attachments/', verbose_name='Файл')
    filename = models.CharField(max_length=255, verbose_name='Имя файла')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_attachments', verbose_name='Загрузил')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Прикрепленный файл'
        verbose_name_plural = 'Прикрепленные файлы'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.filename


class TaskAssignee(models.Model):
    """Связь задача-пользователь с ролью (owner/assignee/reviewer)"""
    ROLE_CHOICES = [
        ('owner', 'Владелец'),
        ('assignee', 'Исполнитель'),
        ('reviewer', 'Ревьюер'),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignee_links')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_assignees')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='assignee')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks_history')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'crm'
        verbose_name = 'Назначение задачи'
        verbose_name_plural = 'Назначения задач'
        unique_together = [('task', 'user', 'role')]


class TaskTree(models.Model):
    """Closure table для дерева задач"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='tree_entries')
    ancestor = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='descendant_entries')
    depth = models.IntegerField()

    class Meta:
        app_label = 'crm'
        verbose_name = 'Связь дерева задач'
        verbose_name_plural = 'Связи дерева задач'
        unique_together = [('task', 'ancestor')]
        indexes = [
            models.Index(fields=['task', 'ancestor']),
            models.Index(fields=['ancestor', 'depth']),
        ]

class TimeLog(models.Model):
    """Учет времени по задаче"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_logs', verbose_name='Задача')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_logs', verbose_name='Пользователь')
    description = models.TextField(blank=True, verbose_name='Описание работы')
    hours = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Количество часов')
    date = models.DateField(verbose_name='Дата работы')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания записи')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Учет времени'
        verbose_name_plural = 'Учет времени'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.task.title} - {self.hours}ч"

# Создавайте свои модели здесь