from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_approvedstudent_is_suspended'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='messaging_suspended_until',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
