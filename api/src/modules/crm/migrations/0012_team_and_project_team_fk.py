from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0011_task_assignees'),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название команды')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('status', models.CharField(choices=[('active', 'Активна'), ('archived', 'Архивирована')], default='active', max_length=20, verbose_name='Статус')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teams', to='crm.organization', verbose_name='Организация')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_teams', to=settings.AUTH_USER_MODEL, verbose_name='Владелец команды')),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managed_teams', to=settings.AUTH_USER_MODEL, verbose_name='Менеджер команды')),
            ],
            options={'verbose_name': 'Команда', 'verbose_name_plural': 'Команды', 'ordering': ['name'], 'app_label': 'crm'},
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('member', 'Участник'), ('lead', 'Лидер'), ('observer', 'Наблюдатель')], default='member', max_length=20, verbose_name='Роль')),
                ('joined_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата присоединения')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='crm.team')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_memberships', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Участник команды', 'verbose_name_plural': 'Участники команд', 'app_label': 'crm'},
        ),
        migrations.AddField(
            model_name='team',
            name='members',
            field=models.ManyToManyField(related_name='teams', through='crm.TeamMember', to=settings.AUTH_USER_MODEL, verbose_name='Участники'),
        ),
        migrations.AlterUniqueTogether(
            name='teammember',
            unique_together={('team', 'user')},
        ),
        migrations.AddField(
            model_name='project',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='projects', to='crm.team', verbose_name='Команда'),
        ),
    ]


