from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from academics.models import Class, Assignment, Submission, Attendance
from wellness.models import RiskAssessment, Alert, WellnessCheckIn
from datetime import date, timedelta
import random

FIRST_NAMES = ['James','Maria','John','Ana','Carlos','Sofia','Miguel','Isabella','Luis','Camila',
               'Jose','Valentina','David','Lucia','Daniel','Elena','Kevin','Diana','Ryan','Paula',
               'Mark','Clara','Eric','Nina','Alex','Rosa','Chris','Mia','Brian','Lena',
               'Aaron','Nora','Sean','Iris','Kyle','Vera','Troy','Jade','Cole','Faye',
               'Drew','Zoe','Blake','Ivy','Reid','Ava','Lane','Sky','Dean','Hope']
LAST_NAMES = ['Santos','Reyes','Cruz','Garcia','Lopez','Martinez','Gonzalez','Perez','Torres','Flores',
              'Rivera','Ramirez','Morales','Ortiz','Gutierrez','Chavez','Ramos','Mendoza','Ruiz','Vargas',
              'Castillo','Jimenez','Moreno','Romero','Herrera','Medina','Aguilar','Vega','Cabrera','Soto',
              'Delgado','Rios','Fuentes','Pena','Miranda','Lara','Guerrero','Campos','Espinoza','Sandoval',
              'Rojas','Diaz','Nunez','Salazar','Molina','Suarez','Contreras','Ibarra','Acosta','Pacheco']

class Command(BaseCommand):
    help = 'Create 50 dummy students with risk data'

    def handle(self, *args, **kwargs):
        # Get or create a teacher
        teacher, _ = User.objects.get_or_create(
            username='demo_teacher',
            defaults={
                'email': 'demoteacher@brighttrack.com',
                'role': 'teacher',
                'first_name': 'Demo',
                'last_name': 'Teacher',
                'profile_completed': True,
            }
        )
        if _:
            teacher.set_password('teacher123')
            teacher.save()

        # Get or create a counselor
        counselor, _ = User.objects.get_or_create(
            username='demo_counselor',
            defaults={
                'email': 'democounselor@brighttrack.com',
                'role': 'counselor',
                'first_name': 'Demo',
                'last_name': 'Counselor',
                'profile_completed': True,
            }
        )
        if _:
            counselor.set_password('counselor123')
            counselor.save()

        # Create classes
        apple_class, _ = Class.objects.get_or_create(
            code='SEC-APPLE-7',
            defaults={
                'name': 'Grade 7 - Apple',
                'teacher': teacher,
                'semester': '1st Semester 2025-2026',
                'section': 'Apple',
                'year_level': '7',
            }
        )
        banana_class, _ = Class.objects.get_or_create(
            code='SEC-BANANA-10',
            defaults={
                'name': 'Grade 10 - Banana',
                'teacher': teacher,
                'semester': '1st Semester 2025-2026',
                'section': 'Banana',
                'year_level': '10',
            }
        )
        general_class, _ = Class.objects.get_or_create(
            code='GEN-7-2025',
            defaults={
                'name': 'Grade 7 - General',
                'teacher': teacher,
                'semester': '1st Semester 2025-2026',
                'section': '',
                'year_level': '7',
            }
        )

        created = 0
        groups = [
            # (count, year_level, section, risk_level, risk_score, gpa, attendance, missing, alert_severity)
            (10, '7', 'Apple',  'high',   75.0, 1.8, 60.0, 5, 'high'),
            (20, '7', '',       'low',    20.0, 3.2, 88.0, 0, 'low'),
            (10, '10','Banana', 'high',   90.0, 1.2, 50.0, 7, 'critical'),
            (10, '8', 'Mango',  'medium', 50.0, 2.5, 75.0, 2, 'medium'),
        ]

        idx = 0
        for count, year_level, section, risk_level, risk_score, gpa, attendance, missing, alert_sev in groups:
            for i in range(count):
                first = FIRST_NAMES[idx % len(FIRST_NAMES)]
                last = LAST_NAMES[idx % len(LAST_NAMES)]
                username = f'student_{year_level}_{section.lower() or "gen"}_{i+1}'
                email = f'{username}@brighttrack.com'

                student, created_now = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'role': 'student',
                        'first_name': first,
                        'last_name': last,
                        'year_level': year_level,
                        'section': section,
                        'student_number': f'2025-{idx+1:04d}',
                        'profile_completed': True,
                    }
                )
                if created_now:
                    student.set_password('student123')
                    student.save()
                    created += 1

                # Enroll in class
                if section == 'Apple' and year_level == '7':
                    apple_class.students.add(student)
                elif section == 'Banana' and year_level == '10':
                    banana_class.students.add(student)
                else:
                    general_class.students.add(student)

                # Risk assessment
                RiskAssessment.objects.get_or_create(
                    student=student,
                    date=date.today(),
                    defaults={
                        'risk_level': risk_level,
                        'risk_score': risk_score + random.uniform(-5, 5),
                        'gpa': gpa + random.uniform(-0.2, 0.2),
                        'attendance_rate': attendance + random.uniform(-5, 5),
                        'missing_assignments': missing + random.randint(0, 2),
                    }
                )

                # Alert
                Alert.objects.get_or_create(
                    student=student,
                    alert_type='high_risk' if risk_level == 'high' else 'missing_assignments',
                    resolved=False,
                    defaults={
                        'severity': alert_sev,
                        'message': f'{first} {last} has been flagged: GPA {gpa:.1f}, Attendance {attendance:.0f}%, {missing} missing assignments.',
                    }
                )

                # Wellness check-in
                WellnessCheckIn.objects.get_or_create(
                    student=student,
                    defaults={
                        'stress_level': 5 if risk_level == 'high' else random.randint(1, 3),
                        'motivation_level': 1 if risk_level == 'high' else random.randint(3, 5),
                        'workload_level': 5 if risk_level == 'high' else random.randint(2, 4),
                        'sleep_quality': 1 if risk_level == 'high' else random.randint(3, 5),
                        'need_help': risk_level == 'high',
                        'comments': 'Struggling with coursework.' if risk_level == 'high' else 'Doing okay.',
                    }
                )

                idx += 1

        self.stdout.write(self.style.SUCCESS(f'Done! Created {created} new students.'))
        self.stdout.write('Groups created:')
        self.stdout.write('  10x Grade 7 Apple  → HIGH risk    (password: student123)')
        self.stdout.write('  20x Grade 7 No sec → LOW risk     (password: student123)')
        self.stdout.write('  10x Grade 10 Banana→ CRITICAL risk(password: student123)')
        self.stdout.write('  10x Grade 8 Mango  → MEDIUM risk  (password: student123)')
        self.stdout.write('Teacher:   demo_teacher / teacher123')
        self.stdout.write('Counselor: demo_counselor / counselor123')
