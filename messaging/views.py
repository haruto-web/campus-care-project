import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_POST
from .models import Conversation, Message
from accounts.models import User

# Role-based allowed recipients
ALLOWED_RECIPIENTS = {
    'admin':    ['counselor', 'teacher', 'student'],
    'counselor':['admin', 'counselor', 'teacher', 'student'],
    'teacher':  ['counselor', 'admin', 'student'],
    'student':  ['counselor', 'teacher'],
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
        body = request.POST.get('body', '').strip()
        attachment = request.FILES.get('attachment')
        if body or attachment:
            msg = Message.objects.create(
                conversation=conv,
                sender=request.user,
                body=body,
                attachment=attachment
            )
            conv.save()
            # AJAX send — return JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'id': msg.id,
                    'body': msg.body,
                    'attachment_url': msg.attachment.url if msg.attachment else None,
                    'is_image': msg.is_image() if msg.attachment else False,
                    'created_at': msg.created_at.strftime('%b %d, %I:%M %p'),
                    'is_mine': True,
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
    """Return messages newer than ?after=<message_id> as JSON."""
    conv = get_object_or_404(Conversation, id=conv_id)
    if request.user not in conv.participants.all():
        return JsonResponse({'error': 'denied'}, status=403)

    after_id = int(request.GET.get('after', 0))
    new_msgs = conv.messages.filter(id__gt=after_id).select_related('sender')
    # Mark incoming as read
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
        })
    return JsonResponse({'messages': data})


@login_required
def new_message(request, recipient_id=None):
    allowed_roles = ALLOWED_RECIPIENTS.get(request.user.role, [])
    recipients_qs = User.objects.filter(role__in=allowed_roles).exclude(id=request.user.id)

    if request.method == 'POST':
        recipient_id = request.POST.get('recipient') or recipient_id
        body = request.POST.get('body', '').strip()
        attachment = request.FILES.get('attachment')
        recipient = get_object_or_404(User, id=recipient_id)

        if recipient.role not in allowed_roles:
            messages.error(request, 'You cannot message this user.')
            return redirect('messaging:inbox')

        # Find existing conversation between these two users
        conv = Conversation.objects.filter(participants=request.user).filter(participants=recipient).first()
        if not conv:
            conv = Conversation.objects.create()
            conv.participants.add(request.user, recipient)

        if body or attachment:
            Message.objects.create(conversation=conv, sender=request.user, body=body, attachment=attachment)
            conv.save()

        return redirect('messaging:conversation', conv_id=conv.id)

    selected_recipient = None
    if recipient_id:
        selected_recipient = get_object_or_404(User, id=recipient_id)

    # Build recipients list with section/year data for JS filtering
    recipients_data = list(recipients_qs.values('id', 'first_name', 'last_name', 'role', 'year_level', 'section'))
    for r in recipients_data:
        r['full_name'] = f"{r['first_name']} {r['last_name']}"

    # Get unique sections and year levels from students
    students = recipients_qs.filter(role='student')
    sections = sorted(set(s.section for s in students if s.section))
    year_levels = sorted(set(s.year_level for s in students if s.year_level))

    return render(request, 'messaging/new_message.html', {
        'recipients_json': recipients_data,
        'recipients': recipients_qs,
        'selected_recipient': selected_recipient,
        'sections': sections,
        'year_levels': year_levels,
        'available_roles': sorted(set(allowed_roles)),
    })
