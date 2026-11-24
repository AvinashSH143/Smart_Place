from django.db import models
from django.contrib.auth.models import User
from students.models import StudentProfile


class DisciplineRecord(models.Model):
    CATEGORY_ALCOHOL = 'ALCOHOL'
    CATEGORY_MOBILE = 'MOBILE'
    CATEGORY_FIGHTING = 'FIGHTING'
    CATEGORY_MISCONDUCT = 'MISCONDUCT'
    CATEGORY_OTHER = 'OTHER'

    CATEGORY_CHOICES = [
        (CATEGORY_ALCOHOL, 'Alcohol/Substance Violation in Campus/Class'),
        (CATEGORY_MOBILE, 'Unauthorized Mobile Device Use During Exam/Class'),
        (CATEGORY_FIGHTING, 'Physical Altercation or Fighting'),
        (CATEGORY_MISCONDUCT, 'Serious Behavioral Misconduct / Disruption'),
        (CATEGORY_OTHER, 'Other Documented Code of Conduct Violation'),
    ]

    STATUS_UNDER_REVIEW = 'UNDER_REVIEW'
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_DISMISSED = 'DISMISSED'
    STATUS_APPEALED = 'APPEALED'

    STATUS_CHOICES = [
        (STATUS_UNDER_REVIEW, 'Under Formal Review'),
        (STATUS_CONFIRMED, 'Confirmed Violation'),
        (STATUS_DISMISSED, 'Dismissed / Exonerated'),
        (STATUS_APPEALED, 'Under Appeal Review'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='discipline_records')
    incident_category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    incident_date = models.DateField()
    description = models.TextField(help_text="Detailed objective account of the incident")
    supporting_evidence = models.FileField(upload_to='discipline_evidence/', blank=True, null=True)
    admin_remarks = models.TextField(blank=True, help_text="Institutional inquiry notes and remarks")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_UNDER_REVIEW)

    # Debarment details
    is_debarred = models.BooleanField(default=False)
    debarment_start = models.DateField(null=True, blank=True)
    debarment_end = models.DateField(null=True, blank=True)
    placement_restrictions = models.TextField(
        blank=True, 
        help_text="Specific restrictions, e.g. 'Debarred from all Tier-1 drives until Jan 2027'"
    )
    admin_decision_notes = models.TextField(
        blank=True,
        help_text="Official rationale, hearings summary, and disciplinary board verdict"
    )

    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recorded_incidents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-incident_date', '-created_at']

    def __str__(self):
        return f"{self.student.full_name} - {self.get_incident_category_display()} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # Sync debarment status with student profile
        super().save(*args, **kwargs)
        # Update student profile debarred status if this record debarred them
        active_debarment = DisciplineRecord.objects.filter(
            student=self.student,
            is_debarred=True,
            status=DisciplineRecord.STATUS_CONFIRMED
        ).exists()
        if self.student.is_debarred != active_debarment:
            self.student.is_debarred = active_debarment
            if active_debarment:
                self.student.debarred_reason = self.placement_restrictions or self.admin_decision_notes or "Debarred under disciplinary policy."
            else:
                self.student.debarred_reason = ""
            self.student.save(update_fields=['is_debarred', 'debarred_reason'])


class DisciplineAppeal(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Review'),
        (STATUS_APPROVED, 'Appeal Upheld / Reinstated'),
        (STATUS_REJECTED, 'Appeal Rejected / Penalty Maintained'),
    ]

    record = models.ForeignKey(DisciplineRecord, on_delete=models.CASCADE, related_name='appeals')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='appeals')
    appeal_statement = models.TextField(help_text="Student's explanation, mitigation, or evidence contesting the decision")
    supporting_document = models.FileField(upload_to='discipline_evidence/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    admin_response = models.TextField(blank=True, help_text="Official findings and response to the student's appeal")
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_appeals')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Appeal for {self.record} by {self.student.full_name} ({self.get_status_display()})"
