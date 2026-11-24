from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Skill(models.Model):
    CATEGORY_TECHNICAL = 'TECHNICAL'
    CATEGORY_COMMUNICATION = 'COMMUNICATION'
    CATEGORY_PRACTICAL = 'PRACTICAL'
    CATEGORY_GENERAL = 'GENERAL'

    CATEGORY_CHOICES = [
        (CATEGORY_TECHNICAL, 'Technical Skills'),
        (CATEGORY_COMMUNICATION, 'Communication'),
        (CATEGORY_PRACTICAL, 'Practical Knowledge'),
        (CATEGORY_GENERAL, 'General & Domain'),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default=CATEGORY_TECHNICAL)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class StudentProfile(models.Model):
    BRANCH_CSE = 'Computer Science & Engineering'
    BRANCH_IT = 'Information Technology'
    BRANCH_ECE = 'Electronics & Communication'
    BRANCH_EEE = 'Electrical & Electronics'
    BRANCH_MECH = 'Mechanical Engineering'
    BRANCH_CIVIL = 'Civil Engineering'
    BRANCH_AIML = 'AI & Machine Learning'
    BRANCH_DS = 'Data Science'

    BRANCH_CHOICES = [
        (BRANCH_CSE, 'Computer Science & Engineering'),
        (BRANCH_IT, 'Information Technology'),
        (BRANCH_AIML, 'AI & Machine Learning'),
        (BRANCH_DS, 'Data Science'),
        (BRANCH_ECE, 'Electronics & Communication'),
        (BRANCH_EEE, 'Electrical & Electronics'),
        (BRANCH_MECH, 'Mechanical Engineering'),
        (BRANCH_CIVIL, 'Civil Engineering'),
    ]

    YEAR_CHOICES = [
        (1, '1st Year'),
        (2, '2nd Year'),
        (3, '3rd Year'),
        (4, '4th Year (Final Year)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    branch = models.CharField(max_length=100, choices=BRANCH_CHOICES)
    year_of_study = models.PositiveSmallIntegerField(choices=YEAR_CHOICES, default=3)
    cgpa = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    current_backlogs = models.PositiveSmallIntegerField(default=0)
    contact_phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.FileField(upload_to='profile_pics/', blank=True, null=True)

    # Disciplinary and debarment flags
    is_debarred = models.BooleanField(default=False)
    debarred_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.branch} - Yr {self.year_of_study})"

    @property
    def initials(self):
        parts = self.full_name.strip().split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        elif parts:
            return parts[0][:2].upper()
        return "ST"

    @property
    def academic_score(self):
        """
        Calculates the student's overall academic score (0-100) based on approved evaluated submissions.
        Returns float rounded to 1 decimal place.
        """
        approved_evals = [
            sub.evaluation.total_marks 
            for sub in self.submissions.filter(status='APPROVED') 
            if hasattr(sub, 'evaluation') and sub.evaluation is not None
        ]
        if approved_evals:
            return round(sum(approved_evals) / len(approved_evals), 1)
        # If no submissions yet, base on normalized CGPA as fallback baseline
        return round(float(self.cgpa) * 10, 1)

    @property
    def verified_skills_count(self):
        return self.skills.filter(is_verified=True).count()

    @property
    def profile_completion_percentage(self):
        score = 0
        total = 8
        if self.full_name: score += 1
        if self.email: score += 1
        if self.branch: score += 1
        if self.year_of_study: score += 1
        if self.cgpa > 0: score += 1
        if self.contact_phone: score += 1
        if self.bio: score += 1
        if self.skills.exists(): score += 1
        return int((score / total) * 100)


class StudentSkill(models.Model):
    PROFICIENCY_BEGINNER = 'BEGINNER'
    PROFICIENCY_INTERMEDIATE = 'INTERMEDIATE'
    PROFICIENCY_ADVANCED = 'ADVANCED'

    PROFICIENCY_CHOICES = [
        (PROFICIENCY_BEGINNER, 'Beginner (Basic understanding)'),
        (PROFICIENCY_INTERMEDIATE, 'Intermediate (Project experience)'),
        (PROFICIENCY_ADVANCED, 'Advanced (Production/Specialist)'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='student_skills')
    proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default=PROFICIENCY_INTERMEDIATE)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_skills')
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'skill')
        ordering = ['-is_verified', 'skill__name']

    def __str__(self):
        status = "Verified" if self.is_verified else "Pending"
        return f"{self.student.full_name} - {self.skill.name} ({self.proficiency}, {status})"
