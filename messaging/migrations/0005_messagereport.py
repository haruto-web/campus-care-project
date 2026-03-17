from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0004_alter_message_attachment'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(choices=[('harassment', 'Harassment / Bullying'), ('inappropriate', 'Inappropriate Content'), ('threat', 'Threat / Violence'), ('hate_speech', 'Hate Speech'), ('other', 'Other')], max_length=20)),
                ('details', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('reviewed', 'Reviewed'), ('resolved', 'Resolved'), ('dismissed', 'Dismissed')], default='pending', max_length=20)),
                ('consequence', models.CharField(blank=True, choices=[('warning', 'Issue Warning'), ('suspend', 'Suspend Messaging'), ('refer', 'Refer to Admin'), ('no_action', 'No Action Needed')], max_length=20)),
                ('counselor_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='messaging.message')),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='filed_reports', to=settings.AUTH_USER_MODEL)),
                ('resolved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resolved_reports', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
