from rest_framework import permissions
from django.db.models import Q
from src.modules.crm.models import Task, Project, Organization, Team


class TaskPermission(permissions.BasePermission):
    """
    Разрешения для управления задачами
    """
    
    def has_permission(self, request, view):
        """Проверяет общие разрешения для действий с задачами"""
        if not request.user.is_authenticated:
            return False
        
        # Разрешаем создание задач
        if request.method == 'POST':
            return True
        
        # Разрешаем чтение и обновление
        return True
    
    def has_object_permission(self, request, view, obj):
        """Проверяет разрешения для конкретной задачи"""
        user = request.user
        
        # Создатель задачи может делать всё
        if getattr(obj, 'creator', None) == user:
            return True
        
        # Исполнитель задачи может читать и обновлять (один или любой из множества)
        if (
            getattr(obj, 'assignee', None) == user or
            (hasattr(obj, 'assignees') and obj.assignees.filter(id=user.id).exists())
        ):
            if request.method in permissions.SAFE_METHODS:
                return True
            if request.method in ['PATCH', 'PUT']:
                return True
        
        # Проверяем права через проект
        if hasattr(obj, 'project') and obj.project:
            project = obj.project
            
            # Владелец проекта может управлять всеми задачами
            if project.owner == user:
                return True
            
            # Менеджер проекта может управлять задачами
            if project.manager == user:
                return True
            
            # Участник команды может читать задачи
            if project.team_members.filter(id=user.id).exists():
                if request.method in permissions.SAFE_METHODS:
                    return True
        
        # Проверяем права через организацию
        if hasattr(obj, 'organization') and obj.organization:
            org = obj.organization
            
            # Владелец организации может управлять всеми задачами
            if org.owner == user:
                return True
            
            # Администратор организации может управлять задачами
            if org.memberships.filter(
                user=user, 
                role='admin', 
                status='accepted'
            ).exists():
                return True
        
        # По умолчанию запрещаем
        return False


class ProjectPermission(permissions.BasePermission):
    """
    Разрешения для управления проектами
    """
    
    def has_permission(self, request, view):
        """Проверяет общие разрешения для действий с проектами"""
        if not request.user.is_authenticated:
            return False
        
        # Разрешаем создание проектов
        if request.method == 'POST':
            return True
        
        # Разрешаем чтение и обновление
        return True
    
    def has_object_permission(self, request, view, obj):
        """Проверяет разрешения для конкретного проекта"""
        user = request.user
        
        # Владелец проекта может делать всё
        if obj.owner == user:
            return True
        
        # Менеджер проекта может управлять проектом
        if obj.manager == user:
            return True
        
        # Участник команды может читать проект
        if obj.team_members.filter(id=user.id).exists():
            if request.method in permissions.SAFE_METHODS:
                return True
        
        # Проверяем права через организацию
        if hasattr(obj, 'organization') and obj.organization:
            org = obj.organization
            
            # Владелец организации может управлять всеми проектами
            if org.owner == user:
                return True
            
            # Администратор организации может управлять проектами
            if org.memberships.filter(
                user=user, 
                role='admin', 
                status='accepted'
            ).exists():
                return True
        
        # По умолчанию запрещаем
        return False


class OrganizationPermission(permissions.BasePermission):
    """
    Разрешения для управления организациями
    """
    
    def has_permission(self, request, view):
        """Проверяет общие разрешения для действий с организациями"""
        if not request.user.is_authenticated:
            return False
        
        # Разрешаем создание организаций
        if request.method == 'POST':
            return True
        
        # Разрешаем чтение и обновление
        return True
    
    def has_object_permission(self, request, view, obj):
        """Проверяет разрешения для конкретной организации"""
        user = request.user
        
        # Владелец организации может делать всё
        if obj.owner == user:
            return True
        
        # Администратор организации может управлять
        if obj.memberships.filter(
            user=user, 
            role='admin', 
            status='accepted'
        ).exists():
            return True
        
        # Участник организации может читать
        if obj.memberships.filter(
            user=user, 
            status='accepted'
        ).exists():
            if request.method in permissions.SAFE_METHODS:
                return True
        
        # По умолчанию запрещаем
        return False


class TeamPermission(permissions.BasePermission):
    """Права на управление командами"""
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        # владелец/менеджер команды: полный доступ
        if obj.owner == user or obj.manager == user:
            return True
        # участник команды: чтение
        if obj.members.filter(id=user.id).exists():
            return request.method in permissions.SAFE_METHODS
        # члены организации-родителя: чтение (через memberships)
        if obj.organization.memberships.filter(user=user, status='accepted').exists():
            return request.method in permissions.SAFE_METHODS
        return False
