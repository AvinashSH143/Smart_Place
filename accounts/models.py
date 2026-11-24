from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class UserProfile(models.Model):
    ROLE_ADMIN = 'ADMIN'
    ROLE_STUDENT = 'STUDENT'
    
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Administrator'),
        (ROLE_STUDENT, 'Student'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def clean(self):
        super().clean()
        if self.role == self.ROLE_ADMIN:
            existing_admin = UserProfile.objects.filter(role=self.ROLE_ADMIN)
            if self.pk:
                existing_admin = existing_admin.exclude(pk=self.pk)
            if existing_admin.exists():
                raise ValidationError("Only one authorized administrator account is permitted in the system.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_student(self):
        return self.role == self.ROLE_STUDENT

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
