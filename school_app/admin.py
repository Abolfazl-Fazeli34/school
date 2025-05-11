from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, About


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # فیلدهایی که در لیست کاربران نمایش داده می‌شن
    list_display = (
        'username', 'full_name', 'email', 'phone', 'role', 'grade', 'educational_base',
        'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined'
    )

    # فیلترها برای لیست کاربران
    list_filter = (
        'role', 'educational_base', 'grade', 'is_active', 'is_staff', 'is_superuser',
        'date_joined', 'last_login'
    )

    # قابلیت جستجو روی این فیلدها
    search_fields = ('username', 'full_name', 'email', 'phone', 'role')

    # مرتب‌سازی پیش‌فرض لیست
    ordering = ('username',)

    # فیلدهایی که هنگام ساخت کاربر جدید در پنل ادمین نمایش داده می‌شن
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2', 'full_name', 'email', 'phone',
                'grade', 'role', 'educational_base', 'is_active', 'is_staff'
            )
        }),
    )

    # فیلدهایی که هنگام ویرایش کاربر در پنل ادمین نمایش داده می‌شن
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('اطلاعات شخصی', {'fields': ('full_name', 'email', 'phone', 'grade', 'educational_base')}),
        ('دسترسی‌ها', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('تاریخ‌ها', {'fields': ('last_login', 'date_joined')}),
    )

    # اعمال تغییرات در فرم‌ها برای افزایش امنیت
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # اگر کاربر در حال ویرایش است، اجازه تغییر رمز عبور نمی‌دهیم (در صورت نیاز می‌توانید این را حذف کنید)
        if obj:
            form.base_fields['password'].widget.attrs['readonly'] = True
        return form

    # نمایش اطلاعات دقیق‌تر برای کاربران در جدول
    def last_login(self, obj):
        return obj.last_login.strftime('%Y-%m-%d %H:%M:%S') if obj.last_login else "---"

    def date_joined(self, obj):
        return obj.date_joined.strftime('%Y-%m-%d %H:%M:%S') if obj.date_joined else "---"

    last_login.admin_order_field = 'last_login'  # ترتیب‌بندی
    date_joined.admin_order_field = 'date_joined'  # ترتیب‌بندی

    # ویرایش برخی فیلدها در جدول
    def get_list_editable(self, request):
        return ['full_name', 'phone', 'grade', 'educational_base', 'role', 'is_active', 'is_staff']

    def save_model(self, request, obj, form, change):
        # بررسی و انجام برخی عملیات قبل از ذخیره داده (اگر نیاز باشد)
        if not obj.password:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)

    # فارسی‌سازی عنوان‌ها و توضیحات در پنل ادمین
    # عنوان‌ها در ادمین برای بخش‌ها
    list_display_links = ('username', 'full_name')

    # فارسی‌سازی فیلدهای مختلف
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2', 'full_name', 'email', 'phone',
                'grade', 'role', 'educational_base', 'is_active', 'is_staff'
            )
        }),
    )

    # فارسی‌سازی فیلدهای مربوط به اطلاعات شخصی و دسترسی‌ها
    fieldsets = (
        ('اطلاعات شخصی', {'fields': ('full_name', 'email', 'phone', 'grade', 'educational_base')}),
        ('دسترسی‌ها', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('تاریخ‌ها', {'fields': ('last_login', 'date_joined')}),
    )

    # فیلدهای مربوط به لیست کاربران که نیاز به ویرایش دارند
    get_list_editable = ['full_name', 'phone', 'grade', 'educational_base', 'role', 'is_active', 'is_staff']


from django.contrib import admin
from .models import ChatGroup, Message
from django.utils.html import format_html

@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


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

from django.contrib import admin
from .models import Grade, Report, PrivateMessage
from django.contrib.auth import get_user_model
from django.utils.html import format_html

# مدل نمرات
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'grade', 'view_student')
    search_fields = ('student__username', 'subject')
    list_filter = ('subject',)

    # نمایش نام کامل دانش‌آموز در لیست نمرات
    def view_student(self, obj):
        return format_html('<a href="/admin/auth/user/{}/change/">{}</a>', obj.student.id, obj.student.get_full_name())
    view_student.short_description = 'دانش‌آموز'

# مدل کارنامه‌ها
class ReportAdmin(admin.ModelAdmin):
    list_display = ('student', 'created_at', 'view_student')
    search_fields = ('student__username',)
    list_filter = ('created_at',)

    # نمایش نام کامل دانش‌آموز در لیست کارنامه‌ها
    def view_student(self, obj):
        return format_html('<a href="/admin/auth/user/{}/change/">{}</a>', obj.student.id, obj.student.get_full_name())
    view_student.short_description = 'دانش‌آموز'

# مدل پیام‌های خصوصی
class PrivateMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'created_at', 'view_sender', 'view_receiver')
    search_fields = ('sender__username', 'receiver__username')
    list_filter = ('created_at',)

    # نمایش نام کامل فرستنده
    def view_sender(self, obj):
        return format_html('<a href="/admin/auth/user/{}/change/">{}</a>', obj.sender.id, obj.sender.get_full_name())
    view_sender.short_description = 'فرستنده'

    # نمایش نام کامل دریافت‌کننده
    def view_receiver(self, obj):
        return format_html('<a href="/admin/auth/user/{}/change/">{}</a>', obj.receiver.id, obj.receiver.get_full_name())
    view_receiver.short_description = 'دریافت‌کننده'

# ثبت مدل‌ها در ادمین
admin.site.register(Grade, GradeAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(PrivateMessage, PrivateMessageAdmin)

from django.contrib import admin
from .models import ClassGroup, Attendance

class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'start_time', 'end_time')
    search_fields = ('name', 'teacher__username')
    list_filter = ('teacher',)

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('class_group', 'student', 'attended_at', 'is_late')
    list_filter = ('class_group', 'student', 'is_late')
    search_fields = ('class_group__name', 'student__username')

admin.site.register(ClassGroup, ClassGroupAdmin)
admin.site.register(Attendance, AttendanceAdmin)


admin.site.register(About)