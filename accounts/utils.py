import logging
import hashlib
import hmac
import json
import threading
from academics.models import Attendance
from django.conf import settings
from django.db import transaction
from django.core.cache import cache

logger = logging.getLogger('brighttrack.audit')
AUDIT_SIGNATURE_V1 = 'hmac-sha256-v1'
AUDIT_SIGNATURE_V2 = 'hmac-sha256-v2'


def calculate_attendance_rate(student, class_obj=None):
    """Calculate attendance rate for a student, optionally filtered by class."""
    qs = Attendance.objects.filter(student=student)
    if class_obj:
        qs = qs.filter(class_obj=class_obj)
    total = qs.count()
    if total == 0:
        return None
    present = qs.filter(status='present').count()
    return round((present / total) * 100, 1)


def record_security_metric(scope, window_seconds=300):
    cache_key = f'security_metric:{scope}'
    count = cache.get(cache_key, 0) + 1
    cache.set(cache_key, count, window_seconds)
    return count


def record_security_spike(scope, threshold, window_seconds=300, level='warning'):
    count = record_security_metric(scope, window_seconds=window_seconds)
    if count >= threshold:
        log_fn = getattr(logger, level, logger.warning)
        log_fn('Security spike detected for scope=%s count=%s window=%ss', scope, count, window_seconds)
    return count


def get_client_ip(request):
    """Return the real client IP, respecting Render's X-Forwarded-For proxy header."""
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def hit_rate_limit(request, scope, limit, window_seconds, track_spike=True):
    user_part = str(request.user.id) if getattr(request, 'user', None) and request.user.is_authenticated else 'anon'
    ip_part = get_client_ip(request)
    cache_key = f'ratelimit:{scope}:{user_part}:{ip_part}'
    count = cache.get(cache_key, 0)
    if track_spike:
        metric_scope = f'{scope}:{ip_part}'
        record_security_spike(metric_scope, threshold=max(5, min(limit, 20)), window_seconds=window_seconds)
    if count >= limit:
        logger.warning('Rate limit triggered for scope=%s user=%s ip=%s limit=%s window=%s', scope, user_part, ip_part, limit, window_seconds)
        return True
    cache.set(cache_key, count + 1, window_seconds)
    return False


def run_background_task(task, *args, **kwargs):
    thread = threading.Thread(target=task, args=args, kwargs=kwargs, daemon=True)
    thread.start()
    return thread


def _serialize_extra_data(extra_data):
    try:
        return json.dumps(extra_data or {}, sort_keys=True, separators=(',', ':'), default=str)
    except TypeError:
        return json.dumps({'value': str(extra_data)}, sort_keys=True, separators=(',', ':'))


def _audit_secret_for_version(signature_version):
    if signature_version == AUDIT_SIGNATURE_V2:
        return str(getattr(settings, 'AUDIT_LOG_SIGNING_KEY', settings.SECRET_KEY)).encode('utf-8')
    return str(settings.SECRET_KEY).encode('utf-8')


def build_audit_entry_hash(
    *,
    actor_id,
    action,
    target_type,
    target_id,
    target_label,
    extra_data,
    ip_address,
    timestamp,
    previous_hash,
    signature_version=AUDIT_SIGNATURE_V2,
):
    payload = '||'.join([
        str(actor_id or ''),
        str(action or ''),
        str(target_type or ''),
        str(target_id or ''),
        str(target_label or ''),
        _serialize_extra_data(extra_data),
        str(ip_address or ''),
        str(timestamp.isoformat() if timestamp else ''),
        str(previous_hash or ''),
    ])
    secret = _audit_secret_for_version(signature_version)
    return hmac.new(secret, payload.encode('utf-8'), hashlib.sha256).hexdigest()


def verify_audit_entry(log):
    previous_hash = getattr(log, 'previous_hash', '') or ''
    entry_hash = getattr(log, 'entry_hash', '') or ''
    if not entry_hash:
        return None
    signature_version = getattr(log, 'signature_version', '') or AUDIT_SIGNATURE_V1
    expected_hash = build_audit_entry_hash(
        actor_id=getattr(log, 'actor_id', None),
        action=log.action,
        target_type=log.target_type,
        target_id=log.target_id,
        target_label=log.target_label,
        extra_data=log.extra_data,
        ip_address=log.ip_address,
        timestamp=log.timestamp,
        previous_hash=previous_hash,
        signature_version=signature_version,
    )
    # Backward-compatible verification for pre-versioned or migrated rows.
    if not hmac.compare_digest(entry_hash, expected_hash) and signature_version != AUDIT_SIGNATURE_V1:
        legacy_expected = build_audit_entry_hash(
            actor_id=getattr(log, 'actor_id', None),
            action=log.action,
            target_type=log.target_type,
            target_id=log.target_id,
            target_label=log.target_label,
            extra_data=log.extra_data,
            ip_address=log.ip_address,
            timestamp=log.timestamp,
            previous_hash=previous_hash,
            signature_version=AUDIT_SIGNATURE_V1,
        )
        return hmac.compare_digest(entry_hash, legacy_expected)
    return hmac.compare_digest(entry_hash, expected_hash)


def log_action(request_or_user, action, target_type='', target_id=None, target_label='', extra_data=None, ip=None):
    try:
        from accounts.models import AuditLog
        from django.http import HttpRequest

        actor = None
        ip_address = ip

        if isinstance(request_or_user, HttpRequest):
            actor = request_or_user.user if request_or_user.user.is_authenticated else None
            from accounts.utils import get_client_ip
            ip_address = ip_address or get_client_ip(request_or_user)
        else:
            actor = request_or_user

        with transaction.atomic():
            previous_log = AuditLog.objects.select_for_update().order_by('-id').first()
            previous_hash = previous_log.entry_hash if previous_log and previous_log.entry_hash else ''
            signature_version = getattr(settings, 'AUDIT_LOG_SIGNATURE_VERSION', AUDIT_SIGNATURE_V2)
            log = AuditLog.objects.create(
                actor=actor,
                action=action,
                target_type=target_type,
                target_id=target_id,
                target_label=target_label,
                extra_data=extra_data or {},
                ip_address=ip_address,
                previous_hash=previous_hash,
                signature_version=signature_version,
                entry_hash='',
            )
            log.entry_hash = build_audit_entry_hash(
                actor_id=log.actor_id,
                action=log.action,
                target_type=log.target_type,
                target_id=log.target_id,
                target_label=log.target_label,
                extra_data=log.extra_data,
                ip_address=log.ip_address,
                timestamp=log.timestamp,
                previous_hash=log.previous_hash,
                signature_version=signature_version,
            )
            log.save(update_fields=['entry_hash'])
    except Exception:
        logger.exception('Audit log write failed for action=%s target_type=%s target_id=%s', action, target_type, target_id)
