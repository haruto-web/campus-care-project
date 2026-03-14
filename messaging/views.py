import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .models import Conversation, Message, MessageReport
from accounts.models import User
from .content_filter import contains_inappropriate_content, filter_message_content
from campus_care.validators import validate_document_upload
from accounts.decorators import role_required
from accounts.otp_utils import send_transactional_email

# Role-based allowed recipients
ALLOWED_RECIPIENTS = {
    'admin':    ['counselor', 'teacher', 'student'],
    'counselor':['admin', 'counselor', 'teacher', 'student'],
    'teacher':  ['counselor', 'admin', 'student'],
    'student':  ['counselor', 'teacher', 'student'],
}


@login_required
def inbox(request):
    convs = request.user.conversations.prefetch_related('participants', 'messages').all()
    data = []
    for conv in convs:
        other = conv.get_other_participant(request.user)
        last_msg = conv.messages.last()
        unread = conv.unread_count_for(request.user)
        data.append({'conv': conv, 'other': other, 'last_msg': last_msg, 'unread': unread})
    return render(request, 'messaging/inbox.html', {'conversations': data})


@login_required
def conversation(request, conv_id):
    conv = get_object_or_404(Conversation, id=conv_id)
    if request.user not in conv.participants.all():
        messages.error(request, 'Access denied.')
        return redirect('messaging:inbox')

    # Mark all unread messages as read
    conv.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    if request.method == 'POST':
        # Check messaging suspension
        if request.user.is_messaging_suspended():
            messages.error(request, f'Your messaging access is suspended until {request.user.messaging_suspended_until.strftime("%b %d, %Y at %I:%M %p")}.')
            return redirect('messaging:inbox')

        body = request.POST.get('body', '').strip()
        attachment = request.FILES.get('attachment')

        if attachment:
            try:
                validate_document_upload(attachment)
            except ValidationError as e:
                messages.error(request, f'Attachment rejected: {e.message}')
                return redirect('messaging:conversation', conv_id=conv.id)

        if request.user.role == 'student' and body:
            is_inappropriate, found_words = contains_inappropriate_content(body)
            if is_inappropriate:
                messages.error(request, 'Your message contains inappropriate language and cannot be sent. Please use respectful language.')
                return redirect('messaging:conversation', conv_id=conv.id)

        if body or attachment:
            try:
                msg = Message.objects.create(
                    conversation=conv,
                    sender=request.user,
                    body=body,
                    attachment=attachment
                )
            except Exception:
                msg = Message.objects.create(
                    conversation=conv,
                    sender=request.user,
                    body=body
                )
                messages.warning(request, 'File attachment failed to upload. Message sent without attachment.')
            conv.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'id': msg.id,
                    'body': msg.body,
                    'attachment_url': msg.attachment.url if msg.attachment else None,
                    'is_image': msg.is_image() if msg.attachment else False,
                    'created_at': msg.created_at.strftime('%b %d, %I:%M %p'),
                    'is_mine': True,
                    'is_read': False,
                })
        return redirect('messaging:conversation', conv_id=conv.id)

    other = conv.get_other_participant(request.user)
    return render(request, 'messaging/conversation.html', {
        'conv': conv,
        'other': other,
        'msgs': conv.messages.all(),
    })


@login_required
def poll_messages(request, conv_id):
    conv = get_object_or_404(Conversation, id=conv_id)
    if request.user not in conv.participants.all():
        return JsonResponse({'error': 'denied'}, status=403)

    try:
        after_id = int(request.GET.get('after', 0))
    except (ValueError, TypeError):
        after_id = 0
    new_msgs = conv.messages.filter(id__gt=after_id).select_related('sender')
    new_msgs.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    data = []
    for msg in new_msgs:
        data.append({
            'id': msg.id,
            'body': msg.body,
            'attachment_url': msg.attachment.url if msg.attachment else None,
            'is_image': msg.is_image() if msg.attachment else False,
            'created_at': msg.created_at.strftime('%b %d, %I:%M %p'),
            'is_mine': msg.sender == request.user,
            'is_read': msg.is_read,
        })
    last_read_sent = conv.messages.filter(
        sender=request.user, is_read=True
    ).order_by('-id').values_list('id', flat=True).first()
    user = request.user
    suspended = user.is_messaging_suspended()
    return JsonResponse({
        'messages': data,
        'last_read_sent_id': last_read_sent or 0,
        'is_suspended': suspended,
    })


@login_required
def new_message(request, recipient_id=None):
    allowed_roles = ALLOWED_RECIPIENTS.get(request.user.role, [])
    recipients_qs = User.objects.filter(role__in=allowed_roles).exclude(id=request.user.id)

    recipients_data = list(recipients_qs.values('id', 'first_name', 'last_name', 'role', 'year_level', 'section'))
    for r in recipients_data:
        r['full_name'] = f"{r['first_name']} {r['last_name']}"

    students = recipients_qs.filter(role='student')
    sections = sorted(set(s.section for s in students if s.section))
    year_levels = sorted(set(s.year_level for s in students if s.year_level))

    if request.method == 'POST':
        recipient_id = request.POST.get('recipient') or recipient_id
        body = request.POST.get('body', '').strip()
        attachment = request.FILES.get('attachment')
        recipient = get_object_or_404(User, id=recipient_id)

        if recipient.role not in allowed_roles:
            messages.error(request, 'You cannot message this user.')
            return redirect('messaging:inbox')

        if request.user.is_messaging_suspended():
            messages.error(request, f'Your messaging access is suspended until {request.user.messaging_suspended_until.strftime("%b %d, %Y at %I:%M %p")}.')
            return redirect('messaging:inbox')

        if attachment:
            try:
                validate_document_upload(attachment)
            except ValidationError as e:
                messages.error(request, f'Attachment rejected: {e.message}')
                return render(request, 'messaging/new_message.html', {
                    'recipients_json': recipients_data,
                    'recipients': recipients_qs,
                    'selected_recipient': recipient,
                    'sections': sections,
                    'year_levels': year_levels,
                    'available_roles': sorted(set(allowed_roles)),
                })

        if request.user.role == 'student' and body:
            is_inappropriate, found_words = contains_inappropriate_content(body)
            if is_inappropriate:
                messages.error(request, 'Your message contains inappropriate language and cannot be sent. Please use respectful language.')
                return render(request, 'messaging/new_message.html', {
                    'recipients_json': recipients_data,
                    'recipients': recipients_qs,
                    'selected_recipient': recipient,
                    'sections': sections,
                    'year_levels': year_levels,
                    'available_roles': sorted(set(allowed_roles)),
                })

        conv = Conversation.objects.filter(participants=request.user).filter(participants=recipient).first()
        if not conv:
            conv = Conversation.objects.create()
            conv.participants.add(request.user, recipient)

        if body or attachment:
            try:
                Message.objects.create(conversation=conv, sender=request.user, body=body, attachment=attachment)
            except Exception:
                Message.objects.create(conversation=conv, sender=request.user, body=body)
                messages.warning(request, 'File attachment failed to upload. Message sent without attachment.')
            conv.save()

        return redirect('messaging:conversation', conv_id=conv.id)

    selected_recipient = None
    if recipient_id:
        selected_recipient = get_object_or_404(User, id=recipient_id)

    return render(request, 'messaging/new_message.html', {
        'recipients_json': recipients_data,
        'recipients': recipients_qs,
        'selected_recipient': selected_recipient,
        'sections': sections,
        'year_levels': year_levels,
        'available_roles': sorted(set(allowed_roles)),
    })


@login_required
def report_message(request, msg_id):
    msg = get_object_or_404(Message, id=msg_id)
    if msg.sender == request.user:
        messages.error(request, 'You cannot report your own message.')
        return redirect('messaging:inbox')
    if request.user not in msg.conversation.participants.all():
        messages.error(request, 'Access denied.')
        return redirect('messaging:inbox')
    if MessageReport.objects.filter(reporter=request.user, message=msg).exists():
        messages.warning(request, 'You have already reported this message.')
        return redirect('messaging:conversation', conv_id=msg.conversation_id)

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        details = request.POST.get('details', '').strip()
        if reason not in dict(MessageReport.REASON_CHOICES):
            messages.error(request, 'Invalid reason.')
            return redirect('messaging:report_message', msg_id=msg_id)
        MessageReport.objects.create(reporter=request.user, message=msg, reason=reason, details=details)
        messages.success(request, 'Report submitted. A counselor will review it.')
        return redirect('messaging:conversation', conv_id=msg.conversation_id)

    return render(request, 'messaging/report_message.html', {
        'msg': msg,
        'reason_choices': MessageReport.REASON_CHOICES,
    })


@login_required
@role_required('counselor')
def message_reports(request):
    status_filter = request.GET.get('status', '')
    qs = MessageReport.objects.select_related('reporter', 'message__sender', 'resolved_by')
    if status_filter:
        qs = qs.filter(status=status_filter)
    pending_count = MessageReport.objects.filter(status='pending').count()
    return render(request, 'messaging/message_reports.html', {
        'reports': qs,
        'status_filter': status_filter,
        'status_choices': MessageReport.STATUS_CHOICES,
        'pending_count': pending_count,
    })


@login_required
@role_required('counselor')
def resolve_report(request, report_id):
    report = get_object_or_404(MessageReport, id=report_id)
    if request.method == 'POST':
        status = request.POST.get('status', '').strip()
        consequence = request.POST.get('consequence', '').strip()
        notes = request.POST.get('counselor_notes', '').strip()
        if status not in dict(MessageReport.STATUS_CHOICES):
            messages.error(request, 'Invalid status.')
            return redirect('messaging:message_reports')

        report.status = status
        report.consequence = consequence
        report.counselor_notes = notes
        report.resolved_by = request.user
        report.save()

        reported_user = report.reported_user

        if consequence == 'suspend':
            suspend_until = timezone.now() + timedelta(weeks=1)
            reported_user.messaging_suspended_until = suspend_until
            reported_user.save(update_fields=['messaging_suspended_until'])
            send_transactional_email(
                to_email=reported_user.email,
                subject='BrightTrack — Your Messaging Access Has Been Suspended',
                text_content=(
                    f'Dear {reported_user.get_full_name()},\n\n'
                    f'Following a review of a reported message, your messaging access on BrightTrack '
                    f'has been suspended for 7 days.\n\n'
                    f'Suspension ends: {suspend_until.strftime("%B %d, %Y at %I:%M %p")}\n\n'
                    f'Reason: A message you sent was reported and reviewed by the school counselor.\n'
                    f'Notes: {notes or "No additional notes."}\n\n'
                    f'If you believe this is a mistake, please contact your school counselor.\n\n'
                    f'— BrightTrack School System'
                ),
            )
            messages.success(request, f'{reported_user.get_full_name()} has been suspended from messaging for 1 week. Email sent.')

        elif consequence == 'warning':
            send_transactional_email(
                to_email=reported_user.email,
                subject='BrightTrack — Official Warning Regarding Your Messaging Conduct',
                text_content=(
                    f'Dear {reported_user.get_full_name()},\n\n'
                    f'This is an official warning regarding a message you sent on BrightTrack that was '
                    f'reported by another user and reviewed by the school counselor.\n\n'
                    f'Please be reminded to communicate respectfully and responsibly at all times.\n'
                    f'Notes from counselor: {notes or "No additional notes."}\n\n'
                    f'Further violations may result in suspension of your messaging access.\n\n'
                    f'— BrightTrack School System'
                ),
            )
            messages.success(request, f'Warning email sent to {reported_user.get_full_name()}.')

        elif consequence == 'refer':
            send_transactional_email(
                to_email=reported_user.email,
                subject='BrightTrack — You Are Required to Attend a Counselor Session',
                text_content=(
                    f'Dear {reported_user.get_full_name()},\n\n'
                    f'Following a review of a reported message, you are required to attend a '
                    f'one-on-one session with the school counselor in the guidance office.\n\n'
                    f'Please report to the guidance office at your earliest convenience or as scheduled by your counselor.\n'
                    f'Notes: {notes or "No additional notes."}\n\n'
                    f'This matter requires your immediate attention.\n\n'
                    f'— BrightTrack School System'
                ),
            )
            messages.success(request, f'Referral email sent to {reported_user.get_full_name()}.')

        else:
            messages.success(request, 'Report updated. No notification sent.')

        return redirect('messaging:message_reports')

    return render(request, 'messaging/resolve_report.html', {
        'report': report,
        'status_choices': MessageReport.STATUS_CHOICES,
        'consequence_choices': MessageReport.CONSEQUENCE_CHOICES,
    })


@login_required
@role_required('admin')
def admin_message_reports(request):
    status_filter = request.GET.get('status', '')
    qs = MessageReport.objects.select_related('reporter', 'message__sender', 'resolved_by')
    if status_filter:
        qs = qs.filter(status=status_filter)
    pending_count = MessageReport.objects.filter(status='pending').count()
    return render(request, 'messaging/admin_message_reports.html', {
        'reports': qs,
        'status_filter': status_filter,
        'status_choices': MessageReport.STATUS_CHOICES,
        'pending_count': pending_count,
    })
