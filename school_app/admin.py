from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    CustomUser, About, ChatGroup, Message,
    Grade, Report, PrivateMessage, ClassGroup, Attendance
)


# ======= مدیریت کاربران =======
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = (
        'username', 'full_name', 'email', 'phone', 'role',
        'grade', 'educational_base', 'is_active',
        'is_staff', 'is_superuser', 'last_login_display', 'date_joined_display'
    )
    list_display_links = ('username', 'full_name')
    list_filter = (
        'role', 'educational_base', 'grade',
        'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login'
    )
    search_fields = ('username', 'full_name', 'email', 'phone', 'role')
    ordering = ('username',)

    # فیلدهای ساخت کاربر جدید
    add_fieldsets = (
        ('مشخصات اولیه', {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2', 'full_name', 'email', 'phone',
                'grade', 'role', 'educational_base', 'is_active', 'is_staff'
            )
        }),
    )

    # فیلدهای ویرایش کاربر
    fieldsets = (
        ('مشخصات ورود', {'fields': ('username', 'password')}),
        ('اطلاعات شخصی', {'fields': ('full_name', 'email', 'phone', 'grade', 'educational_base')}),
        ('دسترسی‌ها', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('تاریخ‌ها', {'fields': ('last_login', 'date_joined')}),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['password'].widget.attrs['readonly'] = True
        return form

    def last_login_display(self, obj):
        return obj.last_login.strftime('%Y-%m-%d %H:%M:%S') if obj.last_login else "---"
    last_login_display.short_description = 'آخرین ورود'
    last_login_display.admin_order_field = 'last_login'

    def date_joined_display(self, obj):
        return obj.date_joined.strftime('%Y-%m-%d %H:%M:%S') if obj.date_joined else "---"
    date_joined_display.short_description = 'تاریخ عضویت'
    date_joined_display.admin_order_field = 'date_joined'

    def save_model(self, request, obj, form, change):
        if not obj.password:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)


# ======= مدیریت گروه‌های چت =======
@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


# ======= مدیریت پیام‌های گروهی =======
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('short_text', 'user_display', 'group', 'timestamp', 'is_recent')
    list_filter = ('group', 'timestamp')
    search_fields = ('text', 'user__username', 'group__name')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)

    def short_text(self, obj):
        return obj.text[:30] + ('...' if len(obj.text) > 30 else '')
    short_text.short_description = 'متن پیام'

    def user_display(self, obj):
        return f"{obj.user.get_full_name() or obj.user.username} ({obj.user.role})"
    user_display.short_description = 'ارسال‌کننده'

    def is_recent(self, obj):
        return obj.timestamp.date().today() == obj.timestamp.date()
    is_recent.boolean = True
    is_recent.short_description = 'جدید؟'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'group')


# ======= مدیریت نمرات =======
@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'grade', 'view_student')
    search_fields = ('student__username', 'subject')
    list_filter = ('subject',)

    def view_student(self, obj):
        return format_html('<a href="/admin/auth/user/{}/change/">{}</a>', obj.student.id, obj.student.get_full_name())
    view_student.short_description = 'دانش‌آموز'


# ======= مدیریت کارنامه =======
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('student', 'created_at', 'view_student')
    search_fields = ('student__username',)
    list_filter = ('created_at',)

    def view_student(self, obj):
        return format_html('<a href="/admin/auth/user/{}/change/">{}</a>', obj.student.id, obj.student.get_full_name())
    view_student.short_description = 'دانش‌آموز'


# ======= مدیریت پیام‌های خصوصی =======
@admin.register(PrivateMessage)
class PrivateMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'created_at', 'view_sender', 'view_receiver')
    search_fields = ('sender__username', 'receiver__username')
    list_filter = ('created_at',)

    def view_sender(self, obj):
        return format_html('<a href="/admin/auth/user/{}/change/">{}</a>', obj.sender.id, obj.sender.get_full_name())
    view_sender.short_description = 'فرستنده'

    def view_receiver(self, obj):
        return format_html('<a href="/admin/auth/user/{}/change/">{}</a>', obj.receiver.id, obj.receiver.get_full_name())
    view_receiver.short_description = 'گیرنده'


# ======= مدیریت کلاس‌ها =======
@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'start_time', 'end_time')
    search_fields = ('name', 'teacher__username')
    list_filter = ('teacher',)


# ======= مدیریت حضور و غیاب =======
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('class_group', 'student', 'attended_at', 'is_late')
    list_filter = ('class_group', 'student', 'is_late')
    search_fields = ('class_group__name', 'student__username')


# ======= مدیریت درباره ما =======
admin.site.register(About)


# ======= عنوان‌های فارسی پنل مدیریت =======
admin.site.site_header = "مدیریت سامانه کلاسی"
admin.site.site_title = "پنل مدیریت کلاس"
admin.site.index_title = "داشبورد مدیریت"
