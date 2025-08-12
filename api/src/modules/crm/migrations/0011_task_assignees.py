from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0010_add_subtasks_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='assignees',
            field=models.ManyToManyField(blank=True, related_name='multi_assigned_tasks', to=settings.AUTH_USER_MODEL, verbose_name='Исполнители'),
        ),
    ]


