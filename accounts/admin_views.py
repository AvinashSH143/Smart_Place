import json
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Q
from accounts.decorators import admin_required
from students.models import StudentProfile, StudentSkill, Skill
from companies.models import Company, PlacementDrive
from academics.models import AcademicSubmission, AcademicEvaluation
from discipline.models import DisciplineRecord, DisciplineAppeal
from matching.services import calculate_placement_match
from analysis.services import calculate_student_strength_analysis
from .admin_forms import (
    AcademicEvaluationForm,
    CompanyForm,
    PlacementDriveForm,
    DisciplineRecordForm,
    DebarmentForm,
    AppealReviewForm,
)


@admin_required
def admin_dashboard_home(request):
    total_students = StudentProfile.objects.count()
    total_companies = Company.objects.count()
    active_drives = PlacementDrive.objects.filter(status='ACTIVE', is_published=True).count()
    pending_evaluations = AcademicSubmission.objects.filter(status=AcademicSubmission.STATUS_PENDING).count()
    debarred_students = StudentProfile.objects.filter(is_debarred=True).count()

    # Chart 1: Student Academic Performance Distribution
    # Bands: 0-40, 41-60, 61-80, 81-100
    all_students = list(StudentProfile.objects.all())
    perf_bands = {'0-40': 0, '41-60': 0, '61-80': 0, '81-100': 0}
    for s in all_students:
        score = s.academic_score
        if score <= 40:
            perf_bands['0-40'] += 1
        elif score <= 60:
            perf_bands['41-60'] += 1
        elif score <= 80:
            perf_bands['61-80'] += 1
        else:
            perf_bands['81-100'] += 1

    chart1_labels = list(perf_bands.keys())
    chart1_data = list(perf_bands.values())

    # Chart 2: Placement Matching Distribution
    # Sample active drives and all students to find match distribution
    matching_distribution = {
        'Excellent Match (85-100)': 0,
        'Strong Match (70-84)': 0,
        'Moderate Match (50-69)': 0,
        'Low Match (<50)': 0,
    }
    sample_drives = list(PlacementDrive.objects.filter(is_published=True)[:5])
    if sample_drives and all_students:
        for drive in sample_drives:
            for s in all_students:
                res = calculate_placement_match(s, drive)
                score = res['total_match']
                if score >= 85:
                    matching_distribution['Excellent Match (85-100)'] += 1
                elif score >= 70:
                    matching_distribution['Strong Match (70-84)'] += 1
                elif score >= 50:
                    matching_distribution['Moderate Match (50-69)'] += 1
                else:
                    matching_distribution['Low Match (<50)'] += 1

    chart2_labels = list(matching_distribution.keys())
    chart2_data = list(matching_distribution.values())

    # Recent lists
    recent_registrations = StudentProfile.objects.order_by('-created_at')[:5]
    pending_submissions = AcademicSubmission.objects.filter(
        status=AcademicSubmission.STATUS_PENDING
    ).select_related('student', 'related_skill').order_by('-created_at')[:5]
    recent_drives = PlacementDrive.objects.select_related('company').order_by('-created_at')[:5]

    context = {
        'total_students': total_students,
        'total_companies': total_companies,
        'active_drives': active_drives,
        'pending_evaluations': pending_evaluations,
        'debarred_students': debarred_students,
        'chart1_labels_json': json.dumps(chart1_labels),
        'chart1_data_json': json.dumps(chart1_data),
        'chart2_labels_json': json.dumps(chart2_labels),
        'chart2_data_json': json.dumps(chart2_data),
        'recent_registrations': recent_registrations,
        'pending_submissions': pending_submissions,
        'recent_drives': recent_drives,
    }
    return render(request, 'admin_dashboard/dashboard.html', context)


@admin_required
def admin_students_list(request):
    search_query = request.GET.get('q', '').strip()
    branch_filter = request.GET.get('branch', '')
    status_filter = request.GET.get('status', '')

    students = StudentProfile.objects.all().order_by('full_name')

    if search_query:
        students = students.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )

    if branch_filter:
        students = students.filter(branch=branch_filter)

    if status_filter == 'debarred':
        students = students.filter(is_debarred=True)
    elif status_filter == 'active':
        students = students.filter(is_debarred=False)

    context = {
        'students': students,
        'search_query': search_query,
        'branch_filter': branch_filter,
        'status_filter': status_filter,
        'branch_choices': StudentProfile.BRANCH_CHOICES,
    }
    return render(request, 'admin_dashboard/students_list.html', context)


@admin_required
def admin_student_detail(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    strength_analysis = calculate_student_strength_analysis(student)

    # Submissions
    submissions = student.submissions.select_related('evaluation', 'related_skill').order_by('-created_at')

    # Placement matches across all published drives
    drives = PlacementDrive.objects.filter(is_published=True).select_related('company').prefetch_related('required_skills')
    matches = [calculate_placement_match(student, drive) for drive in drives]
    matches.sort(key=lambda m: (m['is_eligible'], m['total_match']), reverse=True)

    # Disciplinary history
    discipline_records = student.discipline_records.prefetch_related('appeals').order_by('-incident_date')

    # Skills
    student_skills = student.skills.select_related('skill').order_by('-is_verified', 'skill__name')

    context = {
        'student': student,
        'strength_analysis': strength_analysis,
        'submissions': submissions,
        'matches': matches,
        'discipline_records': discipline_records,
        'student_skills': student_skills,
        'radar_labels_json': json.dumps(strength_analysis['radar_labels']),
        'radar_data_json': json.dumps(strength_analysis['radar_data']),
    }
    return render(request, 'admin_dashboard/student_detail.html', context)


@admin_required
def admin_evaluations_list(request):
    status_filter = request.GET.get('status', 'PENDING')
    category_filter = request.GET.get('category', '')

    submissions = AcademicSubmission.objects.select_related('student', 'related_skill', 'evaluation').order_by('-created_at')

    if status_filter != 'ALL':
        submissions = submissions.filter(status=status_filter)

    if category_filter:
        submissions = submissions.filter(category=category_filter)

    counts = {
        'PENDING': AcademicSubmission.objects.filter(status=AcademicSubmission.STATUS_PENDING).count(),
        'APPROVED': AcademicSubmission.objects.filter(status=AcademicSubmission.STATUS_APPROVED).count(),
        'REJECTED': AcademicSubmission.objects.filter(status=AcademicSubmission.STATUS_REJECTED).count(),
        'RESUBMISSION': AcademicSubmission.objects.filter(status=AcademicSubmission.STATUS_RESUBMISSION).count(),
        'ALL': AcademicSubmission.objects.count(),
    }

    context = {
        'submissions': submissions,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'counts': counts,
    }
    return render(request, 'admin_dashboard/evaluations_list.html', context)


@admin_required
def admin_evaluate_submission(request, submission_id):
    submission = get_object_or_404(
        AcademicSubmission.objects.select_related('student', 'related_skill'),
        id=submission_id
    )

    evaluation = getattr(submission, 'evaluation', None)

    if request.method == 'POST':
        form = AcademicEvaluationForm(request.POST, instance=evaluation)
        if form.is_valid():
            with transaction.atomic():
                eval_obj = form.save(commit=False)
                eval_obj.submission = submission
                eval_obj.evaluated_by = request.user
                eval_obj.save()

                new_status = form.cleaned_data['status']
                submission.status = new_status
                submission.save(update_fields=['status', 'updated_at'])

                # Skill verification auto-sync
                if (new_status == AcademicSubmission.STATUS_APPROVED and 
                    submission.related_skill and 
                    form.cleaned_data.get('verify_related_skill')):
                    student_skill, created = StudentSkill.objects.get_or_create(
                        student=submission.student,
                        skill=submission.related_skill,
                        defaults={
                            'proficiency': StudentSkill.PROFICIENCY_INTERMEDIATE,
                            'is_verified': True,
                            'verified_by': request.user,
                            'verified_at': timezone.now(),
                        }
                    )
                    if not created and not student_skill.is_verified:
                        student_skill.is_verified = True
                        student_skill.verified_by = request.user
                        student_skill.verified_at = timezone.now()
                        student_skill.save()

            messages.success(request, f"Submission evaluated successfully. Total marks awarded: {eval_obj.total_marks}/100 ({submission.get_status_display()}).")
            return redirect('admin_dashboard:evaluations_list')
        else:
            messages.error(request, "Please check the rubric marks and form inputs.")
    else:
        initial_data = {}
        if not evaluation:
            initial_data['status'] = AcademicSubmission.STATUS_APPROVED
        else:
            initial_data['status'] = submission.status
        form = AcademicEvaluationForm(instance=evaluation, initial=initial_data)

    context = {
        'submission': submission,
        'evaluation': evaluation,
        'form': form,
    }
    return render(request, 'admin_dashboard/evaluate_submission.html', context)


@admin_required
def admin_companies_list(request):
    companies = Company.objects.annotate(drives_count=Count('drives')).order_by('name')
    return render(request, 'admin_dashboard/companies_list.html', {'companies': companies})


@admin_required
def admin_company_create(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save()
            messages.success(request, f"Company '{company.name}' successfully added.")
            return redirect('admin_dashboard:companies_list')
    else:
        form = CompanyForm()
    return render(request, 'admin_dashboard/company_form.html', {'form': form, 'title': 'Register New Company'})


@admin_required
def admin_company_edit(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, f"Company '{company.name}' updated successfully.")
            return redirect('admin_dashboard:companies_list')
    else:
        form = CompanyForm(instance=company)
    return render(request, 'admin_dashboard/company_form.html', {'form': form, 'company': company, 'title': f'Edit {company.name}'})


@admin_required
def admin_drives_list(request):
    drives = PlacementDrive.objects.select_related('company').prefetch_related('required_skills').order_by('-drive_date')
    return render(request, 'admin_dashboard/drives_list.html', {'drives': drives})


@admin_required
def admin_drive_create(request):
    if request.method == 'POST':
        form = PlacementDriveForm(request.POST)
        if form.is_valid():
            drive = form.save()
            messages.success(request, f"Placement drive '{drive.job_title}' for {drive.company.name} successfully created.")
            return redirect('admin_dashboard:drives_list')
    else:
        form = PlacementDriveForm()
    return render(request, 'admin_dashboard/drive_form.html', {'form': form, 'title': 'Create New Placement Drive'})


@admin_required
def admin_drive_edit(request, drive_id):
    drive = get_object_or_404(PlacementDrive, id=drive_id)
    if request.method == 'POST':
        form = PlacementDriveForm(request.POST, instance=drive)
        if form.is_valid():
            form.save()
            messages.success(request, f"Drive '{drive.job_title}' updated successfully.")
            return redirect('admin_dashboard:drives_list')
    else:
        form = PlacementDriveForm(instance=drive)
    return render(request, 'admin_dashboard/drive_form.html', {'form': form, 'drive': drive, 'title': f'Edit Drive - {drive.job_title}'})


@admin_required
def admin_drive_toggle_status(request, drive_id):
    drive = get_object_or_404(PlacementDrive, id=drive_id)
    if drive.status == PlacementDrive.STATUS_ACTIVE:
        drive.status = PlacementDrive.STATUS_CLOSED
    else:
        drive.status = PlacementDrive.STATUS_ACTIVE
    drive.save(update_fields=['status'])
    messages.info(request, f"Drive status updated to '{drive.get_status_display()}'.")
    return redirect('admin_dashboard:drives_list')


@admin_required
def admin_drive_delete(request, drive_id):
    drive = get_object_or_404(PlacementDrive, id=drive_id)
    if request.method == 'POST':
        job_title = drive.job_title
        company_name = drive.company.name
        drive.delete()
        messages.success(request, f"Drive '{job_title}' ({company_name}) has been deleted.")
        return redirect('admin_dashboard:drives_list')
    return render(request, 'admin_dashboard/confirm_delete.html', {
        'object_name': f"Placement Drive: {drive.job_title} at {drive.company.name}",
        'cancel_url': reverse('admin_dashboard:drives_list'),
    })


@admin_required
def admin_discipline_list(request):
    status_filter = request.GET.get('status', 'ALL')
    records = DisciplineRecord.objects.select_related('student', 'recorded_by').prefetch_related('appeals').order_by('-incident_date')

    if status_filter != 'ALL':
        records = records.filter(status=status_filter)

    counts = {
        'ALL': DisciplineRecord.objects.count(),
        'UNDER_REVIEW': DisciplineRecord.objects.filter(status=DisciplineRecord.STATUS_UNDER_REVIEW).count(),
        'CONFIRMED': DisciplineRecord.objects.filter(status=DisciplineRecord.STATUS_CONFIRMED).count(),
        'APPEALED': DisciplineRecord.objects.filter(status=DisciplineRecord.STATUS_APPEALED).count(),
        'DISMISSED': DisciplineRecord.objects.filter(status=DisciplineRecord.STATUS_DISMISSED).count(),
    }

    pending_appeals = DisciplineAppeal.objects.filter(status=DisciplineAppeal.STATUS_PENDING).select_related('record', 'student')

    context = {
        'records': records,
        'status_filter': status_filter,
        'counts': counts,
        'pending_appeals': pending_appeals,
    }
    return render(request, 'admin_dashboard/discipline_list.html', context)


@admin_required
def admin_discipline_create(request):
    if request.method == 'POST':
        form = DisciplineRecordForm(request.POST, request.FILES)
        if form.is_valid():
            record = form.save(commit=False)
            record.recorded_by = request.user
            record.save()
            messages.success(request, f"Disciplinary incident for student '{record.student.full_name}' has been documented.")
            return redirect('admin_dashboard:discipline_list')
    else:
        form = DisciplineRecordForm()
    return render(request, 'admin_dashboard/discipline_form.html', {'form': form, 'title': 'Document Disciplinary Incident'})


@admin_required
def admin_discipline_update_status(request, record_id, new_status):
    record = get_object_or_404(DisciplineRecord, id=record_id)
    valid_statuses = [DisciplineRecord.STATUS_CONFIRMED, DisciplineRecord.STATUS_DISMISSED]
    if new_status in valid_statuses:
        record.status = new_status
        record.save()
        messages.info(request, f"Incident status changed to {record.get_status_display()}.")
    else:
        messages.error(request, f"Invalid status value: {new_status}")
    return redirect('admin_dashboard:discipline_list')


@admin_required
def admin_debar_student(request, record_id):
    record = get_object_or_404(DisciplineRecord.objects.select_related('student'), id=record_id)
    student = record.student

    if request.method == 'POST':
        form = DebarmentForm(request.POST)
        if form.is_valid():
            record.is_debarred = form.cleaned_data['is_debarred']
            record.debarment_start = form.cleaned_data['debarment_start']
            record.debarment_end = form.cleaned_data['debarment_end']
            record.placement_restrictions = form.cleaned_data['placement_restrictions']
            record.admin_decision_notes = form.cleaned_data['admin_decision_notes']
            record.status = DisciplineRecord.STATUS_CONFIRMED
            record.save()

            messages.warning(request, f"Debarment decision enforced for '{student.full_name}'. Placement restrictions are now active.")
            return redirect('admin_dashboard:discipline_list')
    else:
        initial = {
            'is_debarred': True,
            'debarment_start': record.debarment_start or timezone.now().date(),
            'debarment_end': record.debarment_end,
            'placement_restrictions': record.placement_restrictions or "Debarred from campus placement drives.",
            'admin_decision_notes': record.admin_decision_notes,
        }
        form = DebarmentForm(initial=initial)

    return render(request, 'admin_dashboard/debar_form.html', {
        'form': form,
        'record': record,
        'student': student,
    })


@admin_required
def admin_reinstate_student(request, record_id):
    record = get_object_or_404(DisciplineRecord.objects.select_related('student'), id=record_id)
    student = record.student

    if request.method == 'POST':
        notes = request.POST.get('reinstatement_notes', '').strip()
        record.is_debarred = False
        record.admin_decision_notes = f"{record.admin_decision_notes}\n[Reinstated on {timezone.now().strftime('%Y-%m-%d')}]: {notes}".strip()
        record.save()

        # Update student profile
        student.is_debarred = False
        student.debarred_reason = ""
        student.save(update_fields=['is_debarred', 'debarred_reason'])

        messages.success(request, f"Student '{student.full_name}' has been officially reinstated and cleared for placements.")
        return redirect('admin_dashboard:discipline_list')

    return render(request, 'admin_dashboard/reinstate_confirm.html', {
        'record': record,
        'student': student,
    })


@admin_required
def admin_appeal_review(request, appeal_id):
    appeal = get_object_or_404(
        DisciplineAppeal.objects.select_related('record', 'student'),
        id=appeal_id
    )

    if request.method == 'POST':
        form = AppealReviewForm(request.POST)
        if form.is_valid():
            decision = form.cleaned_data['decision']
            admin_response = form.cleaned_data['admin_response']

            appeal.admin_response = admin_response
            appeal.reviewed_by = request.user
            appeal.reviewed_at = timezone.now()

            record = appeal.record
            student = appeal.student

            if decision == AppealReviewForm.DECISION_APPROVE:
                appeal.status = DisciplineAppeal.STATUS_APPROVED
                appeal.save()

                # Reinstate student and dismiss violation
                record.is_debarred = False
                record.status = DisciplineRecord.STATUS_DISMISSED
                record.admin_decision_notes = f"{record.admin_decision_notes}\n[Appeal Upheld]: {admin_response}".strip()
                record.save()

                student.is_debarred = False
                student.debarred_reason = ""
                student.save(update_fields=['is_debarred', 'debarred_reason'])

                messages.success(request, f"Appeal approved. Student '{student.full_name}' has been reinstated.")
            else:
                appeal.status = DisciplineAppeal.STATUS_REJECTED
                appeal.save()

                record.status = DisciplineRecord.STATUS_CONFIRMED
                record.admin_decision_notes = f"{record.admin_decision_notes}\n[Appeal Rejected]: {admin_response}".strip()
                record.save()

                messages.info(request, f"Appeal for '{student.full_name}' rejected. Disciplinary penalty maintained.")

            return redirect('admin_dashboard:discipline_list')
    else:
        form = AppealReviewForm()

    return render(request, 'admin_dashboard/appeal_review.html', {
        'appeal': appeal,
        'form': form,
    })

@admin_required
def admin_discipline_delete(request, record_id):
    """Delete a DisciplineRecord after confirmation.
    GET renders a confirmation page; POST performs deletion.
    Also recalculates student's debarment status after deletion.
    """
    record = get_object_or_404(DisciplineRecord, id=record_id)
    if request.method == 'POST':
        student = record.student
        student_name = student.full_name
        record.delete()

        # Recalculate student's debarment status after record deletion
        # Check if any remaining confirmed records still mark this student as debarred
        active_debarment = DisciplineRecord.objects.filter(
            student=student,
            is_debarred=True,
            status=DisciplineRecord.STATUS_CONFIRMED
        ).exists()
        student.is_debarred = active_debarment
        if not active_debarment:
            student.debarred_reason = ""
        student.save(update_fields=['is_debarred', 'debarred_reason'])

        messages.success(request, f"Disciplinary record for student '{student_name}' has been removed.")
        if not active_debarment:
            messages.info(request, f"Student '{student_name}' is now cleared for placement opportunities.")
        return redirect('admin_dashboard:discipline_list')
    # Render confirmation template
    return render(request, 'admin_dashboard/confirm_delete.html', {
        'object': record,
        'object_name': 'Disciplinary Record',
        'cancel_url': reverse('admin_dashboard:discipline_list'),
    })
