from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_user_guardian_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='approvedstudent',
            name='is_suspended',
            field=models.BooleanField(default=False),
        ),
    ]
