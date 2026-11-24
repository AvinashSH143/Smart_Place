import os
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.base import ContentFile
from accounts.models import UserProfile
from students.models import StudentProfile, Skill, StudentSkill
from companies.models import Company, PlacementDrive, DriveRequirement
from academics.models import AcademicSubmission, AcademicEvaluation
from discipline.models import DisciplineRecord, DisciplineAppeal
from core.models import BlogPost, ContactMessage


class Command(BaseCommand):
    help = "Seeds database with realistic initial data for testing and demonstration."

    def handle(self, *args, **options):
        self.stdout.write("Seeding platform database...")

        # 1. Admin account
        admin_profile = UserProfile.objects.filter(role=UserProfile.ROLE_ADMIN).first()
        if not admin_profile:
            admin_user = User.objects.create_superuser('admin', 'admin@placement.edu', 'AdminPass123!')
            admin_user.first_name = "Placement"
            admin_user.last_name = "Director"
            admin_user.save()
            admin_profile = UserProfile.objects.create(user=admin_user, role=UserProfile.ROLE_ADMIN)
        admin_user = admin_profile.user

        # 2. Skills
        skills_data = [
            # Technical
            ("Python", Skill.CATEGORY_TECHNICAL, "Core Python, OOP, asynchronous programming, scripting."),
            ("Django", Skill.CATEGORY_TECHNICAL, "Django 5, ORM, authentication, REST architecture, templates."),
            ("PostgreSQL", Skill.CATEGORY_TECHNICAL, "Relational schema design, indexing, transactions, optimization."),
            ("Data Structures & Algorithms", Skill.CATEGORY_TECHNICAL, "Tree, graph, dynamic programming, algorithmic complexity."),
            ("Docker", Skill.CATEGORY_TECHNICAL, "Containerization, multi-stage builds, Docker Compose."),
            ("Kubernetes", Skill.CATEGORY_TECHNICAL, "Pod lifecycle, deployments, services, ingress controllers."),
            ("AWS Cloud", Skill.CATEGORY_TECHNICAL, "EC2, S3, RDS, Lambda, IAM security configurations."),
            ("Machine Learning", Skill.CATEGORY_TECHNICAL, "Supervised learning, scikit-learn, PyTorch model training."),
            ("System Design", Skill.CATEGORY_TECHNICAL, "Microservices, load balancing, caching, high availability."),
            ("JavaScript / TypeScript", Skill.CATEGORY_TECHNICAL, "Modern ES6+, DOM manipulation, types, event loop."),
            ("React", Skill.CATEGORY_TECHNICAL, "Functional components, hooks, state management, SPA design."),
            ("REST APIs", Skill.CATEGORY_TECHNICAL, "API design, status codes, JSON serialization, security."),
            # Communication
            ("Technical Writing", Skill.CATEGORY_COMMUNICATION, "Architecture docs, API specs, pull request descriptions."),
            ("Verbal Presentation", Skill.CATEGORY_COMMUNICATION, "Executive demos, design reviews, standup updates."),
            # Practical Knowledge
            ("CI/CD Automation", Skill.CATEGORY_PRACTICAL, "GitHub Actions, automated test suites, staging deployments."),
            ("Linux Systems Administration", Skill.CATEGORY_PRACTICAL, "Shell scripting, networking, permission management."),
            # General
            ("Agile & Scrum", Skill.CATEGORY_GENERAL, "Sprint planning, backlog grooming, retrospectives."),
            ("Problem Solving", Skill.CATEGORY_GENERAL, "Analytical debugging, incident triage, root cause analysis."),
        ]

        skills_dict = {}
        for name, category, desc in skills_data:
            skill, _ = Skill.objects.get_or_create(
                name=name,
                defaults={'category': category, 'description': desc}
            )
            skills_dict[name] = skill

        # 3. Companies
        companies_data = [
            {
                'name': 'Google Cloud',
                'industry': 'Cloud Infrastructure & Enterprise AI',
                'website': 'https://cloud.google.com',
                'description': 'Google Cloud accelerates organizations ability to digitally transform through world-leading cloud infrastructure, data analytics, and generative AI.'
            },
            {
                'name': 'Stripe',
                'industry': 'Financial Technology & Global Payments',
                'website': 'https://stripe.com',
                'description': 'Stripe powers modern economic infrastructure for the internet, processing hundreds of billions in global commerce annually.'
            },
            {
                'name': 'Amazon AWS',
                'industry': 'Cloud Computing & Distributed Systems',
                'website': 'https://aws.amazon.com',
                'description': 'AWS provides on-demand cloud computing platforms and APIs to individuals, companies, and governments.'
            },
            {
                'name': 'Microsoft',
                'industry': 'Enterprise Software & Intelligent Cloud',
                'website': 'https://microsoft.com',
                'description': 'Microsoft enables digital transformation for the era of an intelligent cloud and an intelligent edge.'
            },
            {
                'name': 'Goldman Sachs',
                'industry': 'Investment Banking & Quantitative Engineering',
                'website': 'https://goldmansachs.com',
                'description': 'Global financial institution deploying high-frequency trading platforms and cutting-edge quantitative analytics.'
            },
        ]

        companies_dict = {}
        for cdata in companies_data:
            comp, _ = Company.objects.get_or_create(
                name=cdata['name'],
                defaults=cdata
            )
            companies_dict[cdata['name']] = comp

        # 4. Placement Drives
        drives_data = [
            {
                'company': companies_dict['Google Cloud'],
                'job_title': 'Associate Software Engineer - Cloud Platforms',
                'job_role': 'Software Development Engineer',
                'job_description': 'Join the Core Cloud Platform engineering group. You will build highly available distributed systems that scale to millions of concurrent requests worldwide.',
                'min_cgpa': 7.50,
                'allowed_branches': 'Computer Science & Engineering, Information Technology, AI & Machine Learning, Data Science',
                'max_backlogs': 0,
                'required_academic_score': 70.0,
                'application_deadline': date.today() + timedelta(days=20),
                'drive_date': date.today() + timedelta(days=28),
                'salary_package': '18.5 LPA (Base + Bonus + Equity)',
                'additional_requirements': 'Candidates must clear an online algorithmic coding round followed by system design interviews.',
                'status': PlacementDrive.STATUS_ACTIVE,
                'skills': ['Python', 'Data Structures & Algorithms', 'System Design', 'Docker', 'Linux Systems Administration'],
            },
            {
                'company': companies_dict['Stripe'],
                'job_title': 'Backend Systems Engineer - Payments Core',
                'job_role': 'Full Stack / Backend Engineer',
                'job_description': 'Build high-reliability payment routing services, webhook delivery systems, and real-time fraud mitigation microservices.',
                'min_cgpa': 7.00,
                'allowed_branches': 'Computer Science & Engineering, Information Technology, AI & Machine Learning',
                'max_backlogs': 0,
                'required_academic_score': 65.0,
                'application_deadline': date.today() + timedelta(days=14),
                'drive_date': date.today() + timedelta(days=21),
                'salary_package': '22.0 LPA (CTC)',
                'additional_requirements': 'Strong understanding of ACID database transactions, concurrency, and idempotent API design.',
                'status': PlacementDrive.STATUS_ACTIVE,
                'skills': ['Python', 'PostgreSQL', 'REST APIs', 'Docker', 'Problem Solving'],
            },
            {
                'company': companies_dict['Amazon AWS'],
                'job_title': 'Cloud Support & DevOps Associate',
                'job_role': 'Cloud / DevOps Engineer',
                'job_description': 'Design, deploy, and troubleshoot mission-critical cloud deployments on Amazon Web Services across compute, storage, and networking layers.',
                'min_cgpa': 6.50,
                'allowed_branches': 'Computer Science & Engineering, Information Technology, Electronics & Communication, Electrical & Electronics',
                'max_backlogs': 1,
                'required_academic_score': 60.0,
                'application_deadline': date.today() + timedelta(days=25),
                'drive_date': date.today() + timedelta(days=35),
                'salary_package': '16.0 LPA',
                'additional_requirements': 'Demonstrated competence in Linux command line and cloud fundamentals.',
                'status': PlacementDrive.STATUS_ACTIVE,
                'skills': ['AWS Cloud', 'Docker', 'Linux Systems Administration', 'CI/CD Automation'],
            },
            {
                'company': companies_dict['Microsoft'],
                'job_title': 'Applied AI & Machine Learning Engineer',
                'job_role': 'Machine Learning Engineer',
                'job_description': 'Research and fine-tune large foundation models, integrate enterprise copilot solutions, and engineer scalable inference pipelines.',
                'min_cgpa': 8.00,
                'allowed_branches': 'Computer Science & Engineering, AI & Machine Learning, Data Science',
                'max_backlogs': 0,
                'required_academic_score': 75.0,
                'application_deadline': date.today() + timedelta(days=30),
                'drive_date': date.today() + timedelta(days=40),
                'salary_package': '21.5 LPA',
                'additional_requirements': 'Hands-on project experience with deep learning frameworks and model optimization.',
                'status': PlacementDrive.STATUS_ACTIVE,
                'skills': ['Python', 'Machine Learning', 'Data Structures & Algorithms', 'Docker'],
            },
            {
                'company': companies_dict['Goldman Sachs'],
                'job_title': 'Analyst - Quantitative & Financial Engineering',
                'job_role': 'Quantitative Software Engineer',
                'job_description': 'Engineer low-latency quantitative analytics pipelines, backtest automated investment algorithms, and analyze market order flow.',
                'min_cgpa': 8.20,
                'allowed_branches': 'Computer Science & Engineering, AI & Machine Learning, Data Science',
                'max_backlogs': 0,
                'required_academic_score': 80.0,
                'application_deadline': date.today() + timedelta(days=10),
                'drive_date': date.today() + timedelta(days=18),
                'salary_package': '24.0 LPA',
                'additional_requirements': 'Exceptional problem solving and quantitative reasoning abilities.',
                'status': PlacementDrive.STATUS_ACTIVE,
                'skills': ['Python', 'Data Structures & Algorithms', 'Problem Solving', 'PostgreSQL'],
            },
        ]

        for ddata in drives_data:
            req_skills = ddata.pop('skills')
            drive, created = PlacementDrive.objects.get_or_create(
                company=ddata['company'],
                job_title=ddata['job_title'],
                defaults=ddata
            )
            if created or not drive.required_skills.exists():
                for s_name in req_skills:
                    if s_name in skills_dict:
                        drive.required_skills.add(skills_dict[s_name])

        # 5. Blog Posts (Section 4 requirements)
        blog_posts_data = [
            {
                'title': 'How to Build a Placement-Ready Resume',
                'category': 'Career Strategy',
                'short_article': (
                    "A winning placement resume focuses on demonstrated impact rather than generic task lists. "
                    "Highlight verified projects, production architectures, and specific technologies you mastered. "
                    "Use quantifiable metrics such as latency reductions or test coverage improvements. "
                    "Keep formatting clean, concise, and easy for campus recruiters to scan in under thirty seconds. "
                    "Ensure every skill listed is backed by tangible academic achievements or project code repositories."
                ),
            },
            {
                'title': 'Skills That Companies Look For in 2026',
                'category': 'Industry Insights',
                'short_article': (
                    "Modern hiring teams increasingly prioritize fundamental problem-solving over memorization. "
                    "Strong foundations in data structures, API architecture, containerization, and relational database modeling form the baseline. "
                    "Equally critical are clear technical communication, systematic debugging methodologies, and collaborative code review practices. "
                    "Demonstrating end-to-end delivery of working full-stack applications with automated testing signals immediate workplace readiness and sets top tier candidates apart."
                ),
            },
            {
                'title': 'How to Prepare for Technical Interviews',
                'category': 'Interview Prep',
                'short_article': (
                    "Consistent practice is the cornerstone of technical interview excellence. "
                    "Begin by articulating your thought process out loud before writing any code. "
                    "Clarify requirements, test boundary cases, and analyze runtime complexity systematically. "
                    "Review core system design principles such as caching, load balancing, and data consistency. "
                    "Finally, prepare concise stories explaining architectural choices and technical challenges overcome in your major projects."
                ),
            },
        ]

        for bp in blog_posts_data:
            BlogPost.objects.get_or_create(title=bp['title'], defaults=bp)

        # 6. Sample Students
        students_info = [
            {
                'username': 'alex.morgan',
                'email': 'alex.morgan@university.edu',
                'full_name': 'Alex Morgan',
                'branch': StudentProfile.BRANCH_CSE,
                'year_of_study': 4,
                'cgpa': 8.85,
                'current_backlogs': 0,
                'contact_phone': '+1 (555) 234-5678',
                'bio': 'Passionate systems engineer with hands-on expertise in distributed systems, asynchronous microservices, and database tuning.',
                'skills': [
                    ('Python', StudentSkill.PROFICIENCY_ADVANCED, True),
                    ('Django', StudentSkill.PROFICIENCY_ADVANCED, True),
                    ('PostgreSQL', StudentSkill.PROFICIENCY_ADVANCED, True),
                    ('Data Structures & Algorithms', StudentSkill.PROFICIENCY_ADVANCED, True),
                    ('Docker', StudentSkill.PROFICIENCY_INTERMEDIATE, True),
                    ('System Design', StudentSkill.PROFICIENCY_INTERMEDIATE, True),
                    ('Technical Writing', StudentSkill.PROFICIENCY_ADVANCED, True),
                ],
                'submissions': [
                    {
                        'title': 'Distributed Consensus Key-Value Store',
                        'category': AcademicSubmission.CATEGORY_PROJECT,
                        'description': 'Designed and implemented a Raft-based distributed key-value store in Python with leader election, log replication, and persistence.',
                        'skill_name': 'Python',
                        'status': AcademicSubmission.STATUS_APPROVED,
                        'rubric': {'relevance': 20, 'quality': 29, 'practical': 24, 'originality': 24},
                        'feedback': 'Exceptional architectural clarity and test coverage. Benchmark analysis demonstrates solid distributed concurrency management.',
                    },
                    {
                        'title': 'AWS Certified Solutions Architect Certification',
                        'category': AcademicSubmission.CATEGORY_CERTIFICATE,
                        'description': 'Official AWS Solutions Architect Associate credential verifying multi-tier cloud infrastructure, VPC security, and IAM compliance.',
                        'skill_name': 'AWS Cloud',
                        'status': AcademicSubmission.STATUS_APPROVED,
                        'rubric': {'relevance': 20, 'quality': 28, 'practical': 25, 'originality': 23},
                        'feedback': 'Verified official score transcript. Meets enterprise infrastructure standards.',
                    },
                ]
            },
            {
                'username': 'priya.sharma',
                'email': 'priya.sharma@university.edu',
                'full_name': 'Priya Sharma',
                'branch': StudentProfile.BRANCH_AIML,
                'year_of_study': 3,
                'cgpa': 8.40,
                'current_backlogs': 0,
                'contact_phone': '+1 (555) 345-6789',
                'bio': 'Machine learning researcher focused on transformer architectures, NLP pipelines, and computer vision deployment.',
                'skills': [
                    ('Python', StudentSkill.PROFICIENCY_ADVANCED, True),
                    ('Machine Learning', StudentSkill.PROFICIENCY_ADVANCED, True),
                    ('Data Structures & Algorithms', StudentSkill.PROFICIENCY_INTERMEDIATE, True),
                    ('Verbal Presentation', StudentSkill.PROFICIENCY_ADVANCED, True),
                ],
                'submissions': [
                    {
                        'title': 'Multilingual Medical Dialogue Intent Classifier',
                        'category': AcademicSubmission.CATEGORY_PROJECT,
                        'description': 'Fine-tuned multilingual transformer models achieving 94.2% F1 score on clinical inquiry classification benchmarks.',
                        'skill_name': 'Machine Learning',
                        'status': AcademicSubmission.STATUS_APPROVED,
                        'rubric': {'relevance': 19, 'quality': 28, 'practical': 23, 'originality': 24},
                        'feedback': 'Rigorous experimental methodology with ablation studies. Commendable application of deep learning in healthcare.',
                    },
                    {
                        'title': 'DeepLearning.AI NLP Specialization Certificate',
                        'category': AcademicSubmission.CATEGORY_CERTIFICATE,
                        'description': 'Specialization credentials covering attention mechanisms, transformer models, and embeddings.',
                        'skill_name': 'Machine Learning',
                        'status': AcademicSubmission.STATUS_PENDING,
                        'rubric': None,
                        'feedback': '',
                    }
                ]
            },
            {
                'username': 'david.miller',
                'email': 'david.miller@university.edu',
                'full_name': 'David Miller',
                'branch': StudentProfile.BRANCH_IT,
                'year_of_study': 4,
                'cgpa': 7.10,
                'current_backlogs': 0,
                'contact_phone': '+1 (555) 456-7890',
                'bio': 'Frontend and UI enthusiast interested in modern web tooling and responsive layout engineering.',
                'skills': [
                    ('JavaScript / TypeScript', StudentSkill.PROFICIENCY_INTERMEDIATE, True),
                    ('React', StudentSkill.PROFICIENCY_INTERMEDIATE, True),
                    ('Agile & Scrum', StudentSkill.PROFICIENCY_BEGINNER, False),
                ],
                'submissions': [
                    {
                        'title': 'Interactive Data Visualization Dashboard',
                        'category': AcademicSubmission.CATEGORY_PROJECT,
                        'description': 'Engineered a real-time metrics dashboard utilizing modern canvas components and state management.',
                        'skill_name': 'React',
                        'status': AcademicSubmission.STATUS_APPROVED,
                        'rubric': {'relevance': 18, 'quality': 24, 'practical': 20, 'originality': 21},
                        'feedback': 'Clean UI execution. Could improve test coverage and accessibility standards.',
                    }
                ],
                # Disciplinary incident showcase (Section 12)
                'discipline': {
                    'category': DisciplineRecord.CATEGORY_MOBILE,
                    'incident_date': date.today() - timedelta(days=45),
                    'description': 'Candidate observed accessing unauthorized mobile communication device during Midterm Operating Systems examination session.',
                    'admin_remarks': 'Proctor confiscated device. Formal inquiry hearing convened with academic board.',
                    'status': DisciplineRecord.STATUS_CONFIRMED,
                    'is_debarred': False,  # Not debarred initially, or can be tested
                    'appeal': {
                        'statement': 'I deeply apologize for this lapse in judgment. The device was received due to an urgent family medical emergency notification, and no exam material was accessed. I request consideration based on prior exemplary conduct.',
                        'status': DisciplineAppeal.STATUS_PENDING,
                    }
                }
            },
            {
                'username': 'elena.rostova',
                'email': 'elena.rostova@university.edu',
                'full_name': 'Elena Rostova',
                'branch': StudentProfile.BRANCH_CSE,
                'year_of_study': 4,
                'cgpa': 9.20,
                'current_backlogs': 0,
                'contact_phone': '+1 (555) 567-8901',
                'bio': 'Competitive programmer and cloud infrastructure developer with high algorithmic speed and rigor.',
                'skills': [
                    ('Python', StudentSkill.PROFICIENCY_ADVANCED, True),
                    ('Data Structures & Algorithms', StudentSkill.PROFICIENCY_ADVANCED, True),
                    ('System Design', StudentSkill.PROFICIENCY_ADVANCED, True),
                    ('Docker', StudentSkill.PROFICIENCY_ADVANCED, True),
                    ('PostgreSQL', StudentSkill.PROFICIENCY_ADVANCED, True),
                ],
                'submissions': [
                    {
                        'title': 'High-Throughput Distributed Rate Limiter',
                        'category': AcademicSubmission.CATEGORY_PROJECT,
                        'description': 'Sliding-window counter rate limiting service implemented in Python with Redis backing and sub-millisecond latencies.',
                        'skill_name': 'Python',
                        'status': AcademicSubmission.STATUS_APPROVED,
                        'rubric': {'relevance': 20, 'quality': 30, 'practical': 25, 'originality': 25},
                        'feedback': 'Flawless engineering and documentation. Full 100/100 benchmark score.',
                    }
                ]
            }
        ]

        dummy_doc_content = b"%PDF-1.4 ... Sample academic verification document for testing purposes."

        for s_info in students_info:
            user, _ = User.objects.get_or_create(
                username=s_info['username'],
                defaults={
                    'email': s_info['email'],
                    'first_name': s_info['full_name'].split()[0],
                    'last_name': s_info['full_name'].split()[1],
                }
            )
            user.set_password('StudentPass123!')
            user.save()

            UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': UserProfile.ROLE_STUDENT}
            )

            student, _ = StudentProfile.objects.update_or_create(
                user=user,
                defaults={
                    'full_name': s_info['full_name'],
                    'email': s_info['email'],
                    'branch': s_info['branch'],
                    'year_of_study': s_info['year_of_study'],
                    'cgpa': s_info['cgpa'],
                    'current_backlogs': s_info['current_backlogs'],
                    'contact_phone': s_info['contact_phone'],
                    'bio': s_info['bio'],
                }
            )

            # Skills
            for sk_name, prof, verified in s_info.get('skills', []):
                if sk_name in skills_dict:
                    ss, _ = StudentSkill.objects.update_or_create(
                        student=student,
                        skill=skills_dict[sk_name],
                        defaults={
                            'proficiency': prof,
                            'is_verified': verified,
                            'verified_by': admin_user if verified else None,
                            'verified_at': timezone.now() if verified else None,
                        }
                    )

            # Submissions & Evaluations
            for sub_data in s_info.get('submissions', []):
                rel_skill = skills_dict.get(sub_data['skill_name'])
                sub, created = AcademicSubmission.objects.get_or_create(
                    student=student,
                    title=sub_data['title'],
                    defaults={
                        'category': sub_data['category'],
                        'description': sub_data['description'],
                        'related_skill': rel_skill,
                        'status': sub_data['status'],
                    }
                )
                if not sub.file:
                    sub.file.save(f"{sub_data['title'].replace(' ', '_')[:30]}.pdf", ContentFile(dummy_doc_content), save=True)

                if sub_data['rubric'] and sub_data['status'] == AcademicSubmission.STATUS_APPROVED:
                    r = sub_data['rubric']
                    AcademicEvaluation.objects.update_or_create(
                        submission=sub,
                        defaults={
                            'evaluated_by': admin_user,
                            'marks_relevance': r['relevance'],
                            'marks_quality': r['quality'],
                            'marks_practical': r['practical'],
                            'marks_originality': r['originality'],
                            'feedback': sub_data['feedback'],
                        }
                    )

            # Disciplinary incident if present
            if 'discipline' in s_info:
                d_info = s_info['discipline']
                rec, _ = DisciplineRecord.objects.get_or_create(
                    student=student,
                    incident_category=d_info['category'],
                    defaults={
                        'incident_date': d_info['incident_date'],
                        'description': d_info['description'],
                        'admin_remarks': d_info['admin_remarks'],
                        'status': d_info['status'],
                        'is_debarred': d_info['is_debarred'],
                        'recorded_by': admin_user,
                    }
                )
                if 'appeal' in d_info:
                    app_info = d_info['appeal']
                    DisciplineAppeal.objects.get_or_create(
                        record=rec,
                        student=student,
                        defaults={
                            'appeal_statement': app_info['statement'],
                            'status': app_info['status'],
                        }
                    )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully with companies, placement drives, blog posts, skills, students, submissions, and evaluations!"))
