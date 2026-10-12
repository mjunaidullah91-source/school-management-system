"""
Global Context Processors for EduManage / Ittihad Model School.
Provides centralized school setting and branding configuration across all templates.
"""
from .models import SchoolSetting

def school_settings_processor(request):
    try:
        setting = SchoolSetting.get_settings()
    except Exception:
        setting = None
    return {
        'school_setting': setting,
        'SCHOOL_NAME': setting.school_name if setting else 'Ittihad Model School',
    }
