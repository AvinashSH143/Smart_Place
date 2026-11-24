import os
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from students.models import StudentProfile, Skill


def validate_academic_file(file):
    max_size = 5 * 1024 * 1024  # 5 MB
    if file.size > max_size:
        raise ValidationError("File size exceeds maximum allowed limit of 5 MB.")

    valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.docx']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError(f"Unsupported file format '{ext}'. Allowed formats: PDF, JPG, PNG, DOCX.")


class AcademicSubmission(models.Model):
    CATEGORY_CERTIFICATE = 'CERTIFICATE'
    CATEGORY_PROJECT = 'PROJECT'
    CATEGORY_SKILL = 'SKILL'
    CATEGORY_ACHIEVEMENT = 'ACHIEVEMENT'

    CATEGORY_CHOICES = [
        (CATEGORY_CERTIFICATE, 'Academic Certificate'),
        (CATEGORY_PROJECT, 'Project Showcase'),
        (CATEGORY_SKILL, 'Skill Verification'),
        (CATEGORY_ACHIEVEMENT, 'Other Achievement'),
    ]

    STATUS_PENDING = 'PENDING'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_RESUBMISSION = 'RESUBMISSION'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Review'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_RESUBMISSION, 'Resubmission Required'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='submissions')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    file = models.FileField(upload_to='academic_docs/%Y/%m/', validators=[validate_academic_file])
    related_skill = models.ForeignKey(Skill, on_delete=models.SET_NULL, null=True, blank=True, related_name='submissions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.student.full_name} ({self.get_status_display()})"

    @property
    def awarded_marks(self):
        if hasattr(self, 'evaluation') and self.evaluation:
            return self.evaluation.total_marks
        return None

    @property
    def file_extension(self):
        return os.path.splitext(self.file.name)[1].lower().replace('.', '')


class AcademicEvaluation(models.Model):
    submission = models.OneToOneField(AcademicSubmission, on_delete=models.CASCADE, related_name='evaluation')
    evaluated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluations')
    
    # Transparent Rubric
    marks_relevance = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        help_text="Relevance (Max 20 marks)"
    )
    marks_quality = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(30)],
        help_text="Quality of content (Max 30 marks)"
    )
    marks_practical = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(25)],
        help_text="Practical application (Max 25 marks)"
    )
    marks_originality = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(25)],
        help_text="Originality and presentation (Max 25 marks)"
    )
    total_marks = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Automatically computed sum (Max 100)"
    )
    
    feedback = models.TextField(help_text="Constructive evaluation feedback for the student")
    evaluated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-evaluated_at']

    def clean(self):
        super().clean()
        self.total_marks = (
            (self.marks_relevance or 0) +
            (self.marks_quality or 0) +
            (self.marks_practical or 0) +
            (self.marks_originality or 0)
        )
        if self.total_marks > 100:
            raise ValidationError("Total marks cannot exceed 100.")

    def save(self, *args, **kwargs):
        self.total_marks = (
            (self.marks_relevance or 0) +
            (self.marks_quality or 0) +
            (self.marks_practical or 0) +
            (self.marks_originality or 0)
        )
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Evaluation for {self.submission.title} - {self.total_marks}/100"
