from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0009_organizationinvite_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='subtasks_count',
            field=models.IntegerField(default=0, verbose_name='Количество подзадач'),
        ),
    ]
