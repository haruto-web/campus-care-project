from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta


def get_student_data_for_prediction(student):
    """Extract student data for AI risk prediction"""
    from academics.models import Attendance, Submission, Assignment
    from wellness.models import WellnessCheckIn
    
    # Calculate attendance rate (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    attendance_records = Attendance.objects.filter(
        student=student,
        date__gte=thirty_days_ago
    )
    total_days = attendance_records.count()
    present_days = attendance_records.filter(status='present').count()
    attendance_rate = (present_days / total_days * 100) if total_days > 0 else 100
    
    # Count missing assignments
    student_classes = student.enrolled_classes.all()
    assignments = Assignment.objects.filter(class_obj__in=student_classes)
    submitted = Submission.objects.filter(student=student).values_list('assignment_id', flat=True)
    missing_count = assignments.exclude(id__in=submitted).count()
    
    # Get average stress and motivation from recent wellness check-ins
    recent_checkins = WellnessCheckIn.objects.filter(
        student=student
    ).order_by('-date')[:3]
    
    avg_stress = recent_checkins.aggregate(Avg('stress_level'))['stress_level__avg'] or 3
    avg_motivation = recent_checkins.aggregate(Avg('motivation_level'))['motivation_level__avg'] or 3
    
    return {
        'gpa': 0,
        'attendance': round(attendance_rate, 1),
        'missing': missing_count,
        'stress': round(avg_stress, 1),
        'motivation': round(avg_motivation, 1)
    }


def get_student_profile_for_intervention(student):
    """Get student profile for intervention recommendations"""
    from wellness.models import RiskAssessment
    
    issues = []
    
    # Get latest risk assessment for GPA
    latest_risk = RiskAssessment.objects.filter(student=student).order_by('-date').first()
    gpa = latest_risk.gpa if latest_risk and latest_risk.gpa else None
    risk_level = latest_risk.risk_level if latest_risk else 'medium'
    
    if gpa and gpa < 2.5:
        issues.append('academic decline')
    
    data = get_student_data_for_prediction(student)
    if data['attendance'] < 80:
        issues.append('low attendance')
    if data['missing'] >= 3:
        issues.append('missing assignments')
    if data['stress'] >= 4:
        issues.append('high stress')
    
    return {
        'risk_level': risk_level,
        'issues': ', '.join(issues) if issues else 'general support needed',
        'year_level': student.year_level or 9
    }


def get_student_academic_pattern_data(student):
    """Extract student academic pattern data for AI analysis"""
    from academics.models import Attendance, Submission, Assignment
    from django.db.models import Avg
    
    # Get last 10 attendance records
    attendance_records = Attendance.objects.filter(
        student=student
    ).order_by('-date')[:10]
    
    attendance_list = [{
        'date': str(record.date),
        'status': record.status
    } for record in attendance_records]
    
    # Get last 10 graded assignments
    submissions = Submission.objects.filter(
        student=student,
        score__isnull=False
    ).select_related('assignment').order_by('-graded_at')[:10]
    
    assignment_scores = [{
        'title': sub.assignment.title,
        'score': float(sub.score),
        'max_points': float(sub.assignment.points),
        'percentage': round((float(sub.score) / float(sub.assignment.points)) * 100, 1),
        'date': str(sub.graded_at.date())
    } for sub in submissions]
    
    # Calculate grade trend
    if len(assignment_scores) >= 3:
        recent_avg = sum([s['percentage'] for s in assignment_scores[:3]]) / 3
        older_avg = sum([s['percentage'] for s in assignment_scores[-3:]]) / 3
        if recent_avg > older_avg + 5:
            grade_trend = 'improving'
        elif recent_avg < older_avg - 5:
            grade_trend = 'declining'
        else:
            grade_trend = 'stable'
    else:
        grade_trend = 'insufficient_data'
    
    # Recent performance summary
    recent_performance = {
        'avg_score': round(sum([s['percentage'] for s in assignment_scores[:5]]) / len(assignment_scores[:5]), 1) if assignment_scores else 0,
        'attendance_rate': round((attendance_records.filter(status='present').count() / attendance_records.count() * 100), 1) if attendance_records.count() > 0 else 0
    }
    
    return {
        'attendance_records': attendance_list,
        'assignment_scores': assignment_scores,
        'grade_trend': grade_trend,
        'recent_performance': recent_performance
    }
