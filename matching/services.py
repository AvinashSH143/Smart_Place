from decimal import Decimal
from students.models import StudentProfile, Skill, StudentSkill
from companies.models import PlacementDrive


def check_student_eligibility(student: StudentProfile, drive: PlacementDrive) -> dict:
    """
    Evaluates mandatory placement drive eligibility criteria.
    Eligibility is strictly independent of the matching score.
    Returns:
        {
            'is_eligible': bool,
            'criteria': list of dicts with criterion, required, actual, passed, explanation,
            'failed_reasons': list of str,
        }
    """
    criteria = []
    failed_reasons = []

    # 1. Debarment Check
    if student.is_debarred:
        explanation = f"Student is currently debarred: {student.debarred_reason or 'Active disciplinary restriction'}"
        criteria.append({
            'name': 'Disciplinary Clearance',
            'required': 'Active student in good standing (Not Debarred)',
            'actual': 'Debarred',
            'passed': False,
            'explanation': explanation,
        })
        failed_reasons.append(explanation)
    else:
        criteria.append({
            'name': 'Disciplinary Clearance',
            'required': 'Active student in good standing (Not Debarred)',
            'actual': 'Clear (No active debarment)',
            'passed': True,
            'explanation': 'Student is cleared for campus recruitment drives.',
        })

    # 2. Minimum CGPA Check
    cgpa_val = float(student.cgpa)
    min_cgpa_val = float(drive.min_cgpa)
    cgpa_passed = cgpa_val >= min_cgpa_val
    criteria.append({
        'name': 'Minimum CGPA',
        'required': f">= {min_cgpa_val:.2f}",
        'actual': f"{cgpa_val:.2f}",
        'passed': cgpa_passed,
        'explanation': 'Meets minimum CGPA cutoff.' if cgpa_passed else f'CGPA {cgpa_val:.2f} is below minimum requirement of {min_cgpa_val:.2f}.',
    })
    if not cgpa_passed:
        failed_reasons.append(f"CGPA below required cutoff ({cgpa_val:.2f} < {min_cgpa_val:.2f})")

    # 3. Allowed Branch Check
    allowed_branches = drive.get_allowed_branches_list()
    branch_passed = True
    if allowed_branches:
        branch_passed = any(student.branch.strip().lower() == b.strip().lower() for b in allowed_branches)
        criteria.append({
            'name': 'Eligible Branch / Discipline',
            'required': ', '.join(allowed_branches),
            'actual': student.branch,
            'passed': branch_passed,
            'explanation': 'Branch is eligible for this drive.' if branch_passed else f'{student.branch} is not in the allowed branch list for this drive.',
        })
        if not branch_passed:
            failed_reasons.append(f"Branch '{student.branch}' not eligible for this drive")

    # 4. Maximum Backlogs Check
    backlog_passed = student.current_backlogs <= drive.max_backlogs
    criteria.append({
        'name': 'Maximum Backlogs Allowed',
        'required': f"<= {drive.max_backlogs} active backlogs",
        'actual': f"{student.current_backlogs} active backlogs",
        'passed': backlog_passed,
        'explanation': 'Backlog count within permissible limit.' if backlog_passed else f'Exceeds allowed backlog limit ({student.current_backlogs} > {drive.max_backlogs}).',
    })
    if not backlog_passed:
        failed_reasons.append(f"Active backlogs ({student.current_backlogs}) exceed maximum allowed ({drive.max_backlogs})")

    # 5. Required Academic Score (if set > 0)
    req_acad = float(drive.required_academic_score)
    if req_acad > 0:
        student_acad = float(student.academic_score)
        acad_passed = student_acad >= req_acad
        criteria.append({
            'name': 'Minimum Academic Evaluation Score',
            'required': f">= {req_acad:.1f}/100",
            'actual': f"{student_acad:.1f}/100",
            'passed': acad_passed,
            'explanation': 'Academic evaluation score satisfies requirements.' if acad_passed else f'Academic score {student_acad:.1f} is below required threshold {req_acad:.1f}.',
        })
        if not acad_passed:
            failed_reasons.append(f"Academic score ({student_acad:.1f}) is below drive threshold ({req_acad:.1f})")

    is_eligible = len(failed_reasons) == 0

    return {
        'is_eligible': is_eligible,
        'criteria': criteria,
        'failed_reasons': failed_reasons,
    }


def calculate_placement_match(student: StudentProfile, drive: PlacementDrive) -> dict:
    """
    Calculates weighted placement match score (0-100):
      - Verified technical skills: 40%
      - Academic performance: 25%
      - Project quality: 20%
      - Other verified achievements: 15%
    Returns detailed breakdown, explanations, satisfied qualifications, and missing skills.
    """
    # 1. Technical Skills (40% Weight)
    drive_required_skills = list(drive.required_skills.all())
    student_skills_qs = StudentSkill.objects.filter(student=student).select_related('skill')
    student_skills_map = {ss.skill_id: ss for ss in student_skills_qs}

    matched_skills = []
    missing_skills = []
    skill_points_earned = 0.0

    if drive_required_skills:
        skill_unit_weight = 40.0 / len(drive_required_skills)
        for req_skill in drive_required_skills:
            if req_skill.id in student_skills_map:
                ss = student_skills_map[req_skill.id]
                # Proficiency multiplier
                prof_mult = 1.0
                if ss.proficiency == StudentSkill.PROFICIENCY_ADVANCED:
                    prof_mult = 1.0
                elif ss.proficiency == StudentSkill.PROFICIENCY_INTERMEDIATE:
                    prof_mult = 0.8
                else:  # BEGINNER
                    prof_mult = 0.5

                if ss.is_verified:
                    earned = skill_unit_weight * prof_mult
                    skill_points_earned += earned
                    matched_skills.append({
                        'name': req_skill.name,
                        'proficiency': ss.get_proficiency_display(),
                        'is_verified': True,
                        'status': 'Fully Verified',
                        'earned_weight': round(earned, 1),
                    })
                else:
                    # Partial credit for unverified declared skill (0.2 of unit weight)
                    earned = skill_unit_weight * 0.2 * prof_mult
                    skill_points_earned += earned
                    matched_skills.append({
                        'name': req_skill.name,
                        'proficiency': ss.get_proficiency_display(),
                        'is_verified': False,
                        'status': 'Pending Verification (Partial Credit)',
                        'earned_weight': round(earned, 1),
                    })
            else:
                missing_skills.append({
                    'name': req_skill.name,
                    'category': req_skill.get_category_display(),
                })
    else:
        # If no specific skills defined on drive, base on student verified skills count
        verified_count = student.skills.filter(is_verified=True).count()
        skill_points_earned = min(40.0, (verified_count / 5.0) * 40.0)
        for ss in student.skills.filter(is_verified=True)[:5]:
            matched_skills.append({
                'name': ss.skill.name,
                'proficiency': ss.get_proficiency_display(),
                'is_verified': True,
                'status': 'Verified Candidate Strength',
                'earned_weight': round(40.0 / max(1, min(5, verified_count)), 1),
            })

    skill_score = min(40.0, skill_points_earned)

    # 2. Academic Performance (25% Weight)
    acad_score_val = float(student.academic_score)
    academic_score_contrib = (min(100.0, acad_score_val) / 100.0) * 25.0

    # 3. Project Quality (20% Weight)
    approved_projects = student.submissions.filter(
        category='PROJECT',
        status='APPROVED',
        evaluation__isnull=False
    )
    if approved_projects.exists():
        project_evals = [p.evaluation.total_marks for p in approved_projects]
        avg_project_marks = sum(project_evals) / len(project_evals)
        project_score_contrib = (avg_project_marks / 100.0) * 20.0
    else:
        # If no approved projects, check pending projects for small provisional baseline or 0
        has_pending = student.submissions.filter(category='PROJECT', status='PENDING').exists()
        project_score_contrib = 5.0 if has_pending else 0.0

    # 4. Other Verified Achievements (15% Weight)
    approved_achievements = student.submissions.filter(
        category__in=['CERTIFICATE', 'ACHIEVEMENT'],
        status='APPROVED',
        evaluation__isnull=False
    )
    if approved_achievements.exists():
        achieve_evals = [a.evaluation.total_marks for a in approved_achievements]
        avg_achieve_marks = sum(achieve_evals) / len(achieve_evals)
        achievement_score_contrib = (avg_achieve_marks / 100.0) * 15.0
    else:
        has_pending_achieve = student.submissions.filter(
            category__in=['CERTIFICATE', 'ACHIEVEMENT'],
            status='PENDING'
        ).exists()
        achievement_score_contrib = 3.0 if has_pending_achieve else 0.0

    # Final Total Match Score
    total_match = round(
        skill_score + academic_score_contrib + project_score_contrib + achievement_score_contrib, 
        1
    )
    total_match = max(0.0, min(100.0, total_match))

    # Match Classification
    if total_match >= 85:
        classification = "Excellent Match"
        classification_color = "emerald"
    elif total_match >= 70:
        classification = "Strong Match"
        classification_color = "sky"
    elif total_match >= 50:
        classification = "Moderate Match"
        classification_color = "amber"
    else:
        classification = "Low Match"
        classification_color = "rose"

    # Eligibility evaluation
    eligibility = check_student_eligibility(student, drive)

    # Explanations
    why_matched = []
    if skill_score >= 25:
        why_matched.append(f"Strong alignment in technical capabilities with {len(matched_skills)} matched skill(s).")
    if academic_score_contrib >= 18:
        why_matched.append(f"High academic evaluation standing ({acad_score_val:.1f}/100) satisfies recruiter criteria.")
    if project_score_contrib >= 14:
        why_matched.append("Admin-verified project showcases practical engineering ability.")
    if achievement_score_contrib >= 10:
        why_matched.append("Verified certifications and extracurricular achievements validate domain expertise.")
    if not why_matched:
        why_matched.append("Preliminary match based on registered branch and baseline academic standing.")

    areas_for_improvement = []
    if missing_skills:
        skill_names = ", ".join([s['name'] for s in missing_skills[:3]])
        areas_for_improvement.append(f"Acquire and verify key drive skills: {skill_names}.")
    if not approved_projects.exists():
        areas_for_improvement.append("Submit and get project work evaluated by the admin to boost project quality score (up to +20%).")
    if not approved_achievements.exists():
        areas_for_improvement.append("Upload industry certificates or competitive achievements to earn remaining 15% achievement weight.")
    if acad_score_val < 70:
        areas_for_improvement.append("Enhance academic coursework performance to improve academic score multiplier.")

    return {
        'drive': drive,
        'student': student,
        'total_match': total_match,
        'classification': classification,
        'classification_color': classification_color,
        'is_eligible': eligibility['is_eligible'],
        'eligibility': eligibility,
        'breakdown': {
            'skills': {
                'weight': 40,
                'score': round(skill_score, 1),
                'matched': matched_skills,
                'missing': missing_skills,
            },
            'academic': {
                'weight': 25,
                'score': round(academic_score_contrib, 1),
                'student_score': acad_score_val,
            },
            'projects': {
                'weight': 20,
                'score': round(project_score_contrib, 1),
                'count': approved_projects.count(),
            },
            'achievements': {
                'weight': 15,
                'score': round(achievement_score_contrib, 1),
                'count': approved_achievements.count(),
            },
        },
        'why_matched': why_matched,
        'areas_for_improvement': areas_for_improvement,
    }
