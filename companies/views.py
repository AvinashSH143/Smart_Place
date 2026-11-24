from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from accounts.decorators import student_required
from .models import Company, PlacementDrive
from students.models import StudentProfile
from matching.services import calculate_placement_match, check_student_eligibility


@student_required
def drives_list(request):
    student = get_object_or_404(StudentProfile, user=request.user)
    
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', 'all')
    eligibility_filter = request.GET.get('eligibility', 'all')

    drives = PlacementDrive.objects.filter(is_published=True).select_related('company').prefetch_related('required_skills')

    if query:
        drives = drives.filter(job_title__icontains=query) | drives.filter(company__name__icontains=query) | drives.filter(job_role__icontains=query)

    if status_filter in ['ACTIVE', 'UPCOMING']:
        drives = drives.filter(status=status_filter)

    drive_matches = []
    for drive in drives:
        match_data = calculate_placement_match(student, drive)
        
        # Filter by eligibility if requested
        if eligibility_filter == 'eligible' and not match_data['is_eligible']:
            continue
        elif eligibility_filter == 'ineligible' and match_data['is_eligible']:
            continue
            
        drive_matches.append(match_data)

    # Sort: Eligible first, then descending by match score
    drive_matches.sort(key=lambda m: (m['is_eligible'], m['total_match']), reverse=True)

    context = {
        'student': student,
        'drive_matches': drive_matches,
        'query': query,
        'status_filter': status_filter,
        'eligibility_filter': eligibility_filter,
        'total_drives_count': len(drive_matches),
    }
    return render(request, 'companies/drives_list.html', context)


@student_required
def drive_detail(request, drive_id):
    student = get_object_or_404(StudentProfile, user=request.user)
    drive = get_object_or_404(
        PlacementDrive.objects.select_related('company').prefetch_related('required_skills', 'requirements'),
        id=drive_id,
        is_published=True
    )

    match_data = calculate_placement_match(student, drive)

    context = {
        'student': student,
        'drive': drive,
        'match_data': match_data,
    }
    return render(request, 'companies/drive_detail.html', context)
