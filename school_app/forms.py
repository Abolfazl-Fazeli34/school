from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="رمز عبور",
        min_length=6,
        error_messages={
            'required': 'لطفاً رمز عبور را وارد کنید.',
            'min_length': 'رمز عبور باید حداقل ۶ کاراکتر باشد.'
        }
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="تکرار رمز عبور",
        error_messages={'required': 'لطفاً تکرار رمز عبور را وارد کنید.'}
    )

    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'phone', 'grade', 'educational_base', 'password']
        labels = {
            'full_name': 'نام کامل',
            'email': 'ایمیل',
            'phone': 'شماره موبایل',
            'grade': 'پایه تحصیلی',
            'educational_base': 'رشته تحصیلی',
        }
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'grade': forms.Select(attrs={'class': 'form-select'}),
            'educational_base': forms.Select(attrs={'class': 'form-select'}),
        }
        error_messages = {
            'full_name': {'required': 'لطفاً نام کامل را وارد کنید.'},
            'email': {
                'required': 'ایمیل الزامی است.',
                'invalid': 'فرمت ایمیل وارد شده معتبر نیست.'
            },
            'phone': {'required': 'شماره موبایل الزامی است.'},
            'grade': {'required': 'پایه تحصیلی را انتخاب کنید.'},
            'educational_base': {'required': 'رشته تحصیلی را انتخاب کنید.'},
        }

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if not full_name or len(full_name.strip()) < 3:
            raise ValidationError("نام کامل باید حداقل ۳ حرف باشد.")
        return full_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("ایمیل نمی‌تواند خالی باشد.")
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("این ایمیل قبلاً ثبت شده است.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise ValidationError("شماره موبایل الزامی است.")
        if not phone.startswith('09') or not phone.isdigit() or len(phone) != 11:
            raise ValidationError("شماره موبایل باید با ۰۹ شروع شود و ۱۱ رقم عددی باشد.")
        return phone

    def clean_grade(self):
        grade = self.cleaned_data.get('grade')
        if not grade:
            raise ValidationError("پایه تحصیلی الزامی است.")
        return grade

    def clean_educational_base(self):
        base = self.cleaned_data.get('educational_base')
        if not base:
            raise ValidationError("رشته تحصیلی الزامی است.")
        return base

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if not password or not confirm_password:
            raise ValidationError("رمز عبور و تکرار آن الزامی هستند.")
        if password != confirm_password:
            self.add_error('confirm_password', "رمز عبور و تکرار آن مطابقت ندارند.")
        return cleaned_data
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from .models import CustomUser

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='نام کاربری',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام کاربری'}),
        error_messages={
            'required': 'لطفاً نام کاربری را وارد کنید.',
        }
    )

    password = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'رمز عبور'}),
        error_messages={
            'required': 'لطفاً رمز عبور را وارد کنید.',
        }
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # بررسی اینکه نام کاربری خالی نباشد
        if not username or len(username.strip()) == 0:
            raise ValidationError("نام کاربری نمی‌تواند خالی باشد.")

        # بررسی اینکه نام کاربری معتبر است (وجود دارد)
        if not CustomUser.objects.filter(username=username).exists():
            raise ValidationError("نام کاربری وارد شده موجود نیست.")

        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        # بررسی اینکه رمز عبور خالی نباشد
        if not password or len(password.strip()) == 0:
            raise ValidationError("رمز عبور نمی‌تواند خالی باشد.")

        return password

    def confirm_login_allowed(self, user):
        # بررسی اینکه آیا حساب کاربری غیرفعال است یا خیر
        if not user.is_active:
            raise ValidationError("حساب کاربری شما غیرفعال است.", code='inactive')

        # بررسی اینکه نام کاربری و رمز عبور صحیح است
        if not self.authenticate_user(user):
            raise ValidationError(
                "لطفاً نام کاربری و رمز عبور صحیح وارد کنید. توجه داشته باشید که این مقادیر به حروف بزرگ و کوچک حساس هستند.")

    def authenticate_user(self, user):
        # بررسی صحت نام کاربری و رمز عبور
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            return True
        return False


# forms.py
from django import forms
from .models import CustomUser

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'phone', 'grade', 'educational_base']
        widgets = {
            'role': forms.Select(choices=CustomUser.ROLE_CHOICES),
            'educational_base': forms.Select(choices=CustomUser.Educational_base_CHOICES),
        }

from django import forms

class MessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'پیام خود را بنویسید...'}))


from django import forms
from .models import Grade

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['subject', 'grade']  # فیلدهای فرم برای ارسال نمرات

from django import forms
from .models import Report

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['report_text']  # فیلد فرم برای ارسال کارنامه

from django import forms
from .models import PrivateMessage

class PrivateMessageForm(forms.ModelForm):
    class Meta:
        model = PrivateMessage
        fields = ['text']  # فیلد فرم برای ارسال پیام


from django import forms
from .models import CustomUser

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'phone', 'grade', 'educational_base']
        labels = {
            'full_name': 'نام کامل',
            'email': 'ایمیل',
            'phone': 'شماره موبایل',
            'grade': 'پایه تحصیلی',
            'educational_base': 'رشته تحصیلی',
        }
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام کامل خود را وارد کنید'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ایمیل خود را وارد کنید'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شماره موبایل خود را وارد کنید'}),
            'grade': forms.Select(attrs={'class': 'form-select'}),
            'educational_base': forms.Select(attrs={'class': 'form-select'}),
        }
        error_messages = {
            'full_name': {'required': 'لطفاً نام کامل خود را وارد کنید.'},
            'email': {'required': 'ایمیل الزامی است.', 'invalid': 'فرمت ایمیل وارد شده معتبر نیست.'},
            'phone': {'required': 'شماره موبایل الزامی است.'},
            'grade': {'required': 'پایه تحصیلی را انتخاب کنید.'},
            'educational_base': {'required': 'رشته تحصیلی را انتخاب کنید.'},
        }

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if not full_name or len(full_name.strip()) < 3:
            raise forms.ValidationError("نام کامل باید حداقل ۳ حرف باشد.")
        return full_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('09') or len(phone) != 11:
            raise forms.ValidationError("شماره موبایل باید با ۰۹ شروع شود و ۱۱ رقم باشد.")
        return phone

# forms.py
from django import forms
from .models import ClassGroup

class ClassGroupForm(forms.ModelForm):
    class Meta:
        model = ClassGroup
        fields = ['name', 'start_time', 'end_time']  # حذف فیلد duration از فرم
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("زمان شروع نباید بعد از زمان پایان باشد.")
        return cleaned_data

from django import forms
from .models import ChatGroup

class ChatGroupForm(forms.ModelForm):
    class Meta:
        model = ChatGroup
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام گروه چت را وارد کنید'})
        }

# school/forms.py


from django import forms
from .models import CustomUser

class CustomUserFormRole(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'phone', 'grade', 'educational_base', 'role']  # اضافه کردن فیلد role

    role = forms.ChoiceField(choices=CustomUser.role, required=False)  # انتخاب نقش برای کاربر


class CustomUserFormRole2(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'role']  # فیلد نقش اضافه شود

