from django.db import migrations

import campus_care.encrypted_fields


def _encrypt_existing_user_text_fields(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    for user in User.objects.all().only("pk", "about_me", "address").iterator():
        User.objects.filter(pk=user.pk).update(
            about_me=user.about_me,
            address=user.address,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0017_user_current_session_key"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="about_me",
            field=campus_care.encrypted_fields.EncryptedTextField(blank=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="address",
            field=campus_care.encrypted_fields.EncryptedTextField(blank=True),
        ),
        migrations.RunPython(
            _encrypt_existing_user_text_fields, migrations.RunPython.noop
        ),
    ]
