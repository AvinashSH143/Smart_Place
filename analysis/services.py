from decimal import Decimal
from students.models import StudentProfile, StudentSkill, Skill
from academics.models import AcademicSubmission, AcademicEvaluation


def calculate_student_strength_analysis(student: StudentProfile) -> dict:
    """
    Computes 5-dimension competency analysis:
      1. Technical Skills (Weight: 30%)
      2. Academic Performance (Weight: 25%)
      3. Project Quality (Weight: 20%)
      4. Communication (Weight: 15%)
      5. Practical Knowledge (Weight: 10%)
    
    Returns scores (0-100 or None if unassessed), radar chart labels & data,
    overall calculated strength, provisional status, and actionable insights.
    """
    weights = {
        'technical': 0.30,
        'academic': 0.25,
        'projects': 0.20,
        'communication': 0.15,
        'practical': 0.10,
    }

    # 1. Technical Skills Dimension
    tech_skills = student.skills.filter(
        skill__category=Skill.CATEGORY_TECHNICAL,
        is_verified=True
    )
    tech_submissions = student.submissions.filter(
        category=AcademicSubmission.CATEGORY_SKILL,
        status=AcademicSubmission.STATUS_APPROVED,
        evaluation__isnull=False
    )
    
    tech_score = None
    if tech_skills.exists() or tech_submissions.exists():
        tech_components = []
        if tech_skills.exists():
            prof_values = {
                StudentSkill.PROFICIENCY_ADVANCED: 95.0,
                StudentSkill.PROFICIENCY_INTERMEDIATE: 75.0,
                StudentSkill.PROFICIENCY_BEGINNER: 50.0,
            }
            skills_avg = sum(prof_values.get(s.proficiency, 60.0) for s in tech_skills) / tech_skills.count()
            tech_components.append(skills_avg)
        if tech_submissions.exists():
            sub_avg = sum(s.evaluation.total_marks for s in tech_submissions) / tech_submissions.count()
            tech_components.append(sub_avg)
        tech_score = round(sum(tech_components) / len(tech_components), 1)

    # 2. Academic Performance Dimension
    cgpa_val = float(student.cgpa)
    cert_submissions = student.submissions.filter(
        category=AcademicSubmission.CATEGORY_CERTIFICATE,
        status=AcademicSubmission.STATUS_APPROVED,
        evaluation__isnull=False
    )
    acad_score = None
    if cgpa_val > 0 or cert_submissions.exists():
        cgpa_normalized = min(100.0, cgpa_val * 10.0)
        if cert_submissions.exists():
            cert_avg = sum(s.evaluation.total_marks for s in cert_submissions) / cert_submissions.count()
            acad_score = round((0.6 * cgpa_normalized) + (0.4 * cert_avg), 1)
        else:
            acad_score = round(cgpa_normalized, 1)

    # 3. Project Quality Dimension
    project_submissions = student.submissions.filter(
        category=AcademicSubmission.CATEGORY_PROJECT,
        status=AcademicSubmission.STATUS_APPROVED,
        evaluation__isnull=False
    )
    project_score = None
    if project_submissions.exists():
        proj_avg = sum(s.evaluation.total_marks for s in project_submissions) / project_submissions.count()
        project_score = round(proj_avg, 1)

    # 4. Communication Dimension
    comm_skills = student.skills.filter(
        skill__category=Skill.CATEGORY_COMMUNICATION,
        is_verified=True
    )
    all_approved_evals = AcademicEvaluation.objects.filter(
        submission__student=student,
        submission__status=AcademicSubmission.STATUS_APPROVED
    )
    comm_score = None
    comm_components = []
    if comm_skills.exists():
        comm_prof_values = {
            StudentSkill.PROFICIENCY_ADVANCED: 95.0,
            StudentSkill.PROFICIENCY_INTERMEDIATE: 78.0,
            StudentSkill.PROFICIENCY_BEGINNER: 55.0,
        }
        comm_skills_avg = sum(comm_prof_values.get(s.proficiency, 65.0) for s in comm_skills) / comm_skills.count()
        comm_components.append(comm_skills_avg)
    if all_approved_evals.exists():
        # Presentation & originality marks max 25 -> scale to 100
        orig_avg = (sum(e.marks_originality for e in all_approved_evals) / all_approved_evals.count()) / 25.0 * 100.0
        comm_components.append(orig_avg)
    if comm_components:
        comm_score = round(sum(comm_components) / len(comm_components), 1)

    # 5. Practical Knowledge Dimension
    practical_score = None
    if all_approved_evals.exists():
        # Practical application marks max 25 -> scale to 100
        prac_avg = (sum(e.marks_practical for e in all_approved_evals) / all_approved_evals.count()) / 25.0 * 100.0
        practical_score = round(prac_avg, 1)
    elif student.skills.filter(skill__category=Skill.CATEGORY_PRACTICAL, is_verified=True).exists():
        prac_skills = student.skills.filter(skill__category=Skill.CATEGORY_PRACTICAL, is_verified=True)
        practical_score = round(sum(75.0 for _ in prac_skills) / prac_skills.count(), 1)

    dimensions = [
        {
            'key': 'technical',
            'name': 'Technical Skills',
            'score': tech_score,
            'weight': weights['technical'],
            'weight_pct': 30,
            'description': 'Proficiency across verified programming languages, frameworks, and verified technical submissions.',
            'status': 'Assessed' if tech_score is not None else 'Not assessed',
        },
        {
            'key': 'academic',
            'name': 'Academic Performance',
            'score': acad_score,
            'weight': weights['academic'],
            'weight_pct': 25,
            'description': 'Cumulative university GPA combined with evaluated academic certifications.',
            'status': 'Assessed' if acad_score is not None else 'Not assessed',
        },
        {
            'key': 'projects',
            'name': 'Project Quality',
            'score': project_score,
            'weight': weights['projects'],
            'weight_pct': 20,
            'description': 'Marks awarded by admin evaluation for architectural design, code quality, and implementation depth.',
            'status': 'Assessed' if project_score is not None else 'Not assessed',
        },
        {
            'key': 'communication',
            'name': 'Communication',
            'score': comm_score,
            'weight': weights['communication'],
            'weight_pct': 15,
            'description': 'Presentation quality, clarity of technical documentation, and verified interpersonal skills.',
            'status': 'Assessed' if comm_score is not None else 'Not assessed',
        },
        {
            'key': 'practical',
            'name': 'Practical Knowledge',
            'score': practical_score,
            'weight': weights['practical'],
            'weight_pct': 10,
            'description': 'Demonstrated real-world problem solving, deployment capabilities, and practical application score.',
            'status': 'Assessed' if practical_score is not None else 'Not assessed',
        },
    ]

    assessed_dimensions = [d for d in dimensions if d['score'] is not None]
    unassessed_dimensions = [d for d in dimensions if d['score'] is None]

    if assessed_dimensions:
        total_assessed_weight = sum(d['weight'] for d in assessed_dimensions)
        weighted_sum = sum(d['score'] * d['weight'] for d in assessed_dimensions)
        overall_strength = round(weighted_sum / total_assessed_weight, 1)
        is_provisional = len(assessed_dimensions) < len(dimensions)
    else:
        overall_strength = 0.0
        is_provisional = True

    # Identify strongest and weakest
    strongest_dim = None
    weakest_dim = None
    if assessed_dimensions:
        sorted_by_score = sorted(assessed_dimensions, key=lambda x: x['score'], reverse=True)
        strongest_dim = sorted_by_score[0]
        weakest_dim = sorted_by_score[-1]

    # Actionable insights & next steps
    skills_needing_improvement = []
    unverified_skills = student.skills.filter(is_verified=False)
    if unverified_skills.exists():
        skills_needing_improvement = [us.skill.name for us in unverified_skills[:3]]

    recommendations = []
    if project_score is None:
        recommendations.append("Upload a capstone project submission for admin review to establish your Project Quality rating.")
    elif project_score < 70:
        recommendations.append("Enhance project implementation by adding comprehensive unit tests, documentation, and live deployments.")

    if tech_score is None:
        recommendations.append("Submit technical skill certifications to verify your core developer capabilities.")
    elif tech_score < 75:
        recommendations.append("Strengthen advanced data structures, system design, or domain-specific framework proficiencies.")

    if unassessed_dimensions:
        names = ", ".join([d['name'] for d in unassessed_dimensions])
        recommendations.append(f"Complete submissions for unassessed areas: {names} to convert your provisional score into a verified composite score.")

    if not recommendations:
        recommendations.append("Your profile is comprehensively assessed and competitive for upcoming placement drives!")

    # Chart data structure for Chart.js
    # Chart.js radar chart requires 0-100 values; for unassessed we can show 0 with a label or null
    radar_labels = [d['name'] for d in dimensions]
    radar_data = [(d['score'] if d['score'] is not None else 0) for d in dimensions]

    return {
        'dimensions': dimensions,
        'assessed_count': len(assessed_dimensions),
        'total_count': len(dimensions),
        'overall_strength': overall_strength,
        'is_provisional': is_provisional,
        'strongest_dimension': strongest_dim,
        'weakest_dimension': weakest_dim,
        'skills_needing_improvement': skills_needing_improvement,
        'recommendations': recommendations,
        'radar_labels': radar_labels,
        'radar_data': radar_data,
    }
