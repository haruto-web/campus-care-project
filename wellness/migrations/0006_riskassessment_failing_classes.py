from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wellness', '0005_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='riskassessment',
            name='failing_classes',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='riskassessment',
            name='risk_level',
            field=models.CharField(
                max_length=10,
                choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')],
            ),
        ),
        migrations.AlterField(
            model_name='alert',
            name='alert_type',
            field=models.CharField(
                max_length=30,
                choices=[
                    ('high_risk', 'High Risk Student'),
                    ('missing_assignments', 'Missing Assignments'),
                    ('low_attendance', 'Low Attendance'),
                    ('wellness_concern', 'Wellness Concern'),
                    ('teacher_concern', 'Teacher Concern'),
                    ('emotional_distress', 'Emotional Distress'),
                    ('ai_intervention', 'AI Intervention Created'),
                    ('failing_subjects', 'Failing in Specific Subjects'),
                ],
            ),
        ),
    ]
