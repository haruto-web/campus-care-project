from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from accounts.utils import log_action


def get_report_data():
    from accounts.models import User
    from wellness.models import RiskAssessment, Alert, Intervention
    from academics.models import Class, Assignment, Submission

    students = User.objects.filter(role='student')
    high_risk = RiskAssessment.objects.filter(risk_level='high').select_related('student')
    medium_risk = RiskAssessment.objects.filter(risk_level='medium').select_related('student')
    low_risk = RiskAssessment.objects.filter(risk_level='low').select_related('student')

    return {
        'generated': timezone.now().strftime('%B %d, %Y %I:%M %p'),
        'total_students': students.count(),
        'total_teachers': User.objects.filter(role='teacher').count(),
        'total_counselors': User.objects.filter(role='counselor').count(),
        'total_classes': Class.objects.count(),
        'high_risk': high_risk,
        'medium_risk': medium_risk,
        'low_risk': low_risk,
        'unresolved_alerts': Alert.objects.filter(resolved=False).count(),
        'pending_interventions': Intervention.objects.filter(status='scheduled').count(),
    }


@login_required
def download_report(request):
    if request.user.role not in ('admin', 'counselor'):
        from django.shortcuts import redirect
        return redirect('dashboard')

    fmt = request.GET.get('format', 'pdf')
    data = get_report_data()
    log_action(request, 'REPORT_DOWNLOADED', 'Report', None, fmt)

    if fmt == 'pdf':
        return _pdf_report(data)
    return _docx_report(data)


def _pdf_report(data):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from io import BytesIO

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('title', parent=styles['Title'], fontSize=20, textColor=colors.HexColor('#DC2626'))
    story.append(Paragraph('BrightTrack — School Report', title_style))
    story.append(Paragraph(f'Generated: {data["generated"]}', styles['Normal']))
    story.append(Spacer(1, 20))

    story.append(Paragraph('Summary', styles['Heading2']))
    summary = [
        ['Metric', 'Count'],
        ['Total Students', data['total_students']],
        ['Total Teachers', data['total_teachers']],
        ['Total Counselors', data['total_counselors']],
        ['Total Classes', data['total_classes']],
        ['Unresolved Alerts', data['unresolved_alerts']],
        ['Pending Interventions', data['pending_interventions']],
    ]
    t = Table(summary, colWidths=[250, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DC2626')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FEF2F2')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    for label, qs, color in [
        ('High Risk Students', data['high_risk'], '#DC2626'),
        ('Medium Risk Students', data['medium_risk'], '#D97706'),
        ('Low Risk Students', data['low_risk'], '#059669'),
    ]:
        story.append(Paragraph(label, styles['Heading2']))
        rows = [['Name', 'GPA', 'Attendance', 'Missing']]
        for r in qs:
            rows.append([
                r.student.get_full_name(),
                str(r.gpa or 'N/A'),
                f'{r.attendance_rate or "N/A"}%',
                str(r.missing_assignments),
            ])
        if len(rows) == 1:
            rows.append(['No students', '', '', ''])
        t2 = Table(rows, colWidths=[200, 80, 100, 80])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t2)
        story.append(Spacer(1, 16))

    doc.build(story)
    buf.seek(0)
    response = HttpResponse(buf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="brighttrack_report.pdf"'
    return response


def _docx_report(data):
    from docx import Document
    from docx.shared import Pt, RGBColor
    from io import BytesIO

    doc = Document()
    doc.add_heading('BrightTrack — School Report', 0)
    doc.add_paragraph(f'Generated: {data["generated"]}')

    doc.add_heading('Summary', level=1)
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Table Grid'
    table.rows[0].cells[0].text = 'Metric'
    table.rows[0].cells[1].text = 'Count'
    for label, val in [
        ('Total Students', data['total_students']),
        ('Total Teachers', data['total_teachers']),
        ('Total Counselors', data['total_counselors']),
        ('Total Classes', data['total_classes']),
        ('Unresolved Alerts', data['unresolved_alerts']),
        ('Pending Interventions', data['pending_interventions']),
    ]:
        row = table.add_row()
        row.cells[0].text = label
        row.cells[1].text = str(val)

    for label, qs in [
        ('High Risk Students', data['high_risk']),
        ('Medium Risk Students', data['medium_risk']),
        ('Low Risk Students', data['low_risk']),
    ]:
        doc.add_heading(label, level=1)
        t2 = doc.add_table(rows=1, cols=4)
        t2.style = 'Table Grid'
        for i, h in enumerate(['Name', 'GPA', 'Attendance', 'Missing']):
            t2.rows[0].cells[i].text = h
        for r in qs:
            row = t2.add_row()
            row.cells[0].text = r.student.get_full_name()
            row.cells[1].text = str(r.gpa or 'N/A')
            row.cells[2].text = f'{r.attendance_rate or "N/A"}%'
            row.cells[3].text = str(r.missing_assignments)
        if not qs.exists():
            row = t2.add_row()
            row.cells[0].text = 'No students'

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    response = HttpResponse(buf, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename="brighttrack_report.docx"'
    return response
