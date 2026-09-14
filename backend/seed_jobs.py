"""Seeds the Job Board with rich, standard-format company postings across the
20 supported portals. Idempotent: matched by ``slug`` so re-running updates the
row in place and keeps applications (which reference job ids) intact.
"""

import asyncio
import datetime
import sys

from sqlalchemy import select

from app.db.session import async_session_factory, init_db
from app.models.models import JobListing

FIELDS = (
    "title", "company", "description", "location", "remote", "salary_range",
    "required_skills", "experience_level", "job_type", "source_portal",
    "company_logo", "company_tagline", "industry", "employment_mode", "openings",
    "application_deadline", "about_company", "responsibilities", "qualifications",
    "perks", "ctc_breakdown", "ctc_min", "ctc_max", "stipend_min", "stipend_max",
    "experience_min_years", "experience_max_years", "eligibility", "apply_questions",
    "is_active", "posted_at",
)

_now = datetime.datetime.now(datetime.timezone.utc)


def days_ago(n: int) -> datetime.datetime:
    return _now - datetime.timedelta(days=n)


# ── Reusable custom application questions ────────────────────────

Q_NOTICE = {
    "key": "notice_period", "label": "Notice period", "type": "select", "required": True,
    "options": ["Immediate", "15 days", "30 days", "60 days", "90 days"],
    "help": "How soon can you join?",
}
Q_CURRENT_CTC = {
    "key": "current_ctc", "label": "Current CTC (₹ LPA)", "type": "number", "required": False,
    "placeholder": "e.g. 6", "help": "Leave blank if fresher",
}
Q_EXPECTED_CTC = {
    "key": "expected_ctc", "label": "Expected CTC (₹ LPA)", "type": "number", "required": True,
    "placeholder": "e.g. 12",
}
Q_RELOCATE = {
    "key": "willing_to_relocate", "label": "Are you willing to relocate?", "type": "boolean",
    "required": True,
}
Q_WORK_AUTH = {
    "key": "work_authorization", "label": "Work authorization", "type": "select", "required": True,
    "options": ["Indian citizen", "Work visa holder", "Requires sponsorship"],
}
Q_PORTFOLIO = {
    "key": "portfolio_link", "label": "Portfolio / GitHub link", "type": "url", "required": False,
    "placeholder": "https://",
}
Q_START_DATE = {
    "key": "earliest_start", "label": "Earliest start date", "type": "date", "required": True,
}
Q_WHY = {
    "key": "why_join", "label": "Why do you want to join us?", "type": "textarea", "required": False,
    "placeholder": "A few sentences...",
}
Q_STIPEND_OK = {
    "key": "stipend_ack", "label": "Is the offered stipend acceptable?", "type": "boolean",
    "required": True,
}
Q_SHIFT = {
    "key": "shift_pref", "label": "Preferred shift", "type": "select", "required": False,
    "options": ["Day", "Night", "Rotational", "Flexible"],
}


def lpa(x: float) -> int:
    return int(x * 100000)


# ── Job builder ──────────────────────────────────────────────────

def job(**kw) -> dict:
    kw.setdefault("remote", False)
    kw.setdefault("is_active", True)
    kw.setdefault("openings", 1)
    kw.setdefault("employment_mode", "In Office")
    kw.setdefault("experience_min_years", 0.0)
    kw.setdefault("experience_max_years", None)
    kw.setdefault("stipend_min", None)
    kw.setdefault("stipend_max", None)
    kw.setdefault("ctc_min", None)
    kw.setdefault("ctc_max", None)
    kw.setdefault("qualifications", [])
    kw.setdefault("perks", [])
    kw.setdefault("ctc_breakdown", [])
    kw.setdefault("apply_questions", [])
    kw.setdefault("eligibility", [])
    kw.setdefault("application_deadline", "")
    kw.setdefault("company_tagline", "")
    return kw


def build_jobs() -> list[dict]:
    jobs: list[dict] = []

    # 1 — LinkedIn — SDE Backend (full time)
    jobs.append(job(
        slug="linkedin-sde-backend-python-nexora",
        title="Software Engineer - Backend (Python)",
        company="Nexora Labs", company_logo="🟦",
        company_tagline="Building developer-first fintech infrastructure",
        source_portal="LinkedIn", industry="Software / IT", job_type="full-time",
        experience_level="mid", employment_mode="Hybrid", location="Bengaluru, India",
        remote=False, openings=3, application_deadline="2026-10-15",
        salary_range="₹18 - 26 LPA", ctc_min=lpa(18), ctc_max=lpa(26),
        experience_min_years=2.0, experience_max_years=5.0,
        required_skills=["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
        description="Own backend services powering our payments platform — design APIs, tune databases and ship reliable, well-tested code.",
        about_company="Nexora Labs is a Series-B fintech company processing over ₹4,000 crore in annual payment volume for 12,000+ Indian businesses. Our engineering team of 80 works in small, autonomous squads.",
        responsibilities=[
            "Design and build scalable REST APIs with Python and FastAPI",
            "Model and optimize PostgreSQL schemas and queries for high throughput",
            "Write unit and integration tests; own services end-to-end in production",
            "Collaborate with product and frontend to ship features every sprint",
            "Participate in on-call rotation and incident response",
        ],
        qualifications=[
            "Experience with event-driven architecture (Kafka/SQS)",
            "Exposure to Kubernetes and CI/CD pipelines",
            "Contributions to open-source projects",
        ],
        perks=["Health insurance for family", "₹60k annual learning budget", "Hybrid — 3 days in office", "ESOPs"],
        ctc_breakdown=[
            {"component": "Fixed base", "amount": "₹16.5 LPA"},
            {"component": "Performance bonus", "amount": "up to ₹2.5 LPA"},
            {"component": "ESOPs (4-yr vest)", "amount": "₹7 LPA equivalent"},
        ],
        eligibility=[
            {"key": "cgpa", "type": "min_cgpa", "label": "Minimum CGPA 7.0", "value": 7.0},
            {"key": "exp", "type": "min_experience", "label": "At least 2 years experience", "value": 2},
            {"key": "skills", "type": "required_skills", "label": "Core skills", "value": ["Python", "SQL"]},
            {"key": "backlogs", "type": "max_backlogs", "label": "No active backlogs", "value": 0},
        ],
        apply_questions=[Q_NOTICE, Q_CURRENT_CTC, Q_EXPECTED_CTC, Q_RELOCATE, Q_PORTFOLIO],
        posted_at=days_ago(2),
    ))

    # 2 — Indeed — Full Stack Developer
    jobs.append(job(
        slug="indeed-fullstack-react-node-brightwave",
        title="Full Stack Developer (React + Node)",
        company="BrightWave Digital", company_logo="🌊",
        company_tagline="Digital products for global brands",
        source_portal="Indeed", industry="Software / IT", job_type="full-time",
        experience_level="mid", employment_mode="In Office", location="Pune, India",
        openings=2, application_deadline="2026-10-20",
        salary_range="₹12 - 18 LPA", ctc_min=lpa(12), ctc_max=lpa(18),
        experience_min_years=1.5, experience_max_years=4.0,
        required_skills=["React", "TypeScript", "Node.js", "MongoDB", "REST APIs"],
        description="Join a product team building customer-facing web apps end to end, from React UI to Node services.",
        about_company="BrightWave Digital is a 200-person product studio delivering web and mobile experiences for retail and media clients across 3 continents.",
        responsibilities=[
            "Build responsive UIs in React + TypeScript",
            "Develop and maintain Node.js/Express services and MongoDB data models",
            "Integrate third-party APIs and payment gateways",
            "Review pull requests and mentor interns",
        ],
        qualifications=["Experience with Next.js", "Familiarity with GraphQL", "AWS or GCP deployment experience"],
        perks=["Flexible hours", "Annual offsite", "Certification reimbursement"],
        ctc_breakdown=[
            {"component": "Fixed base", "amount": "₹13 LPA"},
            {"component": "Variable pay", "amount": "up to ₹3 LPA"},
            {"component": "Joining bonus", "amount": "₹1 LPA"},
        ],
        eligibility=[
            {"key": "cgpa", "type": "min_cgpa", "label": "Minimum CGPA 6.5", "value": 6.5},
            {"key": "exp", "type": "min_experience", "label": "At least 1.5 years experience", "value": 1.5},
            {"key": "skills", "type": "required_skills", "label": "Frontend + backend skills", "value": ["React", "Node.js"]},
        ],
        apply_questions=[Q_NOTICE, Q_EXPECTED_CTC, Q_PORTFOLIO, Q_WHY],
        posted_at=days_ago(4),
    ))

    # 3 — Naukri — Senior Data Engineer
    jobs.append(job(
        slug="naukri-senior-data-engineer-datacraft",
        title="Senior Data Engineer",
        company="DataCraft Analytics", company_logo="📊",
        company_tagline="Turning enterprise data into decisions",
        source_portal="Naukri.com", industry="Data / Analytics", job_type="full-time",
        experience_level="senior", employment_mode="Hybrid", location="Hyderabad, India",
        openings=2, application_deadline="2026-11-01",
        salary_range="₹22 - 34 LPA", ctc_min=lpa(22), ctc_max=lpa(34),
        experience_min_years=4.0, experience_max_years=8.0,
        required_skills=["Python", "Spark", "Airflow", "SQL", "AWS", "Kafka"],
        description="Build and scale batch and streaming data pipelines that power analytics for Fortune 500 clients.",
        about_company="DataCraft Analytics is a data engineering consultancy of 350 specialists serving BFSI and healthcare enterprises.",
        responsibilities=[
            "Design ETL/ELT pipelines with Spark and Airflow",
            "Build streaming ingestion with Kafka",
            "Optimize data warehouse cost and performance",
            "Establish data quality and observability standards",
        ],
        qualifications=["dbt experience", "Snowflake or Redshift", "Terraform / IaC"],
        perks=["Remote-friendly", "Health + life insurance", "Upskilling stipend ₹1 LPA"],
        ctc_breakdown=[
            {"component": "Fixed base", "amount": "₹24 LPA"},
            {"component": "Annual bonus", "amount": "up to ₹6 LPA"},
            {"component": "Retention bonus", "amount": "₹4 LPA"},
        ],
        eligibility=[
            {"key": "exp", "type": "min_experience", "label": "At least 4 years experience", "value": 4},
            {"key": "skills", "type": "required_skills", "label": "Data stack", "value": ["Python", "SQL", "Spark"]},
            {"key": "cgpa", "type": "min_cgpa", "label": "Minimum CGPA 6.0", "value": 6.0},
        ],
        apply_questions=[Q_NOTICE, Q_CURRENT_CTC, Q_EXPECTED_CTC, Q_RELOCATE],
        posted_at=days_ago(6),
    ))

    # 4 — Glassdoor — ML Engineer
    jobs.append(job(
        slug="glassdoor-ml-engineer-cognita",
        title="Machine Learning Engineer",
        company="Cognita AI", company_logo="🧠",
        company_tagline="Applied AI for real-world products",
        source_portal="Glassdoor", industry="Artificial Intelligence", job_type="full-time",
        experience_level="mid", employment_mode="Remote", location="Remote (India)",
        remote=True, openings=2, application_deadline="2026-10-25",
        salary_range="₹20 - 30 LPA", ctc_min=lpa(20), ctc_max=lpa(30),
        experience_min_years=2.0, experience_max_years=6.0,
        required_skills=["Python", "PyTorch", "NLP", "MLOps", "Docker"],
        description="Take ML models from notebook to production — training, evaluation, deployment and monitoring.",
        about_company="Cognita AI (rated 4.6 on Glassdoor) builds NLP products for legal and healthcare, backed by top-tier VCs.",
        responsibilities=[
            "Train and fine-tune NLP/LLM models",
            "Build reproducible training and evaluation pipelines",
            "Deploy models as scalable services and monitor drift",
            "Partner with research to productionize prototypes",
        ],
        qualifications=["LLM fine-tuning experience", "Vector databases", "Kubernetes"],
        perks=["100% remote", "Home-office setup budget", "Conference sponsorship"],
        ctc_breakdown=[
            {"component": "Fixed base", "amount": "₹22 LPA"},
            {"component": "Equity", "amount": "₹6 LPA equivalent"},
            {"component": "Performance bonus", "amount": "up to ₹2 LPA"},
        ],
        eligibility=[
            {"key": "exp", "type": "min_experience", "label": "At least 2 years experience", "value": 2},
            {"key": "skills", "type": "required_skills", "label": "ML skills", "value": ["Python", "PyTorch"]},
            {"key": "degree", "type": "allowed_degrees", "label": "CS / IT / Data Science degree",
             "value": ["Computer Science", "Data Science", "Information Technology", "Artificial Intelligence"]},
        ],
        apply_questions=[Q_NOTICE, Q_EXPECTED_CTC, Q_PORTFOLIO, Q_WORK_AUTH, Q_WHY],
        posted_at=days_ago(3),
    ))

    # 5 — Foundit — DevOps Engineer
    jobs.append(job(
        slug="foundit-devops-engineer-cloudpeak",
        title="DevOps Engineer",
        company="CloudPeak Systems", company_logo="☁️",
        company_tagline="Reliable cloud infrastructure at scale",
        source_portal="Foundit", industry="Cloud / Infrastructure", job_type="full-time",
        experience_level="mid", employment_mode="In Office", location="Chennai, India",
        openings=1, application_deadline="2026-10-30",
        salary_range="₹14 - 22 LPA", ctc_min=lpa(14), ctc_max=lpa(22),
        experience_min_years=2.0, experience_max_years=5.0,
        required_skills=["Kubernetes", "Terraform", "AWS", "CI/CD", "Docker", "Linux"],
        description="Own our cloud platform — infrastructure as code, CI/CD, observability and reliability.",
        about_company="CloudPeak Systems manages cloud infrastructure for 400+ SaaS companies with a 99.99% uptime SLA.",
        responsibilities=[
            "Manage Kubernetes clusters and Terraform modules",
            "Build and maintain CI/CD pipelines",
            "Set up monitoring, alerting and dashboards",
            "Automate provisioning and reduce cloud cost",
        ],
        qualifications=["ArgoCD / GitOps", "Prometheus + Grafana", "Cloud certification"],
        perks=["Health insurance", "On-call allowance", "Certification budget"],
        ctc_breakdown=[
            {"component": "Fixed base", "amount": "₹15 LPA"},
            {"component": "On-call + bonus", "amount": "up to ₹4 LPA"},
        ],
        eligibility=[
            {"key": "exp", "type": "min_experience", "label": "At least 2 years experience", "value": 2},
            {"key": "skills", "type": "required_skills", "label": "DevOps stack", "value": ["Docker", "AWS"]},
            {"key": "cgpa", "type": "min_cgpa", "label": "Minimum CGPA 6.5", "value": 6.5},
        ],
        apply_questions=[Q_NOTICE, Q_EXPECTED_CTC, Q_RELOCATE, Q_SHIFT],
        posted_at=days_ago(8),
    ))

    # 6 — Internshala — Software Development Intern
    jobs.append(job(
        slug="internshala-sde-intern-webspring",
        title="Software Development Intern",
        company="WebSpring Tech", company_logo="🌱",
        company_tagline="Where students become engineers",
        source_portal="Internshala", industry="Software / IT", job_type="internship",
        experience_level="entry", employment_mode="Remote", location="Remote (India)",
        remote=True, openings=10, application_deadline="2026-10-12",
        salary_range="₹15,000 - 25,000 /month", stipend_min=15000, stipend_max=25000,
        experience_min_years=0.0, experience_max_years=1.0,
        required_skills=["JavaScript", "React", "HTML", "CSS", "Git"],
        description="6-month internship building real product features with a supportive mentor and a shot at a pre-placement offer.",
        about_company="WebSpring Tech runs a structured internship program that has converted 70% of interns to full-time roles.",
        responsibilities=[
            "Build UI components in React under mentorship",
            "Fix bugs and write tests",
            "Participate in daily standups and code reviews",
            "Ship a capstone feature by end of internship",
        ],
        qualifications=["Personal projects on GitHub", "Basic knowledge of Node.js"],
        perks=["Certificate + LOR", "Pre-placement offer for top performers", "Flexible hours", "Mentorship"],
        ctc_breakdown=[
            {"component": "Monthly stipend", "amount": "₹15,000 - ₹25,000"},
            {"component": "Completion bonus", "amount": "₹10,000"},
        ],
        eligibility=[
            {"key": "grad", "type": "graduation_year", "label": "Graduating in 2026 or 2027", "value": [2026, 2027]},
            {"key": "skills", "type": "required_skills", "label": "Frontend basics", "value": ["JavaScript", "React"]},
        ],
        apply_questions=[Q_STIPEND_OK, Q_START_DATE, Q_PORTFOLIO, Q_WHY],
        posted_at=days_ago(1),
    ))

    # 7 — FlexJobs — Remote Frontend Developer (contract)
    jobs.append(job(
        slug="flexjobs-remote-frontend-contract-pixelforge",
        title="Remote Frontend Developer (Contract)",
        company="PixelForge Studio", company_logo="🎨",
        company_tagline="Vetted remote work, flexible teams",
        source_portal="FlexJobs", industry="Software / IT", job_type="contract",
        experience_level="mid", employment_mode="Remote", location="Remote (Global)",
        remote=True, openings=2, application_deadline="2026-10-18",
        salary_range="₹8 - 12 LPA (pro-rated)", ctc_min=lpa(8), ctc_max=lpa(12),
        experience_min_years=2.0, experience_max_years=6.0,
        required_skills=["React", "TypeScript", "CSS", "Figma", "Accessibility"],
        description="6-month renewable contract building accessible, pixel-perfect UIs for a design-led product team.",
        about_company="PixelForge Studio is a fully-remote design and engineering collective serving startups worldwide.",
        responsibilities=[
            "Translate Figma designs into accessible React components",
            "Maintain a shared component library",
            "Ensure WCAG 2.1 AA compliance",
        ],
        qualifications=["Design systems experience", "Storybook", "Animation libraries"],
        perks=["Fully remote", "Flexible timezone", "Contract renewal path"],
        ctc_breakdown=[{"component": "Monthly retainer", "amount": "₹80,000 - ₹1,00,000"}],
        eligibility=[
            {"key": "exp", "type": "min_experience", "label": "At least 2 years experience", "value": 2},
            {"key": "skills", "type": "required_skills", "label": "Frontend skills", "value": ["React", "CSS"]},
        ],
        apply_questions=[Q_PORTFOLIO, Q_EXPECTED_CTC, Q_START_DATE, Q_WORK_AUTH],
        posted_at=days_ago(5),
    ))

    # 8 — Upwork — Freelance Python Automation
    jobs.append(job(
        slug="upwork-freelance-python-automation-scriptbay",
        title="Freelance Python Automation Developer",
        company="ScriptBay Clients", company_logo="🐍",
        company_tagline="Freelance projects, delivered",
        source_portal="Upwork", industry="Software / IT", job_type="contract",
        experience_level="mid", employment_mode="Remote", location="Remote (Global)",
        remote=True, openings=5, application_deadline="2026-10-22",
        salary_range="₹2,000 - ₹4,000 /hour", ctc_min=lpa(4), ctc_max=lpa(10),
        experience_min_years=1.0, experience_max_years=None,
        required_skills=["Python", "Selenium", "BeautifulSoup", "APIs", "Pandas"],
        description="Project-based automation work — scrapers, integrations and data pipelines billed hourly.",
        about_company="A pool of vetted Upwork clients seeking dependable automation freelancers for short and long engagements.",
        responsibilities=[
            "Build web scrapers and data extraction scripts",
            "Integrate REST APIs and automate reports",
            "Deliver clean, documented code with tests",
        ],
        qualifications=["Playwright", "Cloud functions", "Prior Upwork history"],
        perks=["Set your own hours", "Long-term client potential"],
        ctc_breakdown=[{"component": "Hourly rate", "amount": "₹2,000 - ₹4,000"}],
        eligibility=[
            {"key": "skills", "type": "required_skills", "label": "Automation skills", "value": ["Python"]},
            {"key": "exp", "type": "min_experience", "label": "At least 1 year experience", "value": 1},
        ],
        apply_questions=[Q_PORTFOLIO, Q_START_DATE],
        posted_at=days_ago(7),
    ))

    # 9 — Wellfound — Founding Engineer (startup)
    jobs.append(job(
        slug="wellfound-founding-engineer-loopstack",
        title="Founding Software Engineer",
        company="LoopStack (Seed)", company_logo="🚀",
        company_tagline="Early-stage startup, huge ownership",
        source_portal="Wellfound", industry="Software / IT", job_type="full-time",
        experience_level="mid", employment_mode="Hybrid", location="Bengaluru, India",
        openings=1, application_deadline="2026-11-05",
        salary_range="₹16 - 24 LPA + equity", ctc_min=lpa(16), ctc_max=lpa(24),
        experience_min_years=3.0, experience_max_years=7.0,
        required_skills=["Python", "React", "AWS", "PostgreSQL", "System Design"],
        description="Be employee #4 at a seed-stage startup — build the product from scratch and shape engineering culture.",
        about_company="LoopStack is a seed-funded startup ($2M raised) building workflow automation for SMBs.",
        responsibilities=[
            "Build the MVP full stack, end to end",
            "Make architecture and tooling decisions",
            "Ship fast, talk to customers, iterate",
        ],
        qualifications=["Prior startup experience", "0-to-1 product experience"],
        perks=["Significant equity (0.5-1.5%)", "Direct founder access", "Flexible hours"],
        ctc_breakdown=[
            {"component": "Fixed base", "amount": "₹18 LPA"},
            {"component": "Equity (0.5-1.5%)", "amount": "meaningful ownership"},
        ],
        eligibility=[
            {"key": "exp", "type": "min_experience", "label": "At least 3 years experience", "value": 3},
            {"key": "skills", "type": "required_skills", "label": "Full stack skills", "value": ["Python", "React"]},
        ],
        apply_questions=[Q_NOTICE, Q_EXPECTED_CTC, Q_PORTFOLIO, Q_WHY, Q_RELOCATE],
        posted_at=days_ago(9),
    ))

    # 10 — Shine — QA Automation Engineer
    jobs.append(job(
        slug="shine-qa-automation-engineer-testlyne",
        title="QA Automation Engineer",
        company="Testlyne Solutions", company_logo="✅",
        company_tagline="Quality engineering specialists",
        source_portal="Shine.com", industry="Software / IT", job_type="full-time",
        experience_level="mid", employment_mode="In Office", location="Noida, India",
        openings=3, application_deadline="2026-10-28",
        salary_range="₹9 - 15 LPA", ctc_min=lpa(9), ctc_max=lpa(15),
        experience_min_years=2.0, experience_max_years=5.0,
        required_skills=["Selenium", "Java", "TestNG", "API Testing", "Jenkins"],
        description="Design and maintain automated test suites for enterprise web applications.",
        about_company="Testlyne Solutions provides QA and test automation services to banking and insurance clients.",
        responsibilities=[
            "Write and maintain Selenium + TestNG suites",
            "Automate API tests and integrate with CI",
            "Report defects and track quality metrics",
        ],
        qualifications=["Performance testing (JMeter)", "Mobile automation (Appium)"],
        perks=["Health insurance", "5-day work week", "Skill certification"],
        ctc_breakdown=[
            {"component": "Fixed base", "amount": "₹10 LPA"},
            {"component": "Variable", "amount": "up to ₹2 LPA"},
        ],
        eligibility=[
            {"key": "exp", "type": "min_experience", "label": "At least 2 years experience", "value": 2},
            {"key": "skills", "type": "required_skills", "label": "Automation skills", "value": ["Selenium"]},
            {"key": "backlogs", "type": "max_backlogs", "label": "At most 1 backlog", "value": 1},
        ],
        apply_questions=[Q_NOTICE, Q_CURRENT_CTC, Q_EXPECTED_CTC, Q_SHIFT],
        posted_at=days_ago(11),
    ))

    # 11 — TimesJobs — Java Backend Developer
    jobs.append(job(
        slug="timesjobs-java-backend-developer-corebank",
        title="Java Backend Developer",
        company="CoreBank Technologies", company_logo="🏦",
        company_tagline="Powering digital banking",
        source_portal="TimesJobs", industry="Banking / FinTech", job_type="full-time",
        experience_level="mid", employment_mode="In Office", location="Mumbai, India",
        openings=4, application_deadline="2026-11-08",
        salary_range="₹13 - 20 LPA", ctc_min=lpa(13), ctc_max=lpa(20),
        experience_min_years=3.0, experience_max_years=6.0,
        required_skills=["Java", "Spring Boot", "Microservices", "Oracle", "Kafka"],
        description="Build secure, high-throughput banking microservices for a top private bank.",
        about_company="CoreBank Technologies is the technology arm of a leading private bank, serving 40M+ customers.",
        responsibilities=[
            "Develop Spring Boot microservices",
            "Ensure security and compliance (PCI-DSS)",
            "Optimize Oracle database performance",
            "Integrate with core banking systems",
        ],
        qualifications=["Kubernetes", "Domain knowledge in payments", "Kafka Streams"],
        perks=["Provident fund + gratuity", "Health cover", "Annual bonus"],
        ctc_breakdown=[
            {"component": "Fixed base", "amount": "₹15 LPA"},
            {"component": "Annual bonus", "amount": "up to ₹5 LPA"},
        ],
        eligibility=[
            {"key": "exp", "type": "min_experience", "label": "At least 3 years experience", "value": 3},
            {"key": "skills", "type": "required_skills", "label": "Java stack", "value": ["Java", "Spring Boot"]},
            {"key": "cgpa", "type": "min_cgpa", "label": "Minimum CGPA 6.5", "value": 6.5},
        ],
        apply_questions=[Q_NOTICE, Q_CURRENT_CTC, Q_EXPECTED_CTC, Q_RELOCATE, Q_WORK_AUTH],
        posted_at=days_ago(13),
    ))

    # 12 — Freshersworld — Graduate Trainee Engineer
    jobs.append(job(
        slug="freshersworld-graduate-trainee-engineer-technova",
        title="Graduate Trainee Engineer",
        company="TechNova Systems", company_logo="🎓",
        company_tagline="Launch your engineering career",
        source_portal="Freshersworld", industry="Software / IT", job_type="full-time",
        experience_level="entry", employment_mode="In Office", location="Coimbatore, India",
        openings=25, application_deadline="2026-10-14",
        salary_range="₹4 - 6 LPA", ctc_min=lpa(4), ctc_max=lpa(6),
        experience_min_years=0.0, experience_max_years=1.0,
        required_skills=["C++", "DSA", "SQL", "OOP"],
        description="A 3-month training program for fresh graduates leading to a full-time software engineering role.",
        about_company="TechNova Systems hires and trains 200+ fresh graduates every year into product engineering teams.",
        responsibilities=[
            "Complete structured training in DSA and web development",
            "Work on a guided capstone project",
            "Join a product team after training",
        ],
        qualifications=["Coding competition participation", "Internship experience"],
        perks=["Paid training", "Guaranteed role on completion", "Hostel assistance"],
        ctc_breakdown=[
            {"component": "Training stipend", "amount": "₹20,000 /month"},
            {"component": "Post-training CTC", "amount": "₹4 - ₹6 LPA"},
        ],
        eligibility=[
            {"key": "grad", "type": "graduation_year", "label": "Graduating in 2026 or 2027", "value": [2026, 2027]},
            {"key": "cgpa", "type": "min_cgpa", "label": "Minimum CGPA 6.0", "value": 6.0},
            {"key": "backlogs", "type": "max_backlogs", "label": "No active backlogs", "value": 0},
        ],
        apply_questions=[Q_START_DATE, Q_RELOCATE, Q_WHY],
        posted_at=days_ago(2),
    ))

    # 13 — Cutshort — Product Engineer (tech startup)
    jobs.append(job(
        slug="cutshort-product-engineer-flowbit",
        title="Product Engineer (Full Stack)",
        company="Flowbit", company_logo="⚡",
        company_tagline="Curated tech hiring, no resumes needed",
        source_portal="Cutshort", industry="Software / IT", job_type="full-time",
        experience_level="mid", employment_mode="Remote", location="Remote (India)",
        remote=True, openings=2, application_deadline="2026-11-02",
        salary_range="₹15 - 25 LPA", ctc_min=lpa(15), ctc_max=lpa(25),
        experience_min_years=2.0, experience_max_years=5.0,
        required_skills=["TypeScript", "Next.js", "Node.js", "PostgreSQL", "GraphQL"],
        description="Own product features end to end at a fast-growing SaaS startup with a strong engineering culture.",
        about_company="Flowbit is a profitable B2B SaaS company with 3,000+ paying customers and a 15-person eng team.",
        responsibilities=[
            "Ship full-stack features with Next.js and Node",
            "Design GraphQL schemas and data models",
            "Own quality — tests, reviews and monitoring",
        ],
        qualifications=["SaaS product experience", "Payments integration", "Design sense"],
        perks=["Remote-first", "4-day work week trial", "Annual retreat", "ESOPs"],
        ctc_breakdown=[
            {"component": "Fixed base", "amount": "₹17 LPA"},
            {"component": "ESOPs", "amount": "₹5 LPA equivalent"},
            {"component": "Bonus", "amount": "up to ₹3 LPA"},
        ],
        eligibility=[
            {"key": "exp", "type": "min_experience", "label": "At least 2 years experience", "value": 2},
            {"key": "skills", "type": "required_skills", "label": "Modern web stack", "value": ["TypeScript", "Node.js"]},
        ],
        apply_questions=[Q_NOTICE, Q_EXPECTED_CTC, Q_PORTFOLIO, Q_WHY],
        posted_at=days_ago(4),
    ))

    # 14 — Instahyre — Senior Frontend Engineer
    jobs.append(job(
        slug="instahyre-senior-frontend-engineer-vantage",
        title="Senior Frontend Engineer",
        company="Vantage Commerce", company_logo="🛒",
        company_tagline="E-commerce at scale",
        source_portal="Instahyre", industry="E-commerce", job_type="full-time",
        experience_level="senior", employment_mode="Hybrid", location="Gurugram, India",
        openings=2, application_deadline="2026-11-10",
        salary_range="₹28 - 42 LPA", ctc_min=lpa(28), ctc_max=lpa(42),
        experience_min_years=5.0, experience_max_years=9.0,
        required_skills=["React", "TypeScript", "Redux", "Performance", "Micro-frontends"],
        description="Lead frontend architecture for a high-traffic e-commerce platform serving millions daily.",
        about_company="Vantage Commerce runs a top-5 Indian e-commerce marketplace with 50M+ monthly users.",
        responsibilities=[
            "Architect scalable micro-frontends",
            "Drive web performance and Core Web Vitals",
            "Mentor a team of 6 frontend engineers",
        ],
        qualifications=["Micro-frontend architecture", "SSR/edge rendering", "Team leadership"],
        perks=["Premium health cover", "Stock options", "Relocation support"],
        ctc_breakdown=[
            {"component": "Fixed base", "amount": "₹32 LPA"},
            {"component": "RSUs", "amount": "₹8 LPA/yr"},
            {"component": "Bonus", "amount": "up to ₹2 LPA"},
        ],
        eligibility=[
            {"key": "exp", "type": "min_experience", "label": "At least 5 years experience", "value": 5},
            {"key": "skills", "type": "required_skills", "label": "Frontend leadership skills", "value": ["React", "TypeScript"]},
            {"key": "cgpa", "type": "min_cgpa", "label": "Minimum CGPA 6.0", "value": 6.0},
        ],
        apply_questions=[Q_NOTICE, Q_CURRENT_CTC, Q_EXPECTED_CTC, Q_RELOCATE],
        posted_at=days_ago(6),
    ))

    # 15 — Apna — Customer Support Associate (entry / gray collar)
    jobs.append(job(
        slug="apna-customer-support-associate-quickcare",
        title="Customer Support Associate",
        company="QuickCare Services", company_logo="🎧",
        company_tagline="Local jobs, quick hiring",
        source_portal="Apna.co", industry="BPO / Support", job_type="full-time",
        experience_level="entry", employment_mode="In Office", location="Indore, India",
        openings=40, application_deadline="2026-10-16",
        salary_range="₹2.4 - 3.6 LPA", ctc_min=lpa(2.4), ctc_max=lpa(3.6),
        experience_min_years=0.0, experience_max_years=2.0,
        required_skills=["Communication", "Hindi", "English", "MS Office"],
        description="Handle inbound customer queries via calls and chat for a consumer services brand.",
        about_company="QuickCare Services operates customer support centers for D2C brands across India.",
        responsibilities=[
            "Resolve customer queries over phone and chat",
            "Maintain CRM records accurately",
            "Meet daily resolution and CSAT targets",
        ],
        qualifications=["Prior BPO experience", "Regional language fluency"],
        perks=["Incentives", "PF + ESI", "Cab for night shift"],
        ctc_breakdown=[
            {"component": "Fixed salary", "amount": "₹20,000 - ₹30,000 /month"},
            {"component": "Incentives", "amount": "up to ₹5,000 /month"},
        ],
        eligibility=[
            {"key": "skills", "type": "required_skills", "label": "Communication skills", "value": ["Communication"]},
        ],
        apply_questions=[Q_SHIFT, Q_START_DATE, Q_RELOCATE],
        posted_at=days_ago(1),
    ))

    # 16 — WorkIndia — Field Operations Executive (blue collar / ops)
    jobs.append(job(
        slug="workindia-field-ops-executive-swiftlogix",
        title="Field Operations Executive",
        company="SwiftLogix", company_logo="📦",
        company_tagline="Logistics that move India",
        source_portal="WorkIndia", industry="Logistics", job_type="full-time",
        experience_level="entry", employment_mode="In Office", location="Ahmedabad, India",
        openings=30, application_deadline="2026-10-19",
        salary_range="₹2.2 - 3.2 LPA", ctc_min=lpa(2.2), ctc_max=lpa(3.2),
        experience_min_years=0.0, experience_max_years=3.0,
        required_skills=["Logistics", "Communication", "Smartphone apps"],
        description="Coordinate last-mile deliveries and manage field staff in your assigned zone.",
        about_company="SwiftLogix is a fast-growing logistics company delivering 1M+ shipments monthly.",
        responsibilities=[
            "Coordinate daily delivery routes",
            "Manage and support field delivery staff",
            "Resolve on-ground delivery issues",
        ],
        qualifications=["Two-wheeler license", "Local area knowledge"],
        perks=["Fuel allowance", "PF + ESI", "Performance incentives"],
        ctc_breakdown=[
            {"component": "Fixed salary", "amount": "₹18,000 - ₹26,000 /month"},
            {"component": "Fuel + incentives", "amount": "up to ₹4,000 /month"},
        ],
        eligibility=[
            {"key": "skills", "type": "required_skills", "label": "Communication skills", "value": ["Communication"]},
        ],
        apply_questions=[Q_START_DATE, Q_RELOCATE, Q_SHIFT],
        posted_at=days_ago(3),
    ))

    # 17 — Hirist — Principal Backend Engineer (premium tech)
    jobs.append(job(
        slug="hirist-principal-backend-engineer-scaleon",
        title="Principal Backend Engineer",
        company="ScaleOn", company_logo="🔷",
        company_tagline="Premium engineering roles only",
        source_portal="Hirist", industry="Software / IT", job_type="full-time",
        experience_level="senior", employment_mode="Hybrid", location="Bengaluru, India",
        openings=1, application_deadline="2026-11-15",
        salary_range="₹45 - 65 LPA", ctc_min=lpa(45), ctc_max=lpa(65),
        experience_min_years=8.0, experience_max_years=14.0,
        required_skills=["Go", "Distributed Systems", "Kubernetes", "System Design", "PostgreSQL"],
        description="Set backend technical direction for a hyper-scale platform and mentor senior engineers.",
        about_company="ScaleOn operates infrastructure serving 500M+ API calls per day for enterprise clients.",
        responsibilities=[
            "Own architecture for distributed backend systems",
            "Lead design reviews and set technical standards",
            "Mentor staff and senior engineers",
        ],
        qualifications=["Large-scale distributed systems", "Open-source leadership", "Published talks/papers"],
        perks=["Top-of-market pay", "Large equity grant", "Sabbatical policy"],
        ctc_breakdown=[
            {"component": "Fixed base", "amount": "₹50 LPA"},
            {"component": "RSUs", "amount": "₹12 LPA/yr"},
            {"component": "Bonus", "amount": "up to ₹3 LPA"},
        ],
        eligibility=[
            {"key": "exp", "type": "min_experience", "label": "At least 8 years experience", "value": 8},
            {"key": "skills", "type": "required_skills", "label": "Backend + systems skills", "value": ["System Design"]},
        ],
        apply_questions=[Q_NOTICE, Q_CURRENT_CTC, Q_EXPECTED_CTC, Q_PORTFOLIO],
        posted_at=days_ago(10),
    ))

    # 18 — Hirect — Android Developer (chat-based startup hiring)
    jobs.append(job(
        slug="hirect-android-developer-mobio",
        title="Android Developer",
        company="Mobio Apps", company_logo="📱",
        company_tagline="Direct chat with hiring managers",
        source_portal="Hirect", industry="Mobile / Software", job_type="full-time",
        experience_level="mid", employment_mode="In Office", location="Kolkata, India",
        openings=2, application_deadline="2026-10-27",
        salary_range="₹8 - 14 LPA", ctc_min=lpa(8), ctc_max=lpa(14),
        experience_min_years=2.0, experience_max_years=5.0,
        required_skills=["Kotlin", "Android SDK", "Jetpack Compose", "REST APIs", "MVVM"],
        description="Build and ship consumer Android apps used by hundreds of thousands of users.",
        about_company="Mobio Apps is a mobile-first startup building consumer utility apps with 2M+ downloads.",
        responsibilities=[
            "Develop features with Kotlin + Jetpack Compose",
            "Integrate REST APIs and optimize app performance",
            "Publish and maintain apps on Play Store",
        ],
        qualifications=["Kotlin Coroutines", "CI for mobile", "Published apps"],
        perks=["Flexible hours", "Latest devices", "Health cover"],
        ctc_breakdown=[
            {"component": "Fixed base", "amount": "₹9 LPA"},
            {"component": "Bonus", "amount": "up to ₹2 LPA"},
        ],
        eligibility=[
            {"key": "exp", "type": "min_experience", "label": "At least 2 years experience", "value": 2},
            {"key": "skills", "type": "required_skills", "label": "Android skills", "value": ["Kotlin"]},
        ],
        apply_questions=[Q_NOTICE, Q_EXPECTED_CTC, Q_PORTFOLIO, Q_START_DATE],
        posted_at=days_ago(5),
    ))

    # 19 — HerKey — Women Returnee Software Engineer
    jobs.append(job(
        slug="herkey-returnee-software-engineer-inclusiv",
        title="Software Engineer - Returnship Program",
        company="Inclusiv Tech", company_logo="🌷",
        company_tagline="Careers and re-entry paths for women",
        source_portal="HerKey", industry="Software / IT", job_type="full-time",
        experience_level="mid", employment_mode="Remote", location="Remote (India)",
        remote=True, openings=5, application_deadline="2026-11-12",
        salary_range="₹10 - 18 LPA", ctc_min=lpa(10), ctc_max=lpa(18),
        experience_min_years=1.0, experience_max_years=8.0,
        required_skills=["Python", "JavaScript", "SQL", "Git"],
        description="A 6-month supported returnship for women re-entering tech, converting to full-time roles.",
        about_company="Inclusiv Tech runs award-winning returnship programs helping women restart careers in technology.",
        responsibilities=[
            "Ramp up with structured mentorship and training",
            "Contribute to real product features",
            "Transition to a permanent role on successful completion",
        ],
        qualifications=["Prior software experience", "Career break re-entry"],
        perks=["Flexible remote work", "Dedicated mentor", "Guaranteed conversion path", "Childcare support"],
        ctc_breakdown=[
            {"component": "Returnship stipend", "amount": "₹80,000 /month"},
            {"component": "Post-conversion CTC", "amount": "₹10 - ₹18 LPA"},
        ],
        eligibility=[
            {"key": "skills", "type": "required_skills", "label": "Programming skills", "value": ["Python"]},
            {"key": "exp", "type": "min_experience", "label": "At least 1 year prior experience", "value": 1},
        ],
        apply_questions=[Q_START_DATE, Q_EXPECTED_CTC, Q_WHY, Q_PORTFOLIO],
        posted_at=days_ago(7),
    ))

    # 20 — Jooble — Cloud Solutions Architect (aggregated)
    jobs.append(job(
        slug="jooble-cloud-solutions-architect-altitude",
        title="Cloud Solutions Architect",
        company="Altitude Cloud", company_logo="🏔️",
        company_tagline="Aggregated from thousands of sources",
        source_portal="Jooble", industry="Cloud / Infrastructure", job_type="full-time",
        experience_level="senior", employment_mode="Hybrid", location="Delhi, India",
        openings=2, application_deadline="2026-11-18",
        salary_range="₹30 - 45 LPA", ctc_min=lpa(30), ctc_max=lpa(45),
        experience_min_years=6.0, experience_max_years=12.0,
        required_skills=["AWS", "Azure", "Terraform", "Kubernetes", "Solution Design"],
        description="Design and present cloud architectures to enterprise clients and lead migration projects.",
        about_company="Altitude Cloud is a cloud consulting firm helping enterprises migrate and modernize on AWS and Azure.",
        responsibilities=[
            "Design multi-cloud reference architectures",
            "Lead client workshops and migrations",
            "Guide engineering teams on best practices",
        ],
        qualifications=["AWS/Azure architect certification", "Pre-sales experience", "Large migration projects"],
        perks=["Certification sponsorship", "Client travel", "Premium insurance"],
        ctc_breakdown=[
            {"component": "Fixed base", "amount": "₹34 LPA"},
            {"component": "Variable + bonus", "amount": "up to ₹9 LPA"},
        ],
        eligibility=[
            {"key": "exp", "type": "min_experience", "label": "At least 6 years experience", "value": 6},
            {"key": "skills", "type": "required_skills", "label": "Cloud skills", "value": ["AWS"]},
            {"key": "cgpa", "type": "min_cgpa", "label": "Minimum CGPA 6.0", "value": 6.0},
        ],
        apply_questions=[Q_NOTICE, Q_CURRENT_CTC, Q_EXPECTED_CTC, Q_RELOCATE, Q_WORK_AUTH],
        posted_at=days_ago(12),
    ))

    # 21 — LinkedIn — Data Analyst Intern (internship + PPO)
    jobs.append(job(
        slug="linkedin-data-analyst-intern-ppo-metricly",
        title="Data Analyst Intern (with PPO)",
        company="Metricly", company_logo="📈",
        company_tagline="Analytics for growth teams",
        source_portal="LinkedIn", industry="Data / Analytics", job_type="internship",
        experience_level="entry", employment_mode="Hybrid", location="Bengaluru, India",
        openings=6, application_deadline="2026-10-13",
        salary_range="₹30,000 /month", stipend_min=30000, stipend_max=30000,
        experience_min_years=0.0, experience_max_years=1.0,
        required_skills=["SQL", "Python", "Excel", "Tableau", "Statistics"],
        description="6-month analytics internship with a guaranteed pre-placement offer for strong performers.",
        about_company="Metricly builds analytics dashboards used by 500+ growth and product teams.",
        responsibilities=[
            "Write SQL queries and build dashboards",
            "Analyze product and marketing funnels",
            "Present insights to stakeholders",
        ],
        qualifications=["Coursework in statistics", "A/B testing knowledge"],
        perks=["₹30k/month stipend", "PPO for top performers", "Mentorship", "Certificate"],
        ctc_breakdown=[
            {"component": "Monthly stipend", "amount": "₹30,000"},
            {"component": "PPO CTC", "amount": "₹8 - ₹11 LPA"},
        ],
        eligibility=[
            {"key": "grad", "type": "graduation_year", "label": "Graduating in 2026 or 2027", "value": [2026, 2027]},
            {"key": "cgpa", "type": "min_cgpa", "label": "Minimum CGPA 7.0", "value": 7.0},
            {"key": "skills", "type": "required_skills", "label": "Analytics skills", "value": ["SQL", "Python"]},
        ],
        apply_questions=[Q_STIPEND_OK, Q_START_DATE, Q_PORTFOLIO, Q_WHY],
        posted_at=days_ago(1),
    ))

    # 22 — Naukri — Part-time Technical Content Writer
    jobs.append(job(
        slug="naukri-part-time-technical-writer-docuwise",
        title="Technical Content Writer (Part-time)",
        company="DocuWise", company_logo="✍️",
        company_tagline="Docs that developers love",
        source_portal="Naukri.com", industry="Content / Media", job_type="part-time",
        experience_level="entry", employment_mode="Remote", location="Remote (India)",
        remote=True, openings=3, application_deadline="2026-10-24",
        salary_range="₹3 - 5 LPA (pro-rated)", ctc_min=lpa(3), ctc_max=lpa(5),
        experience_min_years=1.0, experience_max_years=4.0,
        required_skills=["Technical Writing", "Markdown", "APIs", "Git"],
        description="Write developer documentation, tutorials and API references — 20 hours/week, fully remote.",
        about_company="DocuWise creates documentation for developer-tool companies worldwide.",
        responsibilities=[
            "Write clear API docs and tutorials",
            "Collaborate with engineers to verify accuracy",
            "Maintain docs in Markdown + Git",
        ],
        qualifications=["Prior dev-docs experience", "Basic coding ability"],
        perks=["Fully remote", "Flexible 20 hrs/week", "Byline credit"],
        ctc_breakdown=[{"component": "Part-time retainer", "amount": "₹25,000 - ₹40,000 /month"}],
        eligibility=[
            {"key": "skills", "type": "required_skills", "label": "Writing skills", "value": ["Technical Writing"]},
        ],
        apply_questions=[Q_PORTFOLIO, Q_START_DATE, Q_EXPECTED_CTC],
        posted_at=days_ago(9),
    ))

    # 23 — Foundit — NGO Tech Volunteer (volunteer)
    jobs.append(job(
        slug="foundit-tech-volunteer-codeforgood",
        title="Volunteer Software Developer",
        company="Code For Good Foundation", company_logo="💚",
        company_tagline="Tech for social impact",
        source_portal="Foundit", industry="Non-profit", job_type="volunteer",
        experience_level="entry", employment_mode="Remote", location="Remote (India)",
        remote=True, openings=15, application_deadline="2026-11-20",
        salary_range="Unpaid (certificate + impact)", ctc_min=0, ctc_max=0,
        experience_min_years=0.0, experience_max_years=None,
        required_skills=["JavaScript", "React", "Git"],
        description="Volunteer a few hours a week to build tools for grassroots NGOs and earn a recognized certificate.",
        about_company="Code For Good Foundation connects tech volunteers with non-profits needing digital tools.",
        responsibilities=[
            "Build and maintain small web tools for NGOs",
            "Collaborate async with a volunteer team",
        ],
        qualifications=["Passion for social impact", "Any coding background"],
        perks=["Volunteering certificate", "LOR", "Portfolio projects", "Community"],
        ctc_breakdown=[{"component": "Compensation", "amount": "Unpaid volunteer role"}],
        eligibility=[
            {"key": "skills", "type": "required_skills", "label": "Basic coding skills", "value": ["Git"]},
        ],
        apply_questions=[Q_WHY, Q_START_DATE, Q_PORTFOLIO],
        posted_at=days_ago(14),
    ))

    # 24 — Wellfound — Growth Product Manager (non-eng, tough eligibility)
    jobs.append(job(
        slug="wellfound-growth-product-manager-zenith",
        title="Growth Product Manager",
        company="Zenith (Series A)", company_logo="🎯",
        company_tagline="Startup jobs, tech roles",
        source_portal="Wellfound", industry="Software / IT", job_type="full-time",
        experience_level="mid", employment_mode="Hybrid", location="Bengaluru, India",
        openings=1, application_deadline="2026-11-06",
        salary_range="₹25 - 38 LPA + equity", ctc_min=lpa(25), ctc_max=lpa(38),
        experience_min_years=4.0, experience_max_years=8.0,
        required_skills=["Product Management", "Analytics", "SQL", "A/B Testing", "Growth"],
        description="Own the growth funnel end to end — experiments, analytics and cross-functional execution.",
        about_company="Zenith is a Series-A consumer startup ($8M raised) with 1M+ users and strong growth.",
        responsibilities=[
            "Own activation, retention and referral metrics",
            "Run and analyze growth experiments",
            "Work across engineering, design and marketing",
        ],
        qualifications=["Prior growth PM role", "Consumer product experience", "Strong SQL"],
        perks=["Equity", "Fast growth", "Direct leadership access"],
        ctc_breakdown=[
            {"component": "Fixed base", "amount": "₹28 LPA"},
            {"component": "Equity", "amount": "₹7 LPA equivalent"},
            {"component": "Bonus", "amount": "up to ₹3 LPA"},
        ],
        eligibility=[
            {"key": "exp", "type": "min_experience", "label": "At least 4 years experience", "value": 4},
            {"key": "skills", "type": "required_skills", "label": "PM + growth skills", "value": ["Product Management", "SQL"]},
            {"key": "cgpa", "type": "min_cgpa", "label": "Minimum CGPA 7.5", "value": 7.5},
        ],
        apply_questions=[Q_NOTICE, Q_CURRENT_CTC, Q_EXPECTED_CTC, Q_WHY, Q_RELOCATE],
        posted_at=days_ago(8),
    ))

    return jobs


async def sync_jobs() -> dict:
    rows = build_jobs()
    print(f"[INFO] Built {len(rows)} job postings.")
    created = 0
    updated = 0

    async with async_session_factory() as session:
        existing_rows = (await session.execute(select(JobListing))).scalars().all()
        by_slug = {r.slug: r for r in existing_rows if r.slug}

        for payload in rows:
            slug = payload["slug"]
            row = by_slug.get(slug)
            if row is None:
                row = JobListing(slug=slug)
                session.add(row)
                created += 1
            else:
                updated += 1
            for field in FIELDS:
                setattr(row, field, payload[field])

        await session.commit()

    print(f"[SUCCESS] Synced jobs: {created} created, {updated} updated.")
    return {"total": len(rows), "created": created, "updated": updated}


async def main():
    await init_db()
    await sync_jobs()


if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(0)
