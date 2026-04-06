from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0007_assignment_submission_type_submission_text_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='allow_late_submission',
            field=models.BooleanField(default=True),
        ),
    ]

