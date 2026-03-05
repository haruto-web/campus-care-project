from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from wellness.models import RiskAssessment, Alert, WellnessCheckIn
from datetime import date

STUDENTS = [
    # (first, last, email, username, risk_level, risk_score, gpa, attendance, missing, severity, alert_msg)
    ('Maria', 'Santos',   'maria.santos@demo.com',   'maria_santos',   'high',   85.00, 4.50, 55.00, 8, 'critical', 'Student has critically low GPA and attendance.'),
    ('Jose',  'Reyes',    'jose.reyes@demo.com',     'jose_reyes',     'high',   82.00, 4.25, 60.00, 7, 'critical', 'Multiple missing assignments and poor wellness scores.'),
    ('Ana',   'Cruz',     'ana.cruz@demo.com',       'ana_cruz',       'high',   70.00, 3.75, 68.00, 5, 'high',     'Attendance below threshold, several missing assignments.'),
    ('Carlo', 'Dela Cruz','carlo.delacruz@demo.com', 'carlo_delacruz', 'high',   65.00, 3.50, 70.00, 4, 'high',     'Declining grades and low motivation reported.'),
    ('Liza',  'Garcia',   'liza.garcia@demo.com',    'liza_garcia',    'medium', 40.00, 2.50, 82.00, 2, 'medium',   'Slight drop in performance, monitoring recommended.'),
    ('Mark',  'Bautista', 'mark.bautista@demo.com',  'mark_bautista',  'low',    15.00, 1.75, 95.00, 0, 'low',      'Student is performing well.'),
    ('Nina',  'Flores',   'nina.flores@demo.com',    'nina_flores',    'low',    12.00, 1.50, 97.00, 0, 'low',      'Excellent attendance and grades.'),
    ('Ryan',  'Torres',   'ryan.torres@demo.com',    'ryan_torres',    'low',    18.00, 2.00, 93.00, 1, 'low',      'Good standing overall.'),
    ('Ella',  'Ramos',    'ella.ramos@demo.com',     'ella_ramos',     'low',    10.00, 1.25, 98.00, 0, 'low',      'Top performing student.'),
    ('Luis',  'Mendoza',  'luis.mendoza@demo.com',   'luis_mendoza',   'low',    20.00, 2.00, 91.00, 1, 'low',      'Performing within normal range.'),
]

class Command(BaseCommand):
    help = 'Seed 10 demo students for presentation'

    def handle(self, *args, **kwargs):
        for first, last, email, username, risk_level, risk_score, gpa, attendance, missing, severity, alert_msg in STUDENTS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults=dict(
                    first_name=first, last_name=last, email=email,
                    role='student', year_level='9', section='Demo',
                    profile_completed=True,
                )
            )
            if created:
                user.set_password('demo1234')
                user.save()

            RiskAssessment.objects.filter(student=user).delete()
            RiskAssessment.objects.create(
                student=user, date=date.today(),
                risk_level=risk_level, risk_score=risk_score,
                gpa=gpa, attendance_rate=attendance,
                missing_assignments=missing,
            )

            WellnessCheckIn.objects.filter(student=user).delete()
            stress = 5 if severity == 'critical' else 4 if severity == 'high' else 3 if severity == 'medium' else 1
            WellnessCheckIn.objects.create(
                student=user, stress_level=stress,
                motivation_level=6 - stress, workload_level=stress,
                sleep_quality=6 - stress, need_help=severity in ('critical', 'high'),
            )

            Alert.objects.filter(student=user).delete()
            Alert.objects.create(
                student=user, alert_type='high_risk',
                severity=severity, message=alert_msg,
            )

            status = '✓ created' if created else '↺ updated'
            self.stdout.write(f'{status}: {first} {last} [{risk_level} / {severity}]')

        self.stdout.write(self.style.SUCCESS('\nDemo data seeded! Password for all: demo1234'))
