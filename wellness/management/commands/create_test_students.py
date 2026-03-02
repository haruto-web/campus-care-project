from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.models import User
from academics.models import Class, Assignment, Submission, Grade, Attendance
from wellness.models import RiskAssessment, WellnessCheckIn

class Command(BaseCommand):
    help = 'Create 2 test students with good and bad academic performance'

    def handle(self, *args, **kwargs):
        # Create or get Good Student
        good_student, created = User.objects.get_or_create(
            username='alice_good',
            defaults={
                'email': 'alice.good@school.com',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'role': 'student',
                'year_level': '8',
                'section': 'Apple',
                'profile_completed': True
            }
        )
        if created:
            good_student.set_password('password123')
            good_student.save()

        # Create or get Bad Student  
        bad_student, created = User.objects.get_or_create(
            username='bob_struggling',
            defaults={
                'email': 'bob.struggling@school.com',
                'first_name': 'Bob',
                'last_name': 'Smith',
                'role': 'student',
                'year_level': '8',
                'section': 'Apple',
                'profile_completed': True
            }
        )
        if created:
            bad_student.set_password('password123')
            bad_student.save()

        # Clear existing data for fresh test
        RiskAssessment.objects.filter(student__in=[good_student, bad_student]).delete()
        Grade.objects.filter(student__in=[good_student, bad_student]).delete()
        Submission.objects.filter(student__in=[good_student, bad_student]).delete()
        Attendance.objects.filter(student__in=[good_student, bad_student]).delete()
        WellnessCheckIn.objects.filter(student__in=[good_student, bad_student]).delete()
        
        # Get or create a test class
        test_class, created = Class.objects.get_or_create(
            code='MATH-8A',
            defaults={
                'name': 'Mathematics',
                'teacher': User.objects.filter(role='teacher').first(),
                'section': 'Apple',
                'year_level': '8',
                'description': 'Grade 8 Mathematics',
                'semester': 'First Semester'
            }
        )

        # Enroll both students
        test_class.students.add(good_student, bad_student)

        # Create assignments
        assignments = []
        for i in range(5):
            assignment = Assignment.objects.create(
                title=f'Math Assignment {i+1}',
                description=f'Complete exercises {i*10+1}-{(i+1)*10}',
                class_obj=test_class,
                due_date=timezone.now() + timedelta(days=i+1),
                total_points=100
            )
            assignments.append(assignment)

        # Good Student Performance
        for i, assignment in enumerate(assignments):
            # Submit all assignments
            submission = Submission.objects.create(
                assignment=assignment,
                student=good_student,
                submitted_at=timezone.now() - timedelta(days=1)
            )
            # High grades (85-95)
            Grade.objects.create(
                student=good_student,
                class_obj=test_class,
                assignment=assignment,
                score=85 + (i * 2),  # 85, 87, 89, 91, 93
                max_score=100
            )

        # Good attendance (95%)
        for i in range(20):
            status = 'absent' if i == 19 else 'present'  # 1 absence out of 20
            Attendance.objects.create(
                student=good_student,
                class_obj=test_class,
                date=timezone.now().date() - timedelta(days=i),
                status=status
            )

        # Good wellness
        WellnessCheckIn.objects.create(
            student=good_student,
            stress_level=2,
            motivation_level=4,
            workload_level=3,
            sleep_quality=4,
            need_help=False,
            comments='Feeling great and ready to learn!'
        )

        # Bad Student Performance  
        for i, assignment in enumerate(assignments[:2]):  # Only submit 2 out of 5
            submission = Submission.objects.create(
                assignment=assignment,
                student=bad_student,
                submitted_at=assignment.due_date + timedelta(days=2)  # Late
            )
            # Low grades (45-55)
            Grade.objects.create(
                student=bad_student,
                class_obj=test_class,
                assignment=assignment,
                score=45 + (i * 5),  # 45, 50
                max_score=100
            )

        # Poor attendance (65%)
        for i in range(20):
            status = 'absent' if i % 3 == 0 else 'present'  # 7 absences out of 20
            Attendance.objects.create(
                student=bad_student,
                class_obj=test_class,
                date=timezone.now().date() - timedelta(days=i),
                status=status
            )

        # Poor wellness
        WellnessCheckIn.objects.create(
            student=bad_student,
            stress_level=4,
            motivation_level=2,
            workload_level=5,
            sleep_quality=2,
            need_help=True,
            comments='Feeling overwhelmed and struggling to keep up with assignments.'
        )

        # Calculate risk assessments
        # Good Student - Low Risk
        RiskAssessment.objects.create(
            student=good_student,
            risk_level='low',
            risk_score=5,  # Very low risk
            gpa=3.6,  # 89 average = 3.6 GPA
            attendance_rate=95.0,
            missing_assignments=0
        )

        # Bad Student - High Risk  
        RiskAssessment.objects.create(
            student=bad_student,
            risk_level='high',
            risk_score=75,  # High risk
            gpa=1.9,  # 47.5 average = 1.9 GPA
            attendance_rate=65.0,
            missing_assignments=3
        )

        self.stdout.write(self.style.SUCCESS('Created test students:'))
        self.stdout.write(f'Good Student: Alice Johnson (alice_good) - Low Risk (Score: 5)')
        self.stdout.write(f'Bad Student: Bob Smith (bob_struggling) - High Risk (Score: 75)')
        self.stdout.write(f'Both enrolled in: {test_class.name} ({test_class.code})')