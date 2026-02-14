from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Class, Announcement, Material
from .forms import ClassForm

@login_required
def class_detail(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    
    # Check if user has access
    if request.user.role == 'student':
        if request.user not in class_obj.students.all():
            messages.error(request, 'You are not enrolled in this class.')
            return redirect('dashboard')
    elif request.user.role == 'teacher':
        if class_obj.teacher != request.user:
            messages.error(request, 'You do not teach this class.')
            return redirect('dashboard')
    
    announcements = class_obj.announcements.all()
    materials = class_obj.materials.all()
    assignments = class_obj.assignments.all().order_by('-due_date')
    
    context = {
        'class': class_obj,
        'announcements': announcements,
        'materials': materials,
        'assignments': assignments,
    }
    return render(request, 'academics/class_detail.html', context)

@login_required
def create_announcement(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    
    # Only teacher can create announcements
    if request.user.role != 'teacher' or class_obj.teacher != request.user:
        messages.error(request, 'Only the class teacher can post announcements.')
        return redirect('academics:class_detail', class_id=class_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        priority = request.POST.get('priority', 'normal')
        
        Announcement.objects.create(
            class_obj=class_obj,
            author=request.user,
            title=title,
            content=content,
            priority=priority
        )
        messages.success(request, 'Announcement posted successfully!')
        return redirect('academics:class_detail', class_id=class_id)
    
    return render(request, 'academics/create_announcement.html', {'class': class_obj})

@login_required
def create_class(request):
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can create classes.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            class_obj = form.save(commit=False)
            class_obj.teacher = request.user
            class_obj.save()
            messages.success(request, f'Class {class_obj.code} created successfully!')
            return redirect('dashboard')
    else:
        form = ClassForm()
    
    return render(request, 'academics/create_class.html', {'form': form})

@login_required
def manage_students(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    
    # Only teacher of the class can manage students
    if request.user.role != 'teacher' or class_obj.teacher != request.user:
        messages.error(request, 'You do not have permission to manage students for this class.')
        return redirect('dashboard')
    
    # Get search query
    search_query = request.GET.get('search', '')
    
    # Get all students
    from accounts.models import User
    all_students = User.objects.filter(role='student')
    
    if search_query:
        all_students = all_students.filter(
            first_name__icontains=search_query
        ) | all_students.filter(
            last_name__icontains=search_query
        ) | all_students.filter(
            username__icontains=search_query
        ) | all_students.filter(
            email__icontains=search_query
        )
    
    enrolled_students = class_obj.students.all()
    available_students = all_students.exclude(id__in=enrolled_students.values_list('id', flat=True))
    
    context = {
        'class': class_obj,
        'enrolled_students': enrolled_students,
        'available_students': available_students,
        'search_query': search_query,
    }
    return render(request, 'academics/manage_students.html', context)

@login_required
def add_student(request, class_id, student_id):
    class_obj = get_object_or_404(Class, id=class_id)
    
    if request.user.role != 'teacher' or class_obj.teacher != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    from accounts.models import User
    student = get_object_or_404(User, id=student_id, role='student')
    class_obj.students.add(student)
    messages.success(request, f'{student.get_full_name()} added to {class_obj.code}!')
    return redirect('academics:manage_students', class_id=class_id)

@login_required
def remove_student(request, class_id, student_id):
    class_obj = get_object_or_404(Class, id=class_id)
    
    if request.user.role != 'teacher' or class_obj.teacher != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    from accounts.models import User
    student = get_object_or_404(User, id=student_id)
    class_obj.students.remove(student)
    messages.success(request, f'{student.get_full_name()} removed from {class_obj.code}!')
    return redirect('academics:manage_students', class_id=class_id)
