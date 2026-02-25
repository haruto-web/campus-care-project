from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from ml_models.gemini_client import GeminiClient
from ml_models.utils import get_student_profile_for_intervention
from accounts.models import User
from wellness.models import RiskAssessment, Alert, Intervention, WellnessCheckIn, TeacherConcern
from django.db.models import Q
import json

@login_required
def counselor_chat_view(request):
    """Render counselor chatbox page"""
    if request.user.role not in ['counselor', 'admin']:
        from django.contrib import messages
        messages.error(request, 'Permission denied.')
        from django.shortcuts import redirect
        return redirect('dashboard')
    return render(request, 'ai_assistant/counselor_chat.html')

@login_required
def admin_chat_view(request):
    """Render admin chatbox page"""
    if request.user.role != 'admin':
        from django.contrib import messages
        messages.error(request, 'Permission denied.')
        from django.shortcuts import redirect
        return redirect('dashboard')
    return render(request, 'ai_assistant/admin_chat.html')

@login_required
@require_http_methods(["POST"])
def counselor_chat(request):
    """AI Assistant for Counselor"""
    if request.user.role not in ['counselor', 'admin']:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        action = data.get('action')
        message = data.get('message', '')
        
        client = GeminiClient()
        
        if action == 'create_intervention':
            student_id = data.get('student_id')
            try:
                student = User.objects.get(id=student_id, role='student')
                profile = get_student_profile_for_intervention(student)
                result = client.recommend_intervention(profile)
                
                # Auto-create intervention
                from datetime import datetime, timedelta
                intervention = Intervention.objects.create(
                    student=student,
                    counselor=request.user,
                    intervention_type='counseling',
                    description=f"AI-Generated Intervention: {result.get('summary', '')}",
                    scheduled_date=datetime.now() + timedelta(days=3),
                    status='scheduled'
                )
                
                # Create alert notification
                Alert.objects.create(
                    student=student,
                    alert_type='ai_intervention',
                    severity='medium',
                    message=f"🤖 BT Assistant auto-created intervention for {student.get_full_name()}. Please review the intervention details.",
                    resolved=False
                )
                
                return JsonResponse({
                    'response': result.get('summary', ''),
                    'recommendations': result.get('recommendations', []),
                    'intervention_created': True,
                    'intervention_id': intervention.id
                })
            except User.DoesNotExist:
                return JsonResponse({'error': 'Student not found'}, status=404)
            except Exception as e:
                import traceback
                print(f"Error in create_intervention: {str(e)}")
                print(traceback.format_exc())
                return JsonResponse({'error': f'Error: {str(e)}'}, status=500)
        
        elif action == 'generate_report':
            high_risk = RiskAssessment.objects.filter(risk_level='high').count()
            medium_risk = RiskAssessment.objects.filter(risk_level='medium').count()
            unresolved_alerts = Alert.objects.filter(resolved=False).count()
            pending_interventions = Intervention.objects.filter(status='scheduled').count()
            
            summary_data = {
                'high_risk_count': high_risk,
                'medium_risk_count': medium_risk,
                'unresolved_alerts': unresolved_alerts,
                'pending_interventions': pending_interventions
            }
            
            prompt = f"""Generate a system overview report for a school counselor. Use this data:

Current Status: {high_risk} high-risk students, {medium_risk} medium-risk students, {unresolved_alerts} unresolved alerts, {pending_interventions} pending interventions

Write in a conversational, easy-to-read style:
- Use emojis (🔴 critical, ⚠️ warning, 📊 stats, 💡 insight)
- Create 4 sections: Current Status, Priority Actions, System Health, Recommendations
- Each section should have 2-3 short bullet points
- Start each bullet with an emoji
- Keep sentences short and natural
- No bold text, no asterisks, no markdown
- Use plain text only"""
            summary = client.generate_text(prompt)
            
            return JsonResponse({'response': summary, 'data': summary_data})
        
        elif action == 'analyze_behavior':
            student_id = data.get('student_id')
            try:
                student = User.objects.get(id=student_id, role='student')
            except User.DoesNotExist:
                return JsonResponse({'error': 'Student not found'}, status=404)
            
            # Get student data
            from academics.models import Attendance, Submission
            attendance = Attendance.objects.filter(student=student).order_by('-date')[:30]
            submissions = Submission.objects.filter(student=student).order_by('-submitted_at')[:20]
            wellness = WellnessCheckIn.objects.filter(student=student).order_by('-date')[:10]
            
            behavior_data = {
                'student_name': student.get_full_name(),
                'attendance_pattern': [{'date': str(a.date), 'status': a.status} for a in attendance],
                'submission_pattern': [{'date': str(s.submitted_at.date()) if s.submitted_at else 'N/A', 'score': s.score if s.score else 'N/A'} for s in submissions],
                'wellness_trend': [{'date': str(w.date), 'stress': w.stress_level, 'motivation': w.motivation_level} for w in wellness]
            }
            
            prompt = f"""Analyze this student's behavior pattern and provide insights:
            
{json.dumps(behavior_data, indent=2)}

Provide:
1. Overall pattern (improving/declining/stable)
2. Key observations
3. Concerning trends
4. Recommendations"""
            
            analysis = client.generate_text(prompt)
            return JsonResponse({'response': analysis})
        
        elif action == 'weekly_summary':
            from datetime import datetime, timedelta
            week_ago = datetime.now() - timedelta(days=7)
            
            new_alerts = Alert.objects.filter(created_at__gte=week_ago).count()
            new_interventions = Intervention.objects.filter(scheduled_date__gte=week_ago).count()
            new_concerns = TeacherConcern.objects.filter(created_at__gte=week_ago).count()
            new_high_risk = RiskAssessment.objects.filter(date__gte=week_ago, risk_level='high').count()
            pending_alerts = Alert.objects.filter(resolved=False).count()
            
            weekly_data = {
                'new_alerts': new_alerts,
                'new_interventions': new_interventions,
                'new_concerns': new_concerns,
                'new_high_risk_students': new_high_risk,
                'pending_alerts': pending_alerts
            }
            
            prompt = f"""Generate an engaging weekly summary for a school counselor. Use this data:

This Week: {new_alerts} new alerts, {new_interventions} interventions, {new_concerns} concerns, {new_high_risk} high-risk students, {pending_alerts} pending alerts

Write in a conversational, easy-to-read style:
- Use emojis (🔴 urgent, ⚠️ attention, ✅ positive, 📋 action)
- Create 4 sections: What Happened, Watch Out For, Good News, Next Steps
- Each section should have 2-3 short bullet points
- Start each bullet with an emoji
- Keep sentences short and natural
- No bold text, no asterisks, no markdown
- Use plain text only"""
            
            summary = client.generate_text(prompt)
            return JsonResponse({'response': summary, 'data': weekly_data})
        
        elif action == 'draft_email':
            student_id = data.get('student_id')
            purpose = data.get('purpose', 'general concern')
            try:
                student = User.objects.get(id=student_id, role='student')
            except User.DoesNotExist:
                return JsonResponse({'error': 'Student not found'}, status=404)
            
            # Get recent data
            risk = RiskAssessment.objects.filter(student=student).order_by('-date').first()
            concerns = TeacherConcern.objects.filter(student=student).order_by('-created_at')[:3]
            
            email_context = {
                'student_name': student.get_full_name(),
                'purpose': purpose,
                'risk_level': risk.risk_level if risk else 'unknown',
                'recent_concerns': [c.description for c in concerns] if concerns else ['No recent concerns']
            }
            
            prompt = f"""Draft a professional, empathetic email to parents about their child:

Context:
{json.dumps(email_context, indent=2)}

The email should:
1. Be warm and supportive
2. Clearly state the concern
3. Suggest a meeting or next steps
4. End positively

Format: Subject line and email body"""
            
            email = client.generate_text(prompt)
            return JsonResponse({'response': email})
        
        elif action == 'search_student':
            filters = data.get('filters', {})
            students = User.objects.filter(role='student')
            
            if filters.get('year_level'):
                students = students.filter(year_level=filters['year_level'])
            if filters.get('section'):
                students = students.filter(section__icontains=filters['section'])
            if filters.get('severity'):
                risk_level_map = {'critical': 'high', 'high': 'high', 'medium': 'medium', 'low': 'low'}
                risk_level = risk_level_map.get(filters['severity'])
                student_ids = RiskAssessment.objects.filter(risk_level=risk_level).values_list('student_id', flat=True)
                students = students.filter(id__in=student_ids)
            
            results = [{
                'id': s.id,
                'name': s.get_full_name(),
                'year_level': s.year_level,
                'section': s.section,
                'email': s.email
            } for s in students[:10]]
            
            return JsonResponse({'students': results})
        
        elif action == 'auto_create_interventions':
            # Auto-create interventions for all high-risk students without existing interventions
            from datetime import datetime, timedelta
            
            high_risk_students = RiskAssessment.objects.filter(risk_level='high').values_list('student_id', flat=True)
            students_needing_intervention = User.objects.filter(
                id__in=high_risk_students,
                role='student'
            ).exclude(
                interventions__status='scheduled'
            )
            
            created_count = 0
            for student in students_needing_intervention:
                try:
                    profile = get_student_profile_for_intervention(student)
                    result = client.recommend_intervention(profile)
                    
                    # Create intervention
                    Intervention.objects.create(
                        student=student,
                        counselor=request.user,
                        intervention_type='counseling',
                        description=f"AI Auto-Generated: {result.get('summary', 'Intervention needed for high-risk student')}",
                        scheduled_date=datetime.now() + timedelta(days=3),
                        status='scheduled'
                    )
                    
                    # Create alert
                    Alert.objects.create(
                        student=student,
                        alert_type='ai_intervention',
                        severity='high',
                        message=f"🤖 BT Assistant auto-created intervention for {student.get_full_name()}. High-risk student requires immediate attention.",
                        resolved=False
                    )
                    
                    created_count += 1
                except Exception as e:
                    print(f"Error creating intervention for {student.username}: {e}")
                    continue
            
            return JsonResponse({
                'success': True,
                'created_count': created_count,
                'message': f'Successfully created {created_count} interventions for high-risk students'
            })
        
        elif action == 'ask_ai':
            response = client.generate_text(message)
            return JsonResponse({'response': response})
        
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def admin_chat(request):
    """AI Assistant for Admin"""
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        action = data.get('action')
        message = data.get('message', '')
        
        client = GeminiClient()
        
        if action == 'generate_report':
            total_students = User.objects.filter(role='student').count()
            total_teachers = User.objects.filter(role='teacher').count()
            total_counselors = User.objects.filter(role='counselor').count()
            high_risk = RiskAssessment.objects.filter(risk_level='high').count()
            
            summary_data = {
                'total_students': total_students,
                'total_teachers': total_teachers,
                'total_counselors': total_counselors,
                'high_risk_students': high_risk
            }
            
            prompt = f"""Generate an executive summary report for a school admin. Use this data:

System Status: {total_students} students, {total_teachers} teachers, {total_counselors} counselors, {high_risk} high-risk students

Write in a conversational, easy-to-read style:
- Use emojis (📊 stats, 👥 people, ⚠️ warning, 💡 insight)
- Create 4 sections: System Overview, Staffing Status, Student Wellness, Action Items
- Each section should have 2-3 short bullet points
- Start each bullet with an emoji
- Keep sentences short and natural
- No bold text, no asterisks, no markdown
- Use plain text only"""
            summary = client.generate_text(prompt)
            
            return JsonResponse({'response': summary, 'data': summary_data})
        
        elif action == 'ask_ai':
            response = client.generate_text(message)
            return JsonResponse({'response': response})
        
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
