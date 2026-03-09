from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_auditlog_user_admin_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApprovedStudent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_number', models.CharField(max_length=20, unique=True)),
                ('email', models.EmailField(unique=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('year_level', models.CharField(max_length=2, choices=[('7', 'Grade 7'), ('8', 'Grade 8'), ('9', 'Grade 9'), ('10', 'Grade 10')])),
                ('section', models.CharField(blank=True, max_length=50)),
                ('is_registered', models.BooleanField(default=False)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['last_name', 'first_name'],
            },
        ),
    ]
