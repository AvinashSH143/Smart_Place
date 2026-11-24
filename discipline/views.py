from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.decorators import student_required
from .models import DisciplineRecord, DisciplineAppeal
from .forms import DisciplineAppealForm
from students.models import StudentProfile


@student_required
def student_discipline_view(request):
    student = get_object_or_404(StudentProfile, user=request.user)
    records = student.discipline_records.prefetch_related('appeals').order_by('-incident_date')

    has_active_debarment = student.is_debarred
    total_incidents = records.count()
    confirmed_violations = records.filter(status=DisciplineRecord.STATUS_CONFIRMED).count()
    under_review = records.filter(status__in=[DisciplineRecord.STATUS_UNDER_REVIEW, DisciplineRecord.STATUS_APPEALED]).count()

    context = {
        'student': student,
        'records': records,
        'has_active_debarment': has_active_debarment,
        'total_incidents': total_incidents,
        'confirmed_violations': confirmed_violations,
        'under_review': under_review,
    }
    return render(request, 'discipline/student_discipline.html', context)


@student_required
def submit_appeal_view(request, record_id):
    student = get_object_or_404(StudentProfile, user=request.user)
    record = get_object_or_404(DisciplineRecord, id=record_id, student=student)

    # Check if there is already a pending appeal
    existing_appeal = record.appeals.filter(status=DisciplineAppeal.STATUS_PENDING).first()
    if existing_appeal:
        messages.warning(request, "An appeal is already pending administrator review for this disciplinary record.")
        return redirect('discipline:discipline_view')

    if request.method == 'POST':
        form = DisciplineAppealForm(request.POST, request.FILES)
        if form.is_valid():
            appeal = form.save(commit=False)
            appeal.record = record
            appeal.student = student
            appeal.status = DisciplineAppeal.STATUS_PENDING
            appeal.save()

            # Mark record status as appealed
            record.status = DisciplineRecord.STATUS_APPEALED
            record.save(update_fields=['status'])

            messages.success(request, "Your formal disciplinary appeal has been submitted to the administration for review.")
            return redirect('discipline:discipline_view')
        else:
            messages.error(request, "Please check your appeal submission for errors.")
    else:
        form = DisciplineAppealForm()

    context = {
        'student': student,
        'record': record,
        'form': form,
    }
    return render(request, 'discipline/submit_appeal.html', context)
