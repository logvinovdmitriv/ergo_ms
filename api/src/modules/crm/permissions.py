from rest_framework.permissions import BasePermission
from .models import Organization, OrganizationMember, OrgRole


def _get_membership(user, org: Organization):
    if not user or not user.is_authenticated:
        return None
    return OrganizationMember.objects.filter(user=user, organization=org).first()


class IsOrgObserverOrAbove(BasePermission):
    """Просмотр (observer+)"""

    def has_object_permission(self, request, view, obj):
        org = getattr(obj, 'organization', None) or getattr(
            getattr(obj, 'project', None), 'organization', None
        )
        if not org:
            return False
        m = _get_membership(request.user, org)
        return bool(m)


class IsOrgMemberOrAbove(BasePermission):
    """Действия, требующие членства"""

    def has_object_permission(self, request, view, obj):
        org = getattr(obj, 'organization', None) or getattr(
            getattr(obj, 'project', None), 'organization', None
        )
        if not org:
            return False
        m = _get_membership(request.user, org)
        return bool(m and m.role in {OrgRole.MEMBER, OrgRole.ADMIN, OrgRole.OWNER})


class IsOrgAdminOrOwner(BasePermission):
    """Приглашения, изменение ролей, редактирование организации"""

    def has_object_permission(self, request, view, obj):
        org = obj if hasattr(obj, 'memberships') else getattr(obj, 'organization', None)
        if not org:
            return False
        m = _get_membership(request.user, org)
        return bool(m and m.role in {OrgRole.ADMIN, OrgRole.OWNER})
