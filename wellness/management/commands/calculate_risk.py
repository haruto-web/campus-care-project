from django.core.management.base import BaseCommand
from django.db.models import Sum
from accounts.models import User
from academics.models import Grade, Attendance, Assignment, Submission
from wellness.models import RiskAssessment, WellnessCheckIn, Alert
from datetime import timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Calculate risk assessments for all students'

    def handle(self, *args, **kwargs):
        students = User.objects.filter(role='student')

        for student in students:
            # ── GPA (correct formula: sum scores / sum max_scores * 100) ──
            grades = Grade.objects.filter(student=student)
            if grades.exists():
                totals = grades.aggregate(total_score=Sum('score'), total_max=Sum('max_score'))
                total_score = totals['total_score'] or 0
                total_max = totals['total_max'] or 1
                avg_percentage = float(total_score) / float(total_max) * 100
            else:
                avg_percentage = 100  # no grades yet = no risk from GPA

            # Convert to Philippine GPA scale
            if avg_percentage >= 97:
                gpa = 1.00
            elif avg_percentage >= 94:
                gpa = 1.25
            elif avg_percentage >= 91:
                gpa = 1.50
            elif avg_percentage >= 88:
                gpa = 1.75
            elif avg_percentage >= 85:
                gpa = 2.00
            elif avg_percentage >= 82:
                gpa = 2.25
            elif avg_percentage >= 79:
                gpa = 2.50
            elif avg_percentage >= 76:
                gpa = 2.75
            elif avg_percentage >= 75:
                gpa = 3.00
            else:
                gpa = 5.00

            # ── Per-class failing detection ──
            student_classes = student.enrolled_classes.all()
            failing_class_names = []
            for cls in student_classes:
                cls_grades = grades.filter(class_obj=cls)
                if cls_grades.exists():
                    cls_totals = cls_grades.aggregate(s=Sum('score'), m=Sum('max_score'))
                    if cls_totals['m']:
                        cls_pct = float(cls_totals['s']) / float(cls_totals['m']) * 100
                        if cls_pct < 75:
                            failing_class_names.append(cls.name)
            failing_classes = len(failing_class_names)

            # ── Attendance rate ──
            attendance_records = Attendance.objects.filter(student=student)
            if attendance_records.exists():
                attendance_rate = (
                    attendance_records.filter(status='present').count()
                    / attendance_records.count() * 100
                )
            else:
                attendance_rate = 100

            # ── Missing assignments ──
            total_assignments = Assignment.objects.filter(class_obj__in=student_classes).count()
            submitted = Submission.objects.filter(student=student).count()
            missing_assignments = max(total_assignments - submitted, 0)

            # ── Risk score ──
            risk_score = 0

            # GPA factor (0–30 points) — based on correct percentage
            if avg_percentage < 75:
                risk_score += 30
            elif avg_percentage < 80:
                risk_score += 20
            elif avg_percentage < 85:
                risk_score += 10

            # Per-class failing factor (0–20 points)
            if failing_classes >= 5:
                risk_score += 20
            elif failing_classes >= 3:
                risk_score += 15
            elif failing_classes >= 1:
                risk_score += 5

            # Attendance factor (0–30 points)
            if attendance_rate < 60:
                risk_score += 30
            elif attendance_rate < 70:
                risk_score += 25
            elif attendance_rate < 80:
                risk_score += 15
            elif attendance_rate < 90:
                risk_score += 5

            # Missing assignments factor (0–20 points)
            if missing_assignments >= 5:
                risk_score += 20
            elif missing_assignments >= 3:
                risk_score += 15
            elif missing_assignments >= 1:
                risk_score += 5

            # Wellness factor (0–10 points)
            recent_checkin = WellnessCheckIn.objects.filter(student=student).order_by('-date').first()
            if recent_checkin:
                if recent_checkin.stress_level >= 4 or recent_checkin.motivation_level <= 2 or recent_checkin.need_help:
                    risk_score += 10

            # ── Risk level (4 tiers) ──
            if risk_score >= 70:
                risk_level = 'critical'
            elif risk_score >= 50:
                risk_level = 'high'
            elif risk_score >= 30:
                risk_level = 'medium'
            else:
                risk_level = 'low'

            # ── Save assessment ──
            RiskAssessment.objects.create(
                student=student,
                risk_level=risk_level,
                risk_score=risk_score,
                gpa=gpa,
                attendance_rate=round(attendance_rate, 2),
                missing_assignments=missing_assignments,
                failing_classes=failing_classes,
            )

            # ── Failing subjects alert (new) ──
            if failing_classes >= 3:
                existing = Alert.objects.filter(
                    student=student,
                    alert_type='failing_subjects',
                    resolved=False
                ).exists()
                if not existing:
                    subject_list = ', '.join(failing_class_names)
                    severity = 'critical' if failing_classes >= 5 else 'high'
                    Alert.objects.create(
                        student=student,
                        alert_type='failing_subjects',
                        severity=severity,
                        message=(
                            f'{student.get_full_name()} is failing {failing_classes} out of '
                            f'{student_classes.count()} classes: {subject_list}. '
                            f'Overall average: {round(avg_percentage, 1)}%. '
                            f'Consider subject-specific tutoring.'
                        )
                    )

            self.stdout.write(self.style.SUCCESS(
                f'{student.get_full_name()}: {risk_level} (score={risk_score}, '
                f'avg={round(avg_percentage,1)}%, failing={failing_classes} classes)'
            ))

        self.stdout.write(self.style.SUCCESS(
            f'Done. Risk assessments calculated for {students.count()} students.'
        ))
