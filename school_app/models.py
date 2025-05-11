from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

# مدل کاربر سفارشی
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'دانش‌آموز'),
        ('teacher', 'معلم'),
        ('admin', 'مدیر'),
        ('assistant', 'معاون'),
    ]
    Educational_base_CHOICES = [
        ('Electricity', 'برق'),
        ('Networks', 'شبکه'),
        ('Electronics', 'الکترونیک'),
    ]

    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    grade = models.CharField(max_length=20)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    educational_base = models.CharField(max_length=20, choices=Educational_base_CHOICES, default='Networks')

    def save(self, *args, **kwargs):
        if self.full_name:
            self.username = self.full_name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

# مدل گروه‌های چت
class ChatGroup(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# مدل پیام‌ها
class Message(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.group.name}"

from django.db import models
from django.conf import settings
from django.utils import timezone


# مدل نمرات
class Grade(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="grades")
    subject = models.CharField(max_length=100)  # موضوع درس (مثلاً ریاضی، فیزیک)
    grade = models.DecimalField(max_digits=5, decimal_places=2)  # نمره (مانند 18.75)

    def __str__(self):
        return f"نمره {self.subject} برای {self.student.full_name}: {self.grade}"

# مدل کارنامه‌ها
class Report(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports")
    report_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"کارنامه برای {self.student.full_name} - {self.created_at.strftime('%Y-%m-%d')}"

# مدل پیام‌های خصوصی
class PrivateMessage(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_private_messages")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_private_messages")
    text = models.TextField()  # متن پیام
    created_at = models.DateTimeField(auto_now_add=True)  # تاریخ ارسال پیام

    def __str__(self):
        return f"پیام از {self.sender.full_name} به {self.receiver.full_name} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

# models.py

from django.db import models
from django.contrib.auth import get_user_model
from datetime import timedelta

class ClassGroup(models.Model):
    name = models.CharField(max_length=255)  # نام گروه درسی
    teacher = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    start_time = models.DateTimeField()  # زمان شروع گروه درسی
    end_time = models.DateTimeField()  # زمان پایان گروه درسی
    duration = models.IntegerField(null=True, blank=True)  # مدت زمان حاضری، nullable

    def save(self, *args, **kwargs):
        # محاسبه مدت زمان حاضری از تفریق زمان شروع و پایان
        if self.start_time and self.end_time:
            self.duration = int((self.end_time - self.start_time).total_seconds() / 60)  # مدت زمان به دقیقه
        super(ClassGroup, self).save(*args, **kwargs)  # ذخیره مدل

    def __str__(self):
        return self.name

class Attendance(models.Model):
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE)
    student = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    attended_at = models.DateTimeField(auto_now_add=True)  # زمانی که حضور ثبت می‌شود
    is_late = models.BooleanField(default=False)  # آیا دانش‌آموز دیر وارد شده است؟

    def __str__(self):
        return f"{self.student} - {self.class_group}"


from django.db import models

class About(models.Model):
    title = models.CharField(max_length=255)  # عنوان بخش درباره ما
    content = models.TextField()  # محتوای توضیحات
    created_at = models.DateTimeField(auto_now_add=True)  # تاریخ ایجاد

    def __str__(self):
        return self.title
