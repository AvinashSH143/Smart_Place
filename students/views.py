import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.decorators import student_required
from .models import StudentProfile, StudentSkill, Skill
from .forms import StudentProfileForm, AddStudentSkillForm
from companies.models import PlacementDrive
from matching.services import calculate_placement_match
from analysis.services import calculate_student_strength_analysis
from academics.models import AcademicSubmission


@student_required
def student_dashboard(request):
    student = get_object_or_404(StudentProfile, user=request.user)

    # Calculate 5-dimension competency analysis
    strength_analysis = calculate_student_strength_analysis(student)

    # Compute matches for all active & published drives
    drives = PlacementDrive.objects.filter(is_published=True).select_related('company').prefetch_related('required_skills')
    
    matches = []
    for drive in drives:
        match_data = calculate_placement_match(student, drive)
        matches.append(match_data)

    # Sort matches by total match score descending
    matches.sort(key=lambda m: (m['is_eligible'], m['total_match']), reverse=True)

    # Top 3 recommended drives
    top_matches = matches[:3]

    # Satisfactory placement matches count (e.g., score >= 50%)
    satisfactory_matches_count = sum(1 for m in matches if m['total_match'] >= 50 and m['is_eligible'])

    # Recent Activity items
    recent_submissions = student.submissions.select_related('evaluation').order_by('-updated_at')[:4]
    recent_skills = student.skills.select_related('skill').order_by('-created_at')[:3]
    recent_drives = PlacementDrive.objects.filter(is_published=True).order_by('-created_at')[:3]

    context = {
        'student': student,
        'strength_analysis': strength_analysis,
        'top_matches': top_matches,
        'satisfactory_matches_count': satisfactory_matches_count,
        'recent_submissions': recent_submissions,
        'recent_skills': recent_skills,
        'recent_drives': recent_drives,
        'radar_labels_json': json.dumps(strength_analysis['radar_labels']),
        'radar_data_json': json.dumps(strength_analysis['radar_data']),
    }
    return render(request, 'students/dashboard.html', context)


@student_required
def student_profile(request):
    student = get_object_or_404(StudentProfile, user=request.user)
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile information has been successfully updated.")
            return redirect('students:profile')
        else:
            messages.error(request, "Please check the profile form for errors.")
    else:
        form = StudentProfileForm(instance=student)

    # Analytics and breakdowns
    strength_analysis = calculate_student_strength_analysis(student)

    # Category counts
    approved_certs = student.submissions.filter(category=AcademicSubmission.CATEGORY_CERTIFICATE, status=AcademicSubmission.STATUS_APPROVED).count()
    approved_projects = student.submissions.filter(category=AcademicSubmission.CATEGORY_PROJECT, status=AcademicSubmission.STATUS_APPROVED).count()
    approved_skills = student.skills.filter(is_verified=True).count()
    pending_submissions = student.submissions.filter(status=AcademicSubmission.STATUS_PENDING).count()

    # Skill form
    skill_form = AddStudentSkillForm()
    declared_skills = student.skills.select_related('skill').order_by('-is_verified', 'skill__name')

    context = {
        'student': student,
        'form': form,
        'skill_form': skill_form,
        'declared_skills': declared_skills,
        'strength_analysis': strength_analysis,
        'approved_certs': approved_certs,
        'approved_projects': approved_projects,
        'approved_skills': approved_skills,
        'pending_submissions': pending_submissions,
        'radar_labels_json': json.dumps(strength_analysis['radar_labels']),
        'radar_data_json': json.dumps(strength_analysis['radar_data']),
    }
    return render(request, 'students/profile.html', context)


@student_required
def add_student_skill(request):
    student = get_object_or_404(StudentProfile, user=request.user)
    if request.method == 'POST':
        form = AddStudentSkillForm(request.POST)
        if form.is_valid():
            skill = form.cleaned_data['skill']
            proficiency = form.cleaned_data['proficiency']
            student_skill, created = StudentSkill.objects.get_or_create(
                student=student,
                skill=skill,
                defaults={'proficiency': proficiency}
            )
            if not created:
                student_skill.proficiency = proficiency
                student_skill.save()
                messages.info(request, f"Updated proficiency for '{skill.name}'.")
            else:
                messages.success(request, f"Skill '{skill.name}' added to your profile (Pending admin verification).")
        else:
            messages.error(request, "Could not add skill. Please verify your selection.")
    return redirect('students:profile')


@student_required
def delete_student_skill(request, skill_id):
    student = get_object_or_404(StudentProfile, user=request.user)
    student_skill = get_object_or_404(StudentSkill, id=skill_id, student=student)
    skill_name = student_skill.skill.name
    student_skill.delete()
    messages.success(request, f"Skill '{skill_name}' removed from your profile.")
    return redirect('students:profile')
