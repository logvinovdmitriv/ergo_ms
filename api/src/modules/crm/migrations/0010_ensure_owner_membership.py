from django.db import migrations

def ensure_owner_membership(apps, schema_editor):
    Organization = apps.get_model('crm', 'Organization')
    OrganizationMember = apps.get_model('crm', 'OrganizationMember')
    db = schema_editor.connection.alias

    for org in Organization.objects.using(db).all():
        if not org.owner_id:
            continue
        OrganizationMember.objects.using(db).update_or_create(
            organization_id=org.id,
            user_id=org.owner_id,
            defaults={'role': 'owner', 'status': 'accepted'}
        )

class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0009_organizationinvite_role'),
    ]
    operations = [
        migrations.RunPython(ensure_owner_membership, migrations.RunPython.noop),
    ]
