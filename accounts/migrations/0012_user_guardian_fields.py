from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_approvedstudent'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='address',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='guardian_name',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='user',
            name='guardian_relation',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='user',
            name='guardian_occupation',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='user',
            name='profile_skipped_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
