from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from pyexpat.errors import messages as expat_messages

from .forms import RegisterForm, LoginForm, ProfileForm, GradeForm, ReportForm, PrivateMessageForm, ClassGroupForm, ChatGroupForm
from .models import ChatGroup, Message, CustomUser, Grade, Report, PrivateMessage, ClassGroup, Attendance, About


# صفحه خانه
@login_required(login_url='login')
def home(request):
    return render(request, 'home.html')


# ثبت‌نام
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # هش کردن رمز
            user.save()
            login(request, user)  # ورود خودکار بعد از ثبت‌نام
            return redirect('login')
        else:
            messages.error(request, 'اطلاعات وارد شده معتبر نیست!')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


# ورود
class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = LoginForm


# خروج از حساب
def logout_view(request):
    logout(request)
    return redirect('login')


# پروفایل کاربر
@login_required
def profile_view(request):
    user = request.user

    # دریافت نمرات، کارنامه‌ها و پیام‌های ارسال‌شده به این کاربر
    grades = Grade.objects.filter(student=user)
    reports = Report.objects.filter(student=user)
    messages = PrivateMessage.objects.filter(receiver=user)

    if user.role == 'teacher':
        students = CustomUser.objects.filter(educational_base=user.educational_base, grade=user.grade, role='student')
        student_messages = PrivateMessage.objects.filter(sender=user, receiver__in=students)
        student_grades = Grade.objects.filter(student__in=students)
        student_reports = Report.objects.filter(student__in=students)

        return render(request, 'teacher_students.html', {
            'teacher': user,
            'students': students,
            'student_grades': student_grades,
            'student_reports': student_reports,
            'student_messages': student_messages,
        })

    return render(request, 'profile.html', {
        'form': ProfileForm(instance=user),
        'user': user,
        'grades': grades,
        'reports': reports,
        'messages': messages,
    })


# صفحه چت گروهی
@login_required
def chat_view(request):
    groups = ChatGroup.objects.all()

    selected_group_id = request.GET.get('group_id')
    selected_group = None
    if selected_group_id:
        try:
            selected_group = ChatGroup.objects.get(id=selected_group_id)
        except ChatGroup.DoesNotExist:
            selected_group = None
            messages.error(request, 'گروه چت یافت نشد.')

    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        message = request.POST.get('message')
        if group_id and message:
            try:
                group = ChatGroup.objects.get(id=group_id)
                Message.objects.create(group=group, user=request.user, text=message, timestamp=timezone.now())
                return redirect(f'{request.path}?group_id={group_id}')
            except ChatGroup.DoesNotExist:
                messages.error(request, 'گروه چت وجود ندارد.')
    if selected_group:
        messages = Message.objects.filter(group=selected_group).order_by('timestamp')
    else:
        messages = []

    return render(request, 'chat.html', {
        'groups': groups,
        'selected_group': selected_group,
        'messages': messages,
    })


# مدیریت دانش‌آموزان برای معلمان
@login_required
def teacher_students(request):
    teacher = request.user

    if teacher.role != 'teacher':
        messages.error(request, 'شما مجوز دسترسی به این بخش را ندارید.')
        return redirect('home')

    students = CustomUser.objects.filter(role='student', educational_base=teacher.educational_base, grade=teacher.grade)

    report_form = ReportForm()
    grade_form = GradeForm()
    message_form = PrivateMessageForm()

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student = get_object_or_404(CustomUser, id=student_id)

        if 'send_grades' in request.POST:
            form = GradeForm(request.POST)
            if form.is_valid():
                grade = form.save(commit=False)
                grade.student = student
                grade.save()
                messages.success(request, 'نمرات با موفقیت ارسال شد!')
        elif 'send_report' in request.POST:
            form = ReportForm(request.POST)
            if form.is_valid():
                report = form.save(commit=False)
                report.student = student
                report.save()
                messages.success(request, 'کارنامه با موفقیت ارسال شد!')
        elif 'send_message' in request.POST:
            form = PrivateMessageForm(request.POST)
            if form.is_valid():
                message = form.save(commit=False)
                message.sender = teacher
                message.receiver = student
                message.save()
                messages.success(request, 'پیام با موفقیت ارسال شد!')

        return redirect('teacher_students')

    student_messages = PrivateMessage.objects.filter(receiver__in=students, sender=teacher)

    return render(request, 'teacher_students.html', {
        'teacher': teacher,
        'students': students,
        'report_form': report_form,
        'grade_form': grade_form,
        'message_form': message_form,
        'student_messages': student_messages,
    })


# مدیریت گروه‌های درسی
@login_required
def manage_class_groups(request):
    groups = ClassGroup.objects.filter(teacher=request.user)

    if request.method == 'POST':
        form = ClassGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.teacher = request.user
            group.duration = (group.end_time - group.start_time).total_seconds() / 60
            group.save()
            messages.success(request, 'گروه درسی با موفقیت ایجاد شد!')
            return redirect('manage_class_groups')
        else:
            messages.error(request, 'اطلاعات وارد شده معتبر نیست!')
    else:
        form = ClassGroupForm()

    return render(request, 'manage_class_groups.html', {'form': form, 'groups': groups})


# صفحه حضور و غیاب
@login_required
def student_attendance(request):
    groups = ClassGroup.objects.all()
    today = timezone.now()
    attendances = []

    for group in groups:
        is_late = today > group.end_time
        attendance = Attendance.objects.filter(class_group=group, student=request.user)

        if group.start_time <= today <= group.end_time:
            if not attendance.exists():
                attendances.append({'group': group, 'attendance': None, 'is_late': is_late, 'can_mark': True})
            else:
                attendances.append({'group': group, 'attendance': attendance.first(), 'is_late': is_late, 'can_mark': False})
        else:
            attendances.append({'group': group, 'attendance': attendance.first() if attendance.exists() else None, 'is_late': is_late, 'can_mark': False})

    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        group = get_object_or_404(ClassGroup, id=group_id)

        if group.start_time <= today <= group.end_time:
            attendance, created = Attendance.objects.get_or_create(class_group=group, student=request.user)
            if created:
                return redirect('student_attendance')

    return render(request, 'student_attendance.html', {'attendances': attendances})


# ایجاد گروه چت
@login_required
def create_chat_group(request):
    if request.method == 'POST':
        form = ChatGroupForm(request.POST)
        if form.is_valid():
            chat_group = form.save()
            messages.success(request, 'گروه چت با موفقیت ایجاد شد!')
            return redirect('manage_chat_groups')
        else:
            messages.error(request, 'ایجاد گروه چت ناموفق بود.')
    else:
        form = ChatGroupForm()

    return render(request, 'create_chat_group.html', {'form': form})


# درباره ما
def about_view(request):
    about = About.objects.last()
    return render(request, 'about.html', {'about': about})
