import asyncio
import uuid
import datetime
from sqlalchemy import select
from app.db.session import async_session_factory, init_db
from app.models.models import (
    Award,
    BenchmarkScore,
    Certification,
    CodingProblem,
    Education,
    Event,
    JobListing,
    LeaderboardEntry,
    MCQQuestion,
    PositionOfResponsibility,
    Profile,
    ProfileProject,
    ScorecardEntry,
    User,
    WorkExperience,
)
from app.core.security import hash_password


async def seed_content():
    """Catalog data (problems, questions, jobs, events) plus the two demo logins."""
    async with async_session_factory() as session:
        res = await session.execute(select(CodingProblem))
        if res.scalars().first():
            print("[INFO] Content already seeded.")
            return

        print("[INFO] Seeding initial data...")

        # 1. Seed Admin & Demo Student (skip any that already exist)
        existing_emails = set(
            (await session.execute(select(User.email))).scalars().all()
        )

        admin_user = None
        if "admin@careeradvisor.ai" not in existing_emails:
            admin_user = User(
                email="admin@careeradvisor.ai",
                hashed_password=hash_password("admin12345"),
                full_name="System Admin",
                role="admin"
            )
            session.add(admin_user)

        demo_student = None
        if "student@careeradvisor.ai" not in existing_emails:
            demo_student = User(
                email="student@careeradvisor.ai",
                hashed_password=hash_password("student12345"),
                full_name="Alex Johnson",
                role="student"
            )
            session.add(demo_student)

        if admin_user is not None or demo_student is not None:
            await session.flush()

        if admin_user is not None:
            session.add(Profile(user_id=admin_user.id, bio="Platform Administrator"))
            session.add(LeaderboardEntry(user_id=admin_user.id, total_xp=0))

        if demo_student is not None:
            session.add(Profile(
                user_id=demo_student.id,
                bio="Aspiring Full Stack Engineer & AI Enthusiast",
                education="B.Tech Computer Science",
                cgpa=8.8,
                university="Tech University",
                major="Computer Science",
                location="San Francisco, CA",
                interests=["Machine Learning", "Web Development", "System Design"]
            ))
            session.add(LeaderboardEntry(user_id=demo_student.id, total_xp=150, level=2, problems_solved=3, quizzes_passed=2, streak_days=5))

        # 2. Seed Coding Problems
        problems = [
            CodingProblem(
                title="Two Sum",
                description="Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.",
                difficulty="easy",
                tags=["Array", "Hash Table"],
                companies=["Google", "Amazon", "Meta"],
                languages=["python", "javascript"],
                sample_input="nums = [2,7,11,15], target = 9",
                sample_output="[0,1]",
                test_cases=[
                    {"input": "2 7 11 15\n9", "expected_output": "[0, 1]"},
                ],
                starter_code={
                    "python": "def two_sum(nums, target):\n    # Write your solution here\n    pass",
                    "javascript": "function twoSum(nums, target) {\n    // Write your solution here\n}"
                },
                xp_reward=10
            ),
            CodingProblem(
                title="Reverse String",
                description="Write a function that reverses a string. The input string is given as an array of characters.",
                difficulty="easy",
                tags=["String", "Two Pointers"],
                companies=["Apple", "Microsoft"],
                languages=["python", "javascript"],
                sample_input='s = ["h","e","l","l","o"]',
                sample_output='["o","l","l","e","h"]',
                test_cases=[
                    {"input": "hello", "expected_output": "olleh"}
                ],
                starter_code={
                    "python": "def reverse_string(s):\n    return s[::-1]",
                    "javascript": "function reverseString(s) {\n    return s.split('').reverse().join('');\n}"
                },
                xp_reward=10
            ),
            CodingProblem(
                title="Valid Parentheses",
                description="Given a string `s` containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
                difficulty="medium",
                tags=["Stack", "String"],
                companies=["Google", "Meta", "Amazon"],
                languages=["python", "javascript"],
                sample_input='s = "()[]{}"',
                sample_output="True",
                test_cases=[],
                starter_code={
                    "python": "def is_valid(s):\n    # Write your solution here\n    pass"
                },
                xp_reward=25
            )
        ]
        session.add_all(problems)

        # 3. Seed MCQ Aptitude Questions
        mcqs = [
            MCQQuestion(
                question_text="If 5 workers complete a task in 12 days, how many days will 10 workers take to complete the same task at the same rate?",
                options=["4 days", "6 days", "8 days", "10 days"],
                correct_index=1,
                topic="Quantitative Aptitude",
                difficulty="easy",
                explanation="Work = Workers x Days. Total work = 5 x 12 = 60 worker-days. For 10 workers: 60 / 10 = 6 days."
            ),
            MCQQuestion(
                question_text="Choose the synonym for 'Ephemeral':",
                options=["Permanent", "Transient", "Eternal", "Substantial"],
                correct_index=1,
                topic="Verbal Ability",
                difficulty="easy",
                explanation="Ephemeral means lasting for a very short time; transient is a synonym."
            ),
            MCQQuestion(
                question_text="Complete the sequence: 2, 6, 12, 20, 30, ?",
                options=["36", "40", "42", "48"],
                correct_index=2,
                topic="Logical Reasoning",
                difficulty="medium",
                explanation="Differences between consecutive numbers are 4, 6, 8, 10... so next difference is 12. 30 + 12 = 42."
            )
        ]
        session.add_all(mcqs)

        # 4. Seed Job Listings
        jobs = [
            JobListing(
                title="Full Stack Software Engineer",
                company="TechCorp Innovations",
                description="We are looking for a proactive Full Stack Developer with experience in React, Python (FastAPI), and PostgreSQL to build next-generation web platforms.",
                location="San Francisco, CA",
                remote=True,
                salary_range="$110,000 - $140,000",
                required_skills=["python", "react", "fastapi", "postgresql", "docker", "git"],
                experience_level="Entry-level / New Grad",
                job_type="Full-time"
            ),
            JobListing(
                title="Junior AI / Machine Learning Engineer",
                company="DataMind AI Systems",
                description="Join our AI research team working on LLMs, RAG systems, and vector databases. Strong background in Python, PyTorch, and NLP required.",
                location="New York, NY",
                remote=True,
                salary_range="$120,000 - $150,000",
                required_skills=["python", "pytorch", "nlp", "llm", "chromadb", "sql"],
                experience_level="Entry-level",
                job_type="Full-time"
            ),
            JobListing(
                title="Frontend Developer (React & TypeScript)",
                company="Apex UX Labs",
                description="Seeking a UI/UX-focused React developer to create beautiful, fast, and accessible user interfaces.",
                location="Austin, TX",
                remote=False,
                salary_range="$95,000 - $120,000",
                required_skills=["react", "typescript", "css", "html", "web performance"],
                experience_level="Junior",
                job_type="Full-time"
            )
        ]
        session.add_all(jobs)

        # 5. Seed Events
        events = [
            Event(
                title="Global AI & Tech Career Fair 2026",
                description="Connect directly with tech recruiters from top firms including Google, Meta, and high-growth AI startups.",
                event_date=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=14),
                location="Virtual / Zoom",
                event_url="https://careeradvisor.ai/events/fair2026",
                capacity=500
            ),
            Event(
                title="Mastering Technical Coding Interviews Workshop",
                description="Interactive live session on Data Structures, Algorithms, and System Design interviewing strategies.",
                event_date=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7),
                location="Online Webinar",
                event_url="https://careeradvisor.ai/events/interview-prep",
                capacity=200
            )
        ]
        session.add_all(events)

        await session.commit()
        print("[SUCCESS] Database successfully seeded with initial content!")


async def seed_demo_profile():
    """Fills the demo student's My Profile section end to end.

    Runs separately from content seeding (and with its own guard) so it still
    applies to a database that was partially seeded earlier.
    """
    async with async_session_factory() as session:
        user = (
            await session.execute(select(User).where(User.email == "student@careeradvisor.ai"))
        ).scalar_one_or_none()
        if not user:
            print("[INFO] Demo student not found — skipping profile seed.")
            return

        profile = (
            await session.execute(select(Profile).where(Profile.user_id == user.id))
        ).scalar_one_or_none()
        if not profile:
            profile = Profile(user_id=user.id)
            session.add(profile)
            await session.flush()

        already = (
            await session.execute(select(Education).where(Education.user_id == user.id))
        ).scalars().first()
        if already:
            print("[INFO] Demo profile already populated.")
            return

        print("[INFO] Seeding demo student profile...")

        # ── Header, contact and personal details ──
        profile.headline = "AI & Data Science Undergraduate | Full-Stack Developer | Building AI-Powered Applications"
        profile.enrollment_id = "STU2026099227"
        profile.experience_level = "Fresher"
        profile.location = "Bengaluru"
        profile.phone = "+91 63605 36047"
        profile.gender = "Male"
        profile.country = "India"
        profile.state = "Karnataka"
        profile.city = "Bengaluru"
        profile.about_me = (
            "Final-year AI & Data Science undergraduate who enjoys turning messy problems into "
            "working software. I build full-stack products end to end — FastAPI and PostgreSQL on the "
            "backend, React on the front — and I have spent the last year going deep on retrieval-augmented "
            "generation and multi-agent systems. Looking for a graduate software or ML engineering role "
            "where I can ship to real users."
        )

        # ── Links ──
        profile.github_url = "https://github.com/example-student"
        profile.linkedin_url = "https://linkedin.com/in/example-student"
        profile.portfolio_url = "https://example-student.dev"
        profile.other_links = [{"label": "Technical blog", "url": "https://blog.example-student.dev"}]

        profile.additional_info = [
            {"label": "Languages known", "value": "English, Hindi, Kannada"},
            {"label": "Open source", "value": "Contributor to 3 Python projects"},
        ]

        # ── Program / mentorship / training ──
        profile.program_name = "Merit Scholarship Program"
        profile.program_year = "2026-27"
        profile.institution_rating = "AAAA"
        profile.program_extra = [
            {"label": "Cohort", "value": "Batch 12"},
            {"label": "Scholarship status", "value": "Active"},
        ]
        profile.is_mentee = True
        profile.mentor_name = "R. Sharma"
        profile.mentorship_notes = "Fortnightly sessions focused on system design and interview readiness."
        profile.training_details = [
            {"name": "Communication Skills", "status": "Completed", "score": "95", "notes": "Pre-assessment 26"},
            {"name": "Aptitude Program", "status": "Completed", "score": "79.6", "notes": "Pre-assessment 58"},
            {"name": "Career Readiness", "status": "Completed", "score": "", "notes": ""},
            {"name": "Mock Interviews", "status": "Completed", "score": "", "notes": "3 rounds"},
        ]

        # ── School results ──
        profile.class_10_percentage = 79.40
        profile.class_10_board = "CBSE"
        profile.class_12_percentage = 96.33
        profile.class_12_board = "State Board"

        # ── Job preferences ──
        profile.open_for = ["Full Time", "Internship"]
        profile.job_roles = ["Software Engineer", "Backend Developer", "ML Engineer"]
        profile.available_for_hire = True
        profile.willing_to_relocate = True
        profile.preferred_locations = ["Bengaluru", "Pune", "Remote"]
        profile.industry = "Engineering - Software"
        profile.expected_ctc = 1200000
        profile.ctc_period = "Year"

        # ── Education with semester history ──
        session.add(
            Education(
                user_id=user.id,
                institute="State Institute of Technology",
                degree="BE/B.Tech",
                specialization="Artificial Intelligence and Data Science",
                start_year="2023",
                end_year="2027",
                cgpa=8.75,
                cgpa_scale=10.0,
                percentage=87.55,
                is_current=True,
                ongoing_backlogs=0,
                total_backlogs=0,
                semesters=[
                    {"semester": "Sem 1", "cgpa": 8.8, "ongoing_backlogs": 0, "total_backlogs": 0, "marksheet_doc_id": None},
                    {"semester": "Sem 2", "cgpa": 9.0, "ongoing_backlogs": 0, "total_backlogs": 0, "marksheet_doc_id": None},
                    {"semester": "Sem 3", "cgpa": 8.52, "ongoing_backlogs": 0, "total_backlogs": 0, "marksheet_doc_id": None},
                    {"semester": "Sem 4", "cgpa": 8.7, "ongoing_backlogs": 0, "total_backlogs": 0, "marksheet_doc_id": None},
                ],
            )
        )

        # ── Work experience ──
        session.add(
            WorkExperience(
                user_id=user.id,
                company="Northwind Labs",
                role="Backend Engineering Intern",
                employment_type="Internship",
                location="Remote",
                start_date="2025-11",
                end_date="2026-03",
                is_current=False,
                highlights=[
                    "Built Python services for a recommendation platform generating personalised plans from user health data.",
                    "Developed REST APIs for recommendation workflows, user profile management and frontend integration.",
                    "Collaborated across functional teams to improve recommendation accuracy and API performance.",
                ],
            )
        )

        # ── Position of responsibility ──
        session.add(
            PositionOfResponsibility(
                user_id=user.id,
                title="Campaigning Coordinator",
                event_name="Annual College Fest",
                department="Department of Co-Curricular Activities",
                organization="State Institute of Technology",
                start_date="2026-04-01",
                end_date="2026-05-20",
                highlights=[
                    "Served as Campaigning Coordinator for the annual college fest.",
                    "Coordinated promotional activities and campus outreach to increase student participation.",
                    "Collaborated with committee members to plan and execute campaign strategies.",
                ],
            )
        )

        # ── Projects ──
        session.add_all([
            ProfileProject(
                user_id=user.id,
                title="Cognitive Memory & Multi-Agent Reasoning System",
                subtitle="Personal project",
                description="An AI assistant with multi-agent workflows, semantic memory management, OCR and speech processing.",
                tech_stack=["Python", "ChromaDB", "FastAPI", "Sentence Transformers"],
                highlights=[
                    "Designed a scalable vector database pipeline for intelligent context retrieval and memory optimisation.",
                    "Implemented recursive reasoning workflows, hallucination detection and adaptive context retention.",
                ],
                start_date="2026-01",
                end_date="",
                is_ongoing=True,
                repo_url="https://github.com/example-student/cognitive-memory",
                display_order=0,
            ),
            ProfileProject(
                user_id=user.id,
                title="Smart Traffic Signal Display System",
                subtitle="Academic project",
                description="A traffic monitoring and congestion analysis platform with emergency-vehicle prioritisation.",
                tech_stack=["React", "Tailwind CSS", "Recharts", "IoT"],
                highlights=[
                    "Implemented an emergency green corridor with V2V communication for ambulance prioritisation.",
                    "Built responsive dashboards and transportation analytics visualisations over simulated datasets.",
                ],
                start_date="2025-08",
                end_date="2025-12",
                display_order=1,
            ),
            ProfileProject(
                user_id=user.id,
                title="Offline-First Retail Store Application",
                subtitle="Hackathon finalist",
                description="An offline-first mobile app for small retailers covering inventory, billing and daily sales tracking.",
                tech_stack=["Flutter", "Dart", "Firebase", "SQLite"],
                highlights=[
                    "Implemented local storage and synchronisation for low-connectivity environments.",
                    "Designed store management workflows for stock updates, billing and transaction history.",
                ],
                start_date="2025-03",
                end_date="2025-06",
                display_order=2,
            ),
        ])

        # ── Awards ──
        session.add(
            Award(
                user_id=user.id,
                title="2nd Runner Up - CodeSprint 3.0",
                issued_by="Meenakshi Institute of Technology",
                issue_date="2025-04-04",
                achievement_type="Technical",
                description="Placed third among 120 teams in a 24-hour competitive programming and product build contest.",
                award_url="https://example-student.dev/awards/codesprint",
            )
        )

        # ── Certifications ──
        session.add_all([
            Certification(
                user_id=user.id,
                name="Communication Skills Program",
                issuer="Career Advisor Academy",
                course_duration="6 weeks",
                validity="Lifetime Validity",
                cert_type="Communication",
                specialization="English Specialization",
                pre_assessment_score="26",
                marks_obtained="95",
                points_earned="95",
                conclusion="Completed",
                display_order=0,
            ),
            Certification(
                user_id=user.id,
                name="Aptitude Program",
                issuer="Career Advisor Academy",
                course_duration="8 weeks",
                validity="Lifetime Validity",
                cert_type="Aptitude",
                specialization="Aptitude Specialization",
                pre_assessment_score="58",
                marks_obtained="79.6",
                points_earned="79.6",
                conclusion="Completed",
                display_order=1,
            ),
            Certification(
                user_id=user.id,
                name="Cloud Security Fundamentals",
                issuer="Zscaler",
                course_duration="4 weeks",
                validity="Lifetime Validity",
                cert_type="Technical",
                specialization="Cloud Security",
                conclusion="Completed",
                display_order=2,
            ),
        ])

        # ── Employability benchmarks ──
        session.add_all([
            BenchmarkScore(
                user_id=user.id, stage="baseline", provider="Employability Benchmark",
                analytical_score=36, logical_score=60, taken_on="2025-08-12",
            ),
            BenchmarkScore(
                user_id=user.id, stage="midline", provider="Employability Benchmark",
                analytical_score=79, logical_score=53, taken_on="2026-02-18",
            ),
        ])

        # ── A custom event score ──
        session.add(
            ScorecardEntry(
                user_id=user.id, category="custom_event", title="Inter-college Hackathon",
                score=88, max_score=100, scored_on="2026-01-20", notes="Finalist",
            )
        )

        await session.commit()
        print("[SUCCESS] Demo student profile populated.")


async def seed_database():
    await init_db()
    await seed_content()
    await seed_demo_profile()


if __name__ == "__main__":
    asyncio.run(seed_database())
