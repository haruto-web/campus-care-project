from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_user_messaging_suspended_until'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_number', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('year_level', models.CharField(choices=[('7', 'Grade 7'), ('8', 'Grade 8'), ('9', 'Grade 9'), ('10', 'Grade 10')], max_length=2)),
                ('section', models.CharField(blank=True, max_length=50)),
                ('password_hash', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('decided_at', models.DateTimeField(blank=True, null=True)),
                ('rejection_reason', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='processed_registration_requests', to='accounts.user')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='registrationrequest',
            constraint=models.UniqueConstraint(fields=('student_number', 'email'), name='uniq_registration_request_student_email'),
        ),
    ]
