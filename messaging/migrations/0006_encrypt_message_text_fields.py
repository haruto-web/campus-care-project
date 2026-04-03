from django.db import migrations

import campus_care.encrypted_fields


def _encrypt_model_fields(model, fields):
    for row in model.objects.all().only("pk", *fields).iterator():
        update_payload = {field: getattr(row, field) for field in fields}
        model.objects.filter(pk=row.pk).update(**update_payload)


def _encrypt_existing_message_text_fields(apps, schema_editor):
    Message = apps.get_model("messaging", "Message")
    MessageReport = apps.get_model("messaging", "MessageReport")

    _encrypt_model_fields(Message, ["body"])
    _encrypt_model_fields(MessageReport, ["details", "counselor_notes"])


class Migration(migrations.Migration):

    dependencies = [
        ("messaging", "0005_messagereport"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="body",
            field=campus_care.encrypted_fields.EncryptedTextField(blank=True),
        ),
        migrations.AlterField(
            model_name="messagereport",
            name="counselor_notes",
            field=campus_care.encrypted_fields.EncryptedTextField(blank=True),
        ),
        migrations.AlterField(
            model_name="messagereport",
            name="details",
            field=campus_care.encrypted_fields.EncryptedTextField(blank=True),
        ),
        migrations.RunPython(
            _encrypt_existing_message_text_fields, migrations.RunPython.noop
        ),
    ]
