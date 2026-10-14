"""
Global Context Processors for EduManage / Ittihad Model School.
Provides centralized school branding and granular role-based permissions across all templates.
"""
from .models import SchoolSetting, Notification

def school_settings_processor(request):
    try:
        setting = SchoolSetting.get_settings()
    except Exception:
        setting = None

    context = {
        'school_setting': setting,
        'SCHOOL_NAME': setting.school_name if setting else 'Ittihad Model School',
        'is_admin_role': False,
        'is_accountant_role': False,
        'is_teacher_role': False,
        'is_student_role': False,
        'user_role_label': 'Guest',
        'current_student': None,
        'current_staff': None,
        'unread_notifications': 0,
    }

    if hasattr(request, 'user') and request.user.is_authenticated:
        user = request.user
        student = getattr(user, 'student_profile', None)
        staff = getattr(user, 'staff_profile', None)

        # 1. Accountant Role Detection
        if user.username == 'accountant' or (staff and staff.department == 'Finance'):
            context['is_accountant_role'] = True
            context['user_role_label'] = 'Accountant / Fee Dept'
            context['current_staff'] = staff

        # 2. Student Role Detection
        elif student or user.username == 'student' or user.username.startswith('std_'):
            context['is_student_role'] = True
            context['user_role_label'] = 'Student / Parent'
            context['current_student'] = student

        # 3. Teacher Role Detection
        elif user.username == 'teacher' or (staff and staff.department == 'Academics'):
            context['is_teacher_role'] = True
            context['user_role_label'] = 'Faculty Educator'
            context['current_staff'] = staff

        # 4. Admin Role Detection
        elif user.is_superuser or user.is_staff or (staff and staff.department == 'Administration'):
            context['is_admin_role'] = True
            context['user_role_label'] = 'System Administrator'
            context['current_staff'] = staff
        else:
            context['is_admin_role'] = user.is_superuser
            context['user_role_label'] = 'System Admin' if user.is_superuser else 'Staff User'

        try:
            context['unread_notifications'] = Notification.objects.filter(is_read=False).count()
        except Exception:
            context['unread_notifications'] = 0

    return context
