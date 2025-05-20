from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout
from .models import Course, Assignment, Submission, EspaceDepot, StudentDashboardTime
from .forms import (
    CourseForm, AssignmentForm, SubmissionForm, UserRegisterForm,
    LoginForm, GradingForm, EspaceDepotForm
)
from django.http import FileResponse, JsonResponse
import os


def home(request):
    return render(request, 'core/home.html')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Inscription réussie. Bienvenue !")
            if user.user_type == 'teacher':
                return redirect('teacher_dashboard')
            elif user.user_type == 'student':
                return redirect('student_dashboard')
            elif user.user_type == 'admin':
                return redirect('admin_dashboard')
            else:
                return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            from django.contrib.auth import authenticate
            user = authenticate(request, email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                messages.success(request, "Connexion réussie.")
                if user.user_type == 'teacher':
                    return redirect('teacher_dashboard')
                elif user.user_type == 'student':
                    return redirect('student_dashboard')
                elif user.user_type == 'admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('home')
            else:
                messages.error(request, "Email ou mot de passe incorrect.")
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})


@login_required
def teacher_dashboard(request):
    if request.user.user_type != 'teacher':
        messages.error(request, "Accès réservé aux enseignants.")
        return redirect('home')
    courses = Course.objects.filter(teacher=request.user)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            messages.success(request, "Cours ajouté avec succès.")
            return redirect('teacher_dashboard')
    else:
        form = CourseForm()
    # Fetch submissions for teacher's courses
    submissions_by_student = {}
    for course in courses:
        for submission in Submission.objects.filter(course=course):
            student_email = submission.student.email
            if student_email not in submissions_by_student:
                submissions_by_student[student_email] = []
            submissions_by_student[student_email].append(submission)
    return render(request, 'core/teacher_dashboard.html', {
        'courses': courses,
        'form': form,
        'submissions_by_student': submissions_by_student
    })


@login_required
def student_dashboard(request):
    if request.user.user_type != 'student':
        messages.error(request, "Accès réservé aux étudiants.")
        return redirect('home')
    courses = Course.objects.all()
    espaces = EspaceDepot.objects.all()
    # Calculate submission progress for each espace
    espace_progress = {}
    for espace in espaces:
        espace_courses = Course.objects.filter(espace_depot=espace)
        total_courses = espace_courses.count()
        total_submissions = Submission.objects.filter(course__in=espace_courses, student=request.user).count()
        if total_courses > 0:
            percentage = (total_submissions / total_courses) * 100
            espace_progress[espace.id] = min(100, max(0, percentage))  # Ensure percentage is between 0 and 100
        else:
            espace_progress[espace.id] = 0
    return render(request, 'core/student_dashboard.html', {
        'courses': courses,
        'espaces': espaces,
        'espace_progress': espace_progress
    })


@login_required
def admin_dashboard(request):
    if request.user.user_type != 'admin':
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('home')

    if request.method == 'POST':
        espace_form = EspaceDepotForm(request.POST)
        if espace_form.is_valid():
            espace_form.save()
            messages.success(request, "Espace de dépôt créé avec succès.")
            return redirect('admin_dashboard')
    else:
        espace_form = EspaceDepotForm()

    espaces = EspaceDepot.objects.all()

    # Fetch financial data
    dashboard_times = StudentDashboardTime.objects.filter(student__user_type='student')
    total_amount = sum(dt.time_spent for dt in dashboard_times)  # 1 minute = 1 dinar

    return render(request, 'core/admin_dashboard.html', {
        'espace_form': espace_form,
        'espaces': espaces,
        'dashboard_times': dashboard_times,
        'total_amount': total_amount
    })


@login_required
def add_course(request):
    if request.user.user_type != 'teacher':
        messages.error(request, "Seuls les enseignants peuvent ajouter des cours.")
        return redirect('teacher_dashboard')
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            messages.success(request, "Cours ajouté avec succès.")
            return redirect('teacher_dashboard')
    else:
        form = CourseForm()
    return render(request, 'core/add_course.html', {'form': form})


@login_required
def add_assignment(request):
    if request.user.user_type != 'teacher':
        messages.error(request, "Seuls les enseignants peuvent ajouter des assignments.")
        return redirect('teacher_dashboard')
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.teacher = request.user
            assignment.save()
            messages.success(request, "Assignment ajouté avec succès.")
            return redirect('teacher_dashboard')
    else:
        form = AssignmentForm()
    return render(request, 'core/add_assignment.html', {'form': form})


@login_required
def download_course(request, course_id):
    if request.user.user_type != 'student':
        messages.error(request, "Seuls les étudiants peuvent télécharger des cours.")
        return redirect('student_dashboard')
    course = get_object_or_404(Course, id=course_id)
    if course.file:
        file_path = course.file.path
        if os.path.exists(file_path):
            response = FileResponse(
                open(file_path, 'rb'),
                as_attachment=True,
                filename=os.path.basename(file_path)
            )
            return response
        else:
            messages.error(request, "Le fichier n'existe pas sur le serveur.")
    else:
        messages.error(request, "Aucun fichier disponible pour ce cours.")
    return redirect('student_dashboard')


@login_required
def submit_assignment(request, assignment_id):
    if request.user.user_type != 'student':
        messages.error(request, "Seuls les étudiants peuvent soumettre des travaux.")
        return redirect('student_dashboard')
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = request.user
            submission.assignment = assignment
            submission.save()
            messages.success(request, "Travail soumis avec succès.")
            return redirect('student_dashboard')
    else:
        form = SubmissionForm()
    return render(request, 'core/submit_assignment.html', {'form': form, 'assignment': assignment})


@login_required
def download_assignment(request, assignment_id):
    if request.user.user_type != 'student':
        messages.error(request, "Seuls les étudiants peuvent télécharger des assignments.")
        return redirect('student_dashboard')
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if assignment.file:
        file_path = assignment.file.path
        if os.path.exists(file_path):
            response = FileResponse(
                open(file_path, 'rb'),
                as_attachment=True,
                filename=os.path.basename(file_path)
            )
            return response
        else:
            messages.error(request, "Le fichier n'existe pas sur le serveur.")
    else:
        messages.error(request, "Aucun fichier disponible pour cet assignment.")
    return redirect('student_dashboard')


@login_required
def grade_submission(request, submission_id):
    if request.user.user_type != 'teacher':
        messages.error(request, "Seuls les enseignants peuvent grader les travaux.")
        return redirect('teacher_dashboard')
    submission = get_object_or_404(Submission, id=submission_id)
    if request.method == 'POST':
        form = GradingForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, "Note et feedback enregistrés avec succès.")
            return redirect('teacher_dashboard')
    else:
        form = GradingForm(instance=submission)
    return render(request, 'core/grade_submission.html', {'form': form, 'submission': submission})


@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'core/course_list.html', {'courses': courses})


def custom_logout(request):
    logout(request)
    return redirect('login')


@login_required
def espace_detail(request, espace_id):
    if request.user.user_type != 'student':
        messages.error(request, "Accès réservé aux étudiants.")
        return redirect('home')
    espace = get_object_or_404(EspaceDepot, id=espace_id)
    courses = Course.objects.filter(espace_depot=espace)
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        if course_id:
            course = get_object_or_404(Course, id=course_id)
            form = SubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                submission = form.save(commit=False)
                submission.student = request.user
                submission.course = course  # Link to course instead of assignment
                submission.save()
                messages.success(request, "Travail soumis avec succès.")
                return redirect('espace_detail', espace_id=espace.id)
    else:
        form = SubmissionForm()
    submissions = Submission.objects.filter(course__espace_depot=espace)  # Fetch submissions by course
    return render(request, 'core/espace_detail.html', {
        'espace': espace,
        'courses': courses,
        'form': form,
        'submissions': submissions
    })


@login_required
def update_dashboard_time(request):
    if request.user.user_type != 'student':
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    if request.method == 'POST':
        # Get or create the time tracking record for the student
        dashboard_time, created = StudentDashboardTime.objects.get_or_create(student=request.user)
        # Increment time by 1 minute
        dashboard_time.time_spent += 1
        dashboard_time.save()
        return JsonResponse({'status': 'success', 'time_spent': dashboard_time.time_spent})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
