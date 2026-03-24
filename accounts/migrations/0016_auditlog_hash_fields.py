from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_registrationrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditlog',
            name='entry_hash',
            field=models.CharField(blank=True, db_index=True, default='', max_length=64),
        ),
        migrations.AddField(
            model_name='auditlog',
            name='previous_hash',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
        migrations.AddField(
            model_name='auditlog',
            name='signature_version',
            field=models.CharField(blank=True, default='hmac-sha256-v1', max_length=20),
        ),
    ]
