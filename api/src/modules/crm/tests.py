from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.test.utils import override_settings

from .models import Project, Task


@override_settings(ROOT_URLCONF="src.config.urls")
class BulkActionsTestCase(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_authenticate(self.user)
        self.project1 = Project.objects.create(name='P1', owner=self.user)
        self.project2 = Project.objects.create(name='P2', owner=self.user)
        self.task1 = Task.objects.create(title='T1', project=self.project1, creator=self.user)
        self.task2 = Task.objects.create(title='T2', project=self.project1, creator=self.user)
        self.task3 = Task.objects.create(title='T3', project=self.project2, creator=self.user)

    def test_bulk_delete_tasks(self):
        resp = self.client.delete('/crm/tasks/bulk-delete/', {'ids': [self.task1.id, self.task2.id]}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['deleted'], 2)
        self.assertFalse(Task.objects.filter(id__in=[self.task1.id, self.task2.id]).exists())

    def test_bulk_update_tasks_status(self):
        resp = self.client.patch('/crm/tasks/bulk-update/', {'ids': [self.task1.id, self.task2.id], 'status': 'done'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.task2.refresh_from_db()
        self.assertEqual(self.task1.status, 'done')
        self.assertEqual(self.task2.status, 'done')

    def test_bulk_delete_projects(self):
        resp = self.client.delete('/crm/projects/bulk-delete/', {'ids': [self.project1.id]}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(Project.objects.filter(id=self.project1.id).exists())

    def test_bulk_update_projects_status(self):
        resp = self.client.patch('/crm/projects/bulk-update/', {'ids': [self.project2.id], 'status': 'completed'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.project2.refresh_from_db()
        self.assertEqual(self.project2.status, 'completed')

    def test_bulk_delete_tasks_limit(self):
        ids = list(range(1, 1002))
        resp = self.client.delete('/crm/tasks/bulk-delete/', {'ids': ids}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

