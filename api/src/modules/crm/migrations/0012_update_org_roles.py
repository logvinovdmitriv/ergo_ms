from django.db import migrations, models


def forwards(apps, schema_editor):
    OrganizationMember = apps.get_model('crm', 'OrganizationMember')
    Organization = apps.get_model('crm', 'Organization')
    OrganizationMember.objects.filter(role='viewer').update(role='observer')
    Organization.objects.filter(default_role='viewer').update(default_role='observer')


def backwards(apps, schema_editor):
    OrganizationMember = apps.get_model('crm', 'OrganizationMember')
    Organization = apps.get_model('crm', 'Organization')
    OrganizationMember.objects.filter(role='observer').update(role='viewer')
    Organization.objects.filter(default_role='observer').update(default_role='viewer')


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0011_update_organization_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='default_role',
            field=models.CharField(max_length=16, choices=[('member', 'member'), ('admin', 'admin'), ('observer', 'observer')], default='member', verbose_name='Роль по умолчанию'),
        ),
        migrations.AlterField(
            model_name='organizationmember',
            name='role',
            field=models.CharField(max_length=16, choices=[('owner', 'owner'), ('admin', 'admin'), ('member', 'member'), ('observer', 'observer')], default='member', verbose_name='Роль'),
        ),
        migrations.AlterField(
            model_name='organizationinvite',
            name='role',
            field=models.CharField(max_length=20, choices=[('owner', 'owner'), ('admin', 'admin'), ('member', 'member'), ('observer', 'observer')], default='member', verbose_name='Роль'),
        ),
        migrations.RunPython(forwards, backwards),
    ]
