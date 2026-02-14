from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import TeacherConcern
from .forms import TeacherConcernForm
from accounts.models import User

@login_required
def create_concern(request, student_id=None):
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can report concerns.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TeacherConcernForm(request.POST)
        if form.is_valid():
            concern = form.save(commit=False)
            concern.teacher = request.user
            concern.save()
            messages.success(request, f'Concern about {concern.student.get_full_name()} reported successfully!')
            return redirect('wellness:view_concerns')
    else:
        if student_id:
            student = get_object_or_404(User, id=student_id, role='student')
            form = TeacherConcernForm(initial={'student': student})
        else:
            form = TeacherConcernForm()
        
        # Filter students to only show those in teacher's classes
        from academics.models import Class
        teacher_classes = Class.objects.filter(teacher=request.user)
        student_ids = []
        for cls in teacher_classes:
            student_ids.extend(cls.students.values_list('id', flat=True))
        form.fields['student'].queryset = User.objects.filter(id__in=student_ids, role='student')
    
    return render(request, 'wellness/create_concern.html', {'form': form})

@login_required
def view_concerns(request):
    if request.user.role != 'teacher':
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    concerns = TeacherConcern.objects.filter(teacher=request.user).order_by('-created_at')
    
    context = {
        'concerns': concerns,
    }
    return render(request, 'wellness/view_concerns.html', context)
