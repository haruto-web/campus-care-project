from django.db import migrations

import campus_care.encrypted_fields


def _encrypt_model_fields(model, fields):
    for row in model.objects.all().only("pk", *fields).iterator():
        update_payload = {field: getattr(row, field) for field in fields}
        model.objects.filter(pk=row.pk).update(**update_payload)


def _encrypt_existing_wellness_text_fields(apps, schema_editor):
    WellnessCheckIn = apps.get_model("wellness", "WellnessCheckIn")
    RiskAssessment = apps.get_model("wellness", "RiskAssessment")
    TeacherConcern = apps.get_model("wellness", "TeacherConcern")
    Intervention = apps.get_model("wellness", "Intervention")
    Notification = apps.get_model("wellness", "Notification")
    Alert = apps.get_model("wellness", "Alert")

    _encrypt_model_fields(WellnessCheckIn, ["comments", "text_response"])
    _encrypt_model_fields(RiskAssessment, ["notes"])
    _encrypt_model_fields(TeacherConcern, ["description"])
    _encrypt_model_fields(Intervention, ["description", "notes", "outcome"])
    _encrypt_model_fields(Notification, ["message"])
    _encrypt_model_fields(Alert, ["message"])


class Migration(migrations.Migration):

    dependencies = [
        ("wellness", "0007_alter_intervention_scheduled_date_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="alert",
            name="message",
            field=campus_care.encrypted_fields.EncryptedTextField(),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="description",
            field=campus_care.encrypted_fields.EncryptedTextField(),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="notes",
            field=campus_care.encrypted_fields.EncryptedTextField(blank=True),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="outcome",
            field=campus_care.encrypted_fields.EncryptedTextField(blank=True),
        ),
        migrations.AlterField(
            model_name="notification",
            name="message",
            field=campus_care.encrypted_fields.EncryptedTextField(),
        ),
        migrations.AlterField(
            model_name="riskassessment",
            name="notes",
            field=campus_care.encrypted_fields.EncryptedTextField(blank=True),
        ),
        migrations.AlterField(
            model_name="teacherconcern",
            name="description",
            field=campus_care.encrypted_fields.EncryptedTextField(),
        ),
        migrations.AlterField(
            model_name="wellnesscheckin",
            name="comments",
            field=campus_care.encrypted_fields.EncryptedTextField(blank=True),
        ),
        migrations.AlterField(
            model_name="wellnesscheckin",
            name="text_response",
            field=campus_care.encrypted_fields.EncryptedTextField(
                blank=True, help_text="Optional: How are you feeling today?", null=True
            ),
        ),
        migrations.RunPython(
            _encrypt_existing_wellness_text_fields, migrations.RunPython.noop
        ),
    ]
