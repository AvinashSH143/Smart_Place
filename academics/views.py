import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import FileResponse, Http404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from accounts.decorators import student_required
from .models import AcademicSubmission, AcademicEvaluation
from .forms import AcademicSubmissionForm
from students.models import StudentProfile


@student_required
def student_uploads(request):
    student = get_object_or_404(StudentProfile, user=request.user)
    
    if request.method == 'POST':
        form = AcademicSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = student
            submission.status = AcademicSubmission.STATUS_PENDING
            submission.save()
            messages.success(request, f"Document '{submission.title}' successfully submitted for administrator evaluation.")
            return redirect('academics:uploads')
        else:
            messages.error(request, "Failed to submit document. Please check the file format and required fields.")
    else:
        form = AcademicSubmissionForm()

    submissions = student.submissions.select_related('evaluation', 'related_skill').order_by('-created_at')

    # Summary statistics
    total_submissions = submissions.count()
    approved_count = submissions.filter(status=AcademicSubmission.STATUS_APPROVED).count()
    pending_count = submissions.filter(status=AcademicSubmission.STATUS_PENDING).count()
    needs_action_count = submissions.filter(status__in=[AcademicSubmission.STATUS_REJECTED, AcademicSubmission.STATUS_RESUBMISSION]).count()

    context = {
        'student': student,
        'form': form,
        'submissions': submissions,
        'total_submissions': total_submissions,
        'approved_count': approved_count,
        'pending_count': pending_count,
        'needs_action_count': needs_action_count,
    }
    return render(request, 'academics/uploads.html', context)


@student_required
def submission_detail(request, submission_id):
    student = get_object_or_404(StudentProfile, user=request.user)
    submission = get_object_or_404(
        AcademicSubmission.objects.select_related('student', 'related_skill', 'evaluation__evaluated_by'),
        id=submission_id,
        student=student
    )
    return render(request, 'academics/submission_detail.html', {'submission': submission})


@login_required
def secure_download(request, submission_id):
    """
    Secure document download view.
    Ensures that only the document owner (student) or an authorized platform administrator can download.
    """
    submission = get_object_or_404(AcademicSubmission, id=submission_id)

    user = request.user
    is_admin = getattr(user, 'profile', None) and user.profile.is_admin or user.is_superuser
    is_owner = hasattr(user, 'student_profile') and submission.student == user.student_profile

    if not (is_admin or is_owner):
        raise PermissionDenied("You do not have authorization to view or download this document.")

    if not submission.file or not os.path.exists(submission.file.path):
        raise Http404("Requested file does not exist on the storage volume.")

    try:
        response = FileResponse(open(submission.file.path, 'rb'))
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(submission.file.name)}"'
        return response
    except FileNotFoundError:
        raise Http404("Requested file does not exist on the storage volume.")
