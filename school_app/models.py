from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

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

    full_name = models.CharField("نام کامل", max_length=100)
    email = models.EmailField("ایمیل", unique=True)
    phone = models.CharField("شماره تماس", max_length=15)
    grade = models.CharField("پایه تحصیلی", max_length=20)
    role = models.CharField("نقش", max_length=10, choices=ROLE_CHOICES, default='student')
    educational_base = models.CharField("رشته تحصیلی", max_length=20, choices=Educational_base_CHOICES, default='Networks')

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def save(self, *args, **kwargs):
        if self.full_name:
            self.username = self.full_name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


# مدل گروه‌های چت
class ChatGroup(models.Model):
    name = models.CharField("نام گروه", max_length=100)

    class Meta:
        verbose_name = "گروه چت"
        verbose_name_plural = "گروه‌های چت"

    def __str__(self):
        return self.name


# مدل پیام‌ها
class Message(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='messages', verbose_name="گروه چت")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="کاربر")
    text = models.TextField("متن پیام")
    timestamp = models.DateTimeField("زمان ارسال", auto_now_add=True)

    class Meta:
        verbose_name = "پیام گروهی"
        verbose_name_plural = "پیام‌های گروهی"

    def __str__(self):
        return f"{self.user.username} - {self.group.name}"


# مدل نمرات
class Grade(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="grades", verbose_name="دانش‌آموز")
    subject = models.CharField("درس", max_length=100)
    grade = models.DecimalField("نمره", max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = "نمره"
        verbose_name_plural = "نمرات"

    def __str__(self):
        return f"نمره {self.subject} برای {self.student.full_name}: {self.grade}"


# مدل کارنامه‌ها
class Report(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports", verbose_name="دانش‌آموز")
    report_text = models.TextField("متن کارنامه")
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)

    class Meta:
        verbose_name = "کارنامه"
        verbose_name_plural = "کارنامه‌ها"

    def __str__(self):
        return f"کارنامه برای {self.student.full_name} - {self.created_at.strftime('%Y-%m-%d')}"


# مدل پیام‌های خصوصی
class PrivateMessage(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_private_messages", verbose_name="فرستنده")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_private_messages", verbose_name="گیرنده")
    text = models.TextField("متن پیام")
    created_at = models.DateTimeField("تاریخ ارسال", auto_now_add=True)

    class Meta:
        verbose_name = "پیام خصوصی"
        verbose_name_plural = "پیام‌های خصوصی"

    def __str__(self):
        return f"پیام از {self.sender.full_name} به {self.receiver.full_name} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


# مدل گروه‌های درسی
class ClassGroup(models.Model):
    name = models.CharField("نام کلاس", max_length=255)
    teacher = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'}, verbose_name="معلم")
    start_time = models.DateTimeField("زمان شروع")
    end_time = models.DateTimeField("زمان پایان")
    duration = models.IntegerField("مدت زمان (دقیقه)", null=True, blank=True)

    class Meta:
        verbose_name = "کلاس"
        verbose_name_plural = "کلاس‌ها"

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            self.duration = int((self.end_time - self.start_time).total_seconds() / 60)
        super(ClassGroup, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


# مدل حضور و غیاب
class Attendance(models.Model):
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, verbose_name="کلاس")
    student = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, verbose_name="دانش‌آموز")
    attended_at = models.DateTimeField("زمان حضور", auto_now_add=True)
    is_late = models.BooleanField("تاخیر دارد؟", default=False)

    class Meta:
        verbose_name = "حضور و غیاب"
        verbose_name_plural = "حضور و غیاب‌ها"

    def __str__(self):
        return f"{self.student} - {self.class_group}"


# مدل درباره ما
class About(models.Model):
    title = models.CharField("عنوان", max_length=255)
    content = models.TextField("محتوا")
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)

    class Meta:
        verbose_name = "درباره ما"
        verbose_name_plural = "درباره ما"

    def __str__(self):
        return self.title
