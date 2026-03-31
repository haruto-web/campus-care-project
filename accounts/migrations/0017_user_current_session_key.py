from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_auditlog_hash_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='current_session_key',
            field=models.CharField(blank=True, default='', max_length=40),
        ),
    ]

