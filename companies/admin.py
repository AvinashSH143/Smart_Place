from django.contrib import admin
from .models import Company, PlacementDrive, DriveRequirement


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'website', 'created_at')
    search_fields = ('name', 'industry')


class DriveRequirementInline(admin.TabularInline):
    model = DriveRequirement
    extra = 1


@admin.register(PlacementDrive)
class PlacementDriveAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'company', 'job_role', 'min_cgpa', 'drive_date', 'application_deadline', 'status', 'is_published')
    list_filter = ('status', 'is_published', 'company')
    search_fields = ('job_title', 'company__name', 'job_role')
    inlines = [DriveRequirementInline]
