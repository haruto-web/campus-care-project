from django.conf import settings
from django.db import migrations, models
import hashlib
import hmac


AUDIT_TRIGGER_FN = 'accounts_prevent_auditlog_mutation'
AUDIT_TRIGGER_NAME = 'accounts_auditlog_immutable_trg'


def _otp_secret():
    return str(getattr(settings, 'OTP_SIGNING_KEY', settings.SECRET_KEY)).encode('utf-8')


def _hash_otp(value):
    code = str(value or '').strip()
    if not code:
        return ''
    return hmac.new(_otp_secret(), code.encode('utf-8'), hashlib.sha256).hexdigest()


def backfill_otp_hashes(apps, schema_editor):
    OTPCode = apps.get_model('accounts', 'OTPCode')
    qs = OTPCode.objects.exclude(code='').filter(code_hash='')
    for otp in qs.iterator():
        otp.code_hash = _hash_otp(otp.code)
        otp.code = ''
        otp.save(update_fields=['code_hash', 'code'])


def install_audit_immutability_trigger(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return

    schema_editor.execute(
        f"""
        CREATE OR REPLACE FUNCTION {AUDIT_TRIGGER_FN}()
        RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'DELETE' THEN
                RAISE EXCEPTION 'AuditLog rows are immutable and cannot be deleted';
            END IF;

            IF TG_OP = 'UPDATE' THEN
                IF OLD.entry_hash = ''
                   AND NEW.entry_hash <> ''
                   AND NEW.id = OLD.id
                   AND NEW.actor_id IS NOT DISTINCT FROM OLD.actor_id
                   AND NEW.action IS NOT DISTINCT FROM OLD.action
                   AND NEW.target_type IS NOT DISTINCT FROM OLD.target_type
                   AND NEW.target_id IS NOT DISTINCT FROM OLD.target_id
                   AND NEW.target_label IS NOT DISTINCT FROM OLD.target_label
                   AND NEW.extra_data IS NOT DISTINCT FROM OLD.extra_data
                   AND NEW.ip_address IS NOT DISTINCT FROM OLD.ip_address
                   AND NEW.previous_hash IS NOT DISTINCT FROM OLD.previous_hash
                   AND NEW.signature_version IS NOT DISTINCT FROM OLD.signature_version
                   AND NEW.timestamp IS NOT DISTINCT FROM OLD.timestamp
                THEN
                    RETURN NEW;
                END IF;

                RAISE EXCEPTION 'AuditLog rows are immutable and cannot be updated';
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    schema_editor.execute(
        f"""
        DROP TRIGGER IF EXISTS {AUDIT_TRIGGER_NAME} ON accounts_auditlog;
        CREATE TRIGGER {AUDIT_TRIGGER_NAME}
        BEFORE UPDATE OR DELETE ON accounts_auditlog
        FOR EACH ROW
        EXECUTE FUNCTION {AUDIT_TRIGGER_FN}();
        """
    )


def remove_audit_immutability_trigger(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return

    schema_editor.execute(f"DROP TRIGGER IF EXISTS {AUDIT_TRIGGER_NAME} ON accounts_auditlog;")
    schema_editor.execute(f"DROP FUNCTION IF EXISTS {AUDIT_TRIGGER_FN}();")


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_encrypt_user_profile_text_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otpcode',
            name='code',
            field=models.CharField(blank=True, default='', max_length=6),
        ),
        migrations.AddField(
            model_name='otpcode',
            name='code_hash',
            field=models.CharField(blank=True, db_index=True, default='', max_length=64),
        ),
        migrations.RunPython(backfill_otp_hashes, migrations.RunPython.noop),
        migrations.RunPython(install_audit_immutability_trigger, remove_audit_immutability_trigger),
    ]
