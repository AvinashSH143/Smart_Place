from django.contrib import admin
from .models import StudentProfile, Skill, StudentSkill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('name',)


@admin.register(StudentSkill)
class StudentSkillAdmin(admin.ModelAdmin):
    list_display = ('student', 'skill', 'proficiency', 'is_verified', 'verified_by', 'verified_at')
    list_filter = ('proficiency', 'is_verified', 'skill__category')
    search_fields = ('student__full_name', 'skill__name')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'branch', 'year_of_study', 'cgpa', 'is_debarred')
    list_filter = ('branch', 'year_of_study', 'is_debarred')
    search_fields = ('full_name', 'email', 'user__username')
