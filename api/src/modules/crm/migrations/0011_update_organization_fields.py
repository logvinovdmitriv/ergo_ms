from django.db import migrations, models


def migrate_visibility(apps, schema_editor):
    Organization = apps.get_model('crm', 'Organization')
    Organization.objects.filter(visibility='by_invite').update(visibility='internal')


class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0010_ensure_owner_membership'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='logo_url',
            field=models.URLField(default='', blank=True, verbose_name='Логотип'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='visibility',
            field=models.CharField(max_length=20, choices=[('public', 'public'), ('internal', 'internal'), ('private', 'private')], default='private', verbose_name='Видимость'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='default_role',
            field=models.CharField(max_length=20, choices=[('member', 'member'), ('admin', 'admin'), ('viewer', 'viewer')], default='member', verbose_name='Роль по умолчанию'),
        ),
        migrations.RunPython(migrate_visibility, reverse_code=migrations.RunPython.noop),
    ]
