from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from students.models import Skill


class Company(models.Model):
    name = models.CharField(max_length=150, unique=True)
    logo = models.FileField(upload_to='company_logos/', blank=True, null=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100, default="Information Technology")
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Companies'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def initials(self):
        parts = self.name.strip().split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        return self.name[:2].upper()


class PlacementDrive(models.Model):
    STATUS_UPCOMING = 'UPCOMING'
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_CLOSED = 'CLOSED'

    STATUS_CHOICES = [
        (STATUS_UPCOMING, 'Upcoming'),
        (STATUS_ACTIVE, 'Active / Accepting Applications'),
        (STATUS_CLOSED, 'Closed / Completed'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='drives')
    job_title = models.CharField(max_length=200)
    job_role = models.CharField(max_length=100, help_text="e.g. SDE-1, Data Analyst, Cloud DevOps")
    job_description = models.TextField()
    
    # Requirements
    required_skills = models.ManyToManyField(Skill, blank=True, related_name='drives')
    min_cgpa = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=6.00,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    allowed_branches = models.TextField(
        default="Computer Science & Engineering, Information Technology, AI & Machine Learning, Data Science",
        help_text="Comma-separated list of eligible branches"
    )
    max_backlogs = models.PositiveSmallIntegerField(
        default=0,
        help_text="Maximum active backlogs allowed"
    )
    required_academic_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=50.00,
        help_text="Minimum overall verified academic score required (0-100)"
    )
    
    application_deadline = models.DateField()
    drive_date = models.DateField()
    salary_package = models.CharField(max_length=100, blank=True, help_text="e.g. 14.5 LPA (CTC)")
    additional_requirements = models.TextField(blank=True)
    
    is_published = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-drive_date', '-created_at']

    def __str__(self):
        return f"{self.company.name} - {self.job_title} ({self.get_status_display()})"

    def get_allowed_branches_list(self):
        if not self.allowed_branches:
            return []
        return [b.strip() for b in self.allowed_branches.split(',') if b.strip()]


class DriveRequirement(models.Model):
    PROFICIENCY_CHOICES = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
    ]

    drive = models.ForeignKey(PlacementDrive, on_delete=models.CASCADE, related_name='requirements')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    required_proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default='INTERMEDIATE')
    is_mandatory = models.BooleanField(default=True)

    class Meta:
        unique_together = ('drive', 'skill')

    def __str__(self):
        return f"{self.drive.job_title} - {self.skill.name} ({self.required_proficiency})"
