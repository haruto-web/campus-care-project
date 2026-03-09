from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def set_existing_admins_to_superadmin(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    User.objects.filter(role='admin', admin_role='').update(admin_role='superadmin')


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_otpcode'),
    ]

    operations = [
        # Use SeparateDatabaseAndState: raw SQL with IF NOT EXISTS for DB,
        # standard ORM operations for Django's migration state.
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
                        ALTER TABLE accounts_user
                        ADD COLUMN IF NOT EXISTS admin_role VARCHAR(20) NOT NULL DEFAULT '';
                    """,
                    reverse_sql="""
                        ALTER TABLE accounts_user DROP COLUMN IF EXISTS admin_role;
                    """,
                ),
                migrations.RunSQL(
                    sql="""
                        CREATE TABLE IF NOT EXISTS accounts_auditlog (
                            id BIGSERIAL PRIMARY KEY,
                            action VARCHAR(40) NOT NULL,
                            target_type VARCHAR(50) NOT NULL DEFAULT '',
                            target_id INTEGER NULL,
                            target_label VARCHAR(255) NOT NULL DEFAULT '',
                            extra_data JSONB NOT NULL DEFAULT '{}',
                            ip_address INET NULL,
                            timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                            actor_id INTEGER NULL REFERENCES accounts_user(id) ON DELETE SET NULL
                        );
                        CREATE INDEX IF NOT EXISTS accounts_au_timesta_idx ON accounts_auditlog (timestamp DESC);
                        CREATE INDEX IF NOT EXISTS accounts_au_actor_idx ON accounts_auditlog (actor_id);
                        CREATE INDEX IF NOT EXISTS accounts_au_action_idx ON accounts_auditlog (action);
                    """,
                    reverse_sql="DROP TABLE IF EXISTS accounts_auditlog;",
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='user',
                    name='admin_role',
                    field=models.CharField(
                        blank=True, default='',
                        choices=[
                            ('superadmin', 'Super Admin'),
                            ('admin', 'Admin'),
                            ('registrar', 'Registrar'),
                            ('data_viewer', 'Data Viewer'),
                        ],
                        max_length=20,
                    ),
                ),
                migrations.CreateModel(
                    name='AuditLog',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('action', models.CharField(max_length=40, choices=[
                            ('LOGIN', 'Login'), ('LOGOUT', 'Logout'), ('LOGIN_FAILED', 'Login Failed'),
                            ('USER_CREATED', 'User Created'), ('USER_DELETED', 'User Deleted'),
                            ('USER_UPDATED', 'User Updated'), ('CLASS_CREATED', 'Class Created'),
                            ('STUDENT_ENROLLED', 'Student Enrolled'),
                            ('STUDENT_REMOVED_FROM_CLASS', 'Student Removed from Class'),
                            ('ASSIGNMENT_CREATED', 'Assignment Created'),
                            ('ASSIGNMENT_DELETED', 'Assignment Deleted'),
                            ('SUBMISSION_GRADED', 'Submission Graded'), ('GRADE_CHANGED', 'Grade Changed'),
                            ('CONCERN_SUBMITTED', 'Concern Submitted'),
                            ('INTERVENTION_CREATED', 'Intervention Created'),
                            ('INTERVENTION_UPDATED', 'Intervention Updated'),
                            ('ALERT_RESOLVED', 'Alert Resolved'), ('REPORT_DOWNLOADED', 'Report Downloaded'),
                            ('AI_USED', 'AI Used'), ('ADMIN_ROLE_CHANGED', 'Admin Role Changed'),
                            ('MASS_DELETE', 'Mass Delete'),
                        ])),
                        ('target_type', models.CharField(blank=True, max_length=50)),
                        ('target_id', models.PositiveIntegerField(blank=True, null=True)),
                        ('target_label', models.CharField(blank=True, max_length=255)),
                        ('extra_data', models.JSONField(blank=True, default=dict)),
                        ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                        ('timestamp', models.DateTimeField(auto_now_add=True)),
                        ('actor', models.ForeignKey(
                            blank=True, null=True,
                            on_delete=django.db.models.deletion.SET_NULL,
                            related_name='audit_logs',
                            to=settings.AUTH_USER_MODEL,
                        )),
                    ],
                    options={'ordering': ['-timestamp']},
                ),
            ],
        ),
        migrations.RunPython(set_existing_admins_to_superadmin, migrations.RunPython.noop),
    ]
