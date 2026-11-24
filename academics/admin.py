from django.contrib import admin
from .models import AcademicSubmission, AcademicEvaluation


@admin.register(AcademicSubmission)
class AcademicSubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'category', 'status', 'created_at')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('title', 'student__full_name', 'student__email')


@admin.register(AcademicEvaluation)
class AcademicEvaluationAdmin(admin.ModelAdmin):
    list_display = ('submission', 'total_marks', 'marks_relevance', 'marks_quality', 'marks_practical', 'marks_originality', 'evaluated_by', 'evaluated_at')
    search_fields = ('submission__title', 'submission__student__full_name')
