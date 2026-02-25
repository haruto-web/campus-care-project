from accounts.models import User
from wellness.models import Alert

for i in range(1, 11):
    try:
        student = User.objects.get(username=f'teststudent{i}')
        severity = 'critical' if i <= 5 else 'high'
        Alert.objects.create(
            student=student,
            alert_type='emotional_distress',
            severity=severity
        )
        print(f'Alert created for teststudent{i}: {severity}')
    except Exception as e:
        print(f'Error for teststudent{i}: {e}')

print('\nDone! 10 alerts created.')
