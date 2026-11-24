from django.contrib import admin
from .models import DisciplineRecord, DisciplineAppeal


@admin.register(DisciplineRecord)
class DisciplineRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'incident_category', 'incident_date', 'status', 'is_debarred')
    list_filter = ('incident_category', 'status', 'is_debarred')
    search_fields = ('student__full_name', 'student__email')


@admin.register(DisciplineAppeal)
class DisciplineAppealAdmin(admin.ModelAdmin):
    list_display = ('record', 'student', 'status', 'reviewed_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('student__full_name', 'appeal_statement')
