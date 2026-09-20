"""Seeds the Events board with a spread of distinct event formats hosted by
major technology employers.

Idempotent: rows are matched on ``slug`` so re-running updates in place and
keeps existing registrations (which reference event ids) intact.

Run with:  python seed_events.py
"""

import asyncio
import datetime
import sys

from sqlalchemy import select

from app.db.session import async_session_factory, init_db
from app.models.models import Event

FIELDS = (
    "title", "description", "event_date", "end_date", "location", "venue", "city",
    "event_url", "capacity", "host_company", "host_domain", "host_logo", "host_tagline",
    "event_type", "mode", "tags", "timezone_label", "duration_minutes",
    "registration_deadline", "price", "currency", "is_certified", "about", "agenda",
    "speakers", "prizes", "perks", "eligibility", "registration_questions",
    "is_active", "is_featured",
)

_now = datetime.datetime.now(datetime.timezone.utc)


def in_days(n: int, hour: int = 10, minute: int = 0) -> datetime.datetime:
    d = _now + datetime.timedelta(days=n)
    return d.replace(hour=hour, minute=minute, second=0, microsecond=0)


# ─── Reusable registration questions ─────────────────────────────
# Same contract as JobListing.apply_questions:
#   {key, label, type, required, options?, placeholder?, help?}

Q_TEAM_NAME = {
    "key": "team_name", "label": "Team name", "type": "text", "required": True,
    "placeholder": "e.g. Byte Crusaders", "help": "Solo participants can use their own name.",
}
Q_TEAM_SIZE = {
    "key": "team_size", "label": "Team size", "type": "select", "required": True,
    "options": ["Participating solo", "2 members", "3 members", "4 members"],
}
Q_TRACK = {
    "key": "track", "label": "Preferred problem track", "type": "select", "required": True,
    "options": ["AI / Machine Learning", "Cloud & DevOps", "Web & Mobile", "Data Engineering", "Open Innovation"],
}
Q_REPO = {
    "key": "repo_url", "label": "GitHub profile or a project repo", "type": "url",
    "required": False, "placeholder": "https://github.com/your-handle",
}
Q_PRIMARY_LANGUAGE = {
    "key": "primary_language", "label": "Primary programming language", "type": "select",
    "required": True, "options": ["Python", "Java", "C++", "JavaScript / TypeScript", "Go", "Other"],
}
Q_SKILL_LEVEL = {
    "key": "skill_level", "label": "How would you rate your current level?", "type": "select",
    "required": True, "options": ["Beginner", "Intermediate", "Advanced"],
}
Q_TOPICS = {
    "key": "topics_of_interest", "label": "Topics you most want covered", "type": "multiselect",
    "required": False,
    "options": ["System design", "Data structures", "Behavioural rounds", "Salary negotiation",
                "Resume review", "Career switching"],
}
Q_QUESTION_FOR_PANEL = {
    "key": "question_for_panel", "label": "A question you'd like the panel to answer",
    "type": "textarea", "required": False, "placeholder": "Ask anything about the role, team or hiring bar...",
}
Q_ROLES = {
    "key": "roles_of_interest", "label": "Roles you're targeting", "type": "multiselect",
    "required": True,
    "options": ["Software Engineer", "Data Scientist", "ML Engineer", "Product Manager",
                "DevOps / SRE", "Business Analyst", "UX Designer"],
}
Q_NOTICE = {
    "key": "availability", "label": "Earliest date you can start", "type": "date", "required": False,
}
Q_LAPTOP = {
    "key": "brings_laptop", "label": "Will you bring your own laptop?", "type": "boolean",
    "required": True, "help": "Hands-on labs need a machine with admin rights.",
}
Q_PRIOR_CERT = {
    "key": "prior_certification", "label": "Do you already hold a related certification?",
    "type": "boolean", "required": False,
}
Q_TARGET_COMPANIES = {
    "key": "target_companies", "label": "Companies you're preparing for", "type": "text",
    "required": False, "placeholder": "e.g. Google, Zoho, Freshworks",
}
Q_INTERVIEW_SLOT = {
    "key": "interview_slot", "label": "Preferred mock interview slot", "type": "select",
    "required": True, "options": ["09:00 - 10:00", "10:30 - 11:30", "14:00 - 15:00", "16:00 - 17:00"],
}
Q_PORTFOLIO_REVIEW = {
    "key": "wants_portfolio_review", "label": "Would you like a portfolio review slot?",
    "type": "boolean", "required": False,
}
Q_IDEA_SUMMARY = {
    "key": "idea_summary", "label": "Summarise the idea you want to build", "type": "textarea",
    "required": True, "placeholder": "What problem does it solve, and for whom?",
    "help": "Two or three sentences is plenty at this stage.",
}
Q_DOMAIN = {
    "key": "problem_domain", "label": "Problem domain", "type": "select", "required": True,
    "options": ["Healthcare", "Education", "Fintech", "Sustainability", "Agriculture", "Accessibility"],
}
Q_ACCOMMODATION = {
    "key": "needs_accommodation", "label": "Do you need travel or stay assistance?",
    "type": "boolean", "required": False,
}
Q_COMMUNITY = {
    "key": "community_group", "label": "Which community group do you identify with?",
    "type": "select", "required": False,
    "options": ["Women in Tech", "First-generation graduate", "Person with disability",
                "Rural / Tier-3 background", "Prefer not to say"],
}
Q_CLOUD_EXPERIENCE = {
    "key": "cloud_experience", "label": "Months of hands-on cloud experience", "type": "number",
    "required": False, "placeholder": "0",
}


def event(**kw) -> dict:
    """Fill every optional field so the FIELDS sync never hits a KeyError."""
    kw.setdefault("description", "")
    kw.setdefault("end_date", None)
    kw.setdefault("location", "")
    kw.setdefault("venue", "")
    kw.setdefault("city", "")
    kw.setdefault("event_url", "")
    kw.setdefault("capacity", None)
    kw.setdefault("host_company", "")
    kw.setdefault("host_domain", "")
    kw.setdefault("host_logo", "📅")
    kw.setdefault("host_tagline", "")
    kw.setdefault("event_type", "webinar")
    kw.setdefault("mode", "Online")
    kw.setdefault("tags", [])
    kw.setdefault("timezone_label", "IST")
    kw.setdefault("duration_minutes", 90)
    kw.setdefault("registration_deadline", None)
    kw.setdefault("price", 0)
    kw.setdefault("currency", "INR")
    kw.setdefault("is_certified", False)
    kw.setdefault("about", "")
    kw.setdefault("agenda", [])
    kw.setdefault("speakers", [])
    kw.setdefault("prizes", [])
    kw.setdefault("perks", [])
    kw.setdefault("eligibility", [])
    kw.setdefault("registration_questions", [])
    kw.setdefault("is_active", True)
    kw.setdefault("is_featured", False)
    return kw


def build_events() -> list[dict]:
    rows: list[dict] = []

    # 1 ── Hackathon
    rows.append(event(
        slug="google-solution-challenge-hackathon-2026",
        title="Google Solution Challenge — 36 Hour Build Sprint",
        host_company="Google",
        host_domain="google.com",
        host_logo="🟦",
        host_tagline="Developer Student Clubs",
        event_type="hackathon",
        mode="Hybrid",
        description="Build a working solution to a UN Sustainable Development Goal in 36 hours, with Google engineers mentoring each team through the night.",
        about=(
            "The Solution Challenge invites student developers to pick one of the 17 UN Sustainable "
            "Development Goals and ship something real against it in 36 hours. You will scope a problem "
            "on Friday evening, build through Saturday with a Google mentor assigned to your team, and "
            "demo a working prototype to a judging panel on Sunday afternoon.\n\n"
            "Teams get Google Cloud credits, access to Gemini API keys for the weekend, and a mentor "
            "check-in every six hours. The emphasis is on a demoable slice rather than a finished "
            "product — judges score problem clarity, technical execution and the honesty of your demo."
        ),
        event_date=in_days(21, 18, 0),
        end_date=in_days(23, 17, 0),
        duration_minutes=2100,
        location="Google Bengaluru + Online",
        venue="Google RMZ Infinity, Old Madras Road",
        city="Bengaluru",
        capacity=400,
        registration_deadline=in_days(17, 23, 59),
        is_featured=True,
        is_certified=True,
        tags=["Sustainability", "Google Cloud", "Gemini API", "Team event"],
        agenda=[
            {"time": "Fri 6:00 pm", "title": "Kickoff & problem statements", "detail": "SDG tracks revealed, team formation desk opens."},
            {"time": "Fri 8:00 pm", "title": "Mentor matching", "detail": "Each team is paired with a Google engineer."},
            {"time": "Sat 12:00 pm", "title": "Checkpoint one", "detail": "Architecture review and scope trimming."},
            {"time": "Sat 9:00 pm", "title": "Checkpoint two", "detail": "Demo path lock-in — no new features after this."},
            {"time": "Sun 1:00 pm", "title": "Judging round", "detail": "Six minute demo plus four minutes of questions."},
            {"time": "Sun 4:00 pm", "title": "Results & closing", "detail": "Winners announced, offers to top teams."},
        ],
        speakers=[
            {"name": "Ananya Rao", "title": "Staff Software Engineer", "company": "Google"},
            {"name": "Vikram Shetty", "title": "Developer Relations Lead", "company": "Google"},
        ],
        prizes=[
            "Winning team: ₹2,00,000 and a fast-tracked interview loop",
            "Runner up: ₹1,00,000 and Google Cloud credits worth $5,000",
            "Best solo build: ₹25,000 and a Pixel device",
            "All finalists receive a mentor-signed letter of recommendation",
        ],
        perks=["Meals and night snacks on site", "Google Cloud credits", "Swag kit", "Certificate of participation"],
        eligibility=[
            "Open to students currently enrolled in an undergraduate or postgraduate programme",
            "Teams of one to four; cross-college teams allowed",
            "Each participant may join only one team",
        ],
        registration_questions=[Q_TEAM_NAME, Q_TEAM_SIZE, Q_TRACK, Q_REPO, Q_ACCOMMODATION],
    ))

    # 2 ── Career fair
    rows.append(event(
        slug="microsoft-early-careers-fair-2026",
        title="Microsoft Early Careers Fair 2026",
        host_company="Microsoft",
        host_domain="microsoft.com",
        host_logo="🟨",
        host_tagline="Campus Hiring",
        event_type="career_fair",
        mode="Online",
        description="Meet recruiters and engineering managers from Azure, Microsoft 365 and the India Development Centre across a full day of open booths.",
        about=(
            "A single-day virtual fair where Microsoft's India engineering and product teams open "
            "booths for final-year students and recent graduates. Each booth runs a rolling 20 minute "
            "session: a short team overview, then open questions with the engineers who actually do the "
            "interviews.\n\n"
            "Bring a current resume. Recruiters can flag strong conversations directly into the campus "
            "hiring pipeline, and shortlisted attendees hear back within two weeks."
        ),
        event_date=in_days(12, 10, 0),
        end_date=in_days(12, 17, 30),
        duration_minutes=450,
        location="Virtual — Microsoft Teams",
        city="Remote",
        capacity=2000,
        registration_deadline=in_days(10, 23, 59),
        is_featured=True,
        tags=["Hiring", "Azure", "Graduate roles", "Resume review"],
        agenda=[
            {"time": "10:00 am", "title": "Opening keynote", "detail": "How Microsoft India hires early-career engineers."},
            {"time": "11:00 am", "title": "Booth rounds begin", "detail": "Azure, Microsoft 365, Security, Developer Division."},
            {"time": "2:00 pm", "title": "Resume clinic", "detail": "15 minute one-on-one slots with recruiters."},
            {"time": "4:00 pm", "title": "Hiring bar AMA", "detail": "What separates a hire from a no-hire."},
        ],
        speakers=[
            {"name": "Priya Menon", "title": "University Recruiting Lead", "company": "Microsoft"},
            {"name": "Rahul Iyer", "title": "Principal Engineering Manager, Azure", "company": "Microsoft"},
        ],
        perks=["Direct recruiter contact", "Resume feedback", "Referral consideration"],
        eligibility=[
            "Graduating in 2026 or graduated within the last 18 months",
            "Open to all engineering and computer science disciplines",
        ],
        registration_questions=[Q_ROLES, Q_NOTICE, Q_TARGET_COMPANIES],
    ))

    # 3 ── Technical webinar
    rows.append(event(
        slug="amazon-system-design-webinar",
        title="Scaling to a Billion Requests — An Amazon System Design Webinar",
        host_company="Amazon",
        host_domain="amazon.com",
        host_logo="🟧",
        host_tagline="Amazon Web Services",
        event_type="webinar",
        mode="Online",
        description="A senior AWS engineer walks through the real design tradeoffs behind a high-throughput service, then takes live design questions.",
        about=(
            "Most system design content stops at boxes and arrows. This session goes a layer deeper: "
            "an AWS principal engineer takes a single service and walks through the decisions that "
            "actually mattered — where they chose consistency over availability, which caches earned "
            "their complexity, and what they got wrong the first time.\n\n"
            "The last 30 minutes are live design questions from attendees, worked through on a shared "
            "canvas. Recording is shared with everyone who registers."
        ),
        event_date=in_days(6, 19, 0),
        duration_minutes=90,
        location="Virtual — Zoom",
        city="Remote",
        capacity=1500,
        tags=["System design", "AWS", "Scalability", "Interview prep"],
        agenda=[
            {"time": "7:00 pm", "title": "The problem", "detail": "Requirements, traffic shape and failure budget."},
            {"time": "7:20 pm", "title": "Design walkthrough", "detail": "Storage, caching and fan-out decisions."},
            {"time": "8:00 pm", "title": "What we got wrong", "detail": "Two rewrites and why they happened."},
            {"time": "8:15 pm", "title": "Live Q&A", "detail": "Attendee design problems on a shared canvas."},
        ],
        speakers=[{"name": "Sandeep Krishnan", "title": "Principal Engineer", "company": "Amazon Web Services"}],
        perks=["Session recording", "Design template pack"],
        eligibility=["Comfortable with basic distributed systems vocabulary", "Open to students and working engineers"],
        registration_questions=[Q_SKILL_LEVEL, Q_QUESTION_FOR_PANEL],
    ))

    # 4 ── Hands-on workshop
    rows.append(event(
        slug="nvidia-deep-learning-workshop",
        title="NVIDIA Deep Learning Institute — Hands-On CUDA Workshop",
        host_company="NVIDIA",
        host_domain="nvidia.com",
        host_logo="🟩",
        host_tagline="Deep Learning Institute",
        event_type="workshop",
        mode="In Person",
        description="A full-day lab where you profile and optimise real GPU workloads on provided hardware, ending in a graded assessment.",
        about=(
            "An instructor-led lab day from the NVIDIA Deep Learning Institute. You work on provisioned "
            "GPU instances, starting from a deliberately slow training loop and profiling your way to a "
            "measurable speedup. Everything is hands-on keyboard time — there is no lecture block longer "
            "than 20 minutes.\n\n"
            "The day closes with a graded assessment. Passing earns an NVIDIA DLI certificate, which is "
            "recognised in ML infrastructure hiring."
        ),
        event_date=in_days(28, 9, 30),
        end_date=in_days(28, 18, 0),
        duration_minutes=510,
        location="NVIDIA Pune Campus",
        venue="NVIDIA Graphics, Rajiv Gandhi Infotech Park, Hinjawadi",
        city="Pune",
        capacity=60,
        registration_deadline=in_days(24, 23, 59),
        price=1500,
        is_certified=True,
        tags=["CUDA", "GPU", "Deep learning", "Certification"],
        agenda=[
            {"time": "9:30 am", "title": "Environment setup", "detail": "GPU instances assigned, toolchain verified."},
            {"time": "10:30 am", "title": "Profiling fundamentals", "detail": "Finding the real bottleneck with Nsight."},
            {"time": "1:30 pm", "title": "Optimisation lab", "detail": "Memory coalescing and kernel fusion."},
            {"time": "4:30 pm", "title": "Graded assessment", "detail": "Hit the target speedup to certify."},
        ],
        speakers=[{"name": "Dr. Meera Subramanian", "title": "DLI Certified Instructor", "company": "NVIDIA"}],
        perks=["GPU instance for the day", "DLI certificate on passing", "Lunch provided", "Course notebooks to keep"],
        eligibility=[
            "Working knowledge of C++ or Python",
            "Prior exposure to neural network training is helpful but not required",
            "You must bring a laptop capable of SSH and a modern browser",
        ],
        registration_questions=[Q_LAPTOP, Q_PRIMARY_LANGUAGE, Q_SKILL_LEVEL, Q_PRIOR_CERT],
    ))

    # 5 ── Competitive programming contest
    rows.append(event(
        slug="meta-hacker-cup-practice-round",
        title="Meta Hacker Cup — Guided Practice Round",
        host_company="Meta",
        host_domain="meta.com",
        host_logo="🟦",
        host_tagline="Engineering",
        event_type="contest",
        mode="Online",
        description="A timed three-hour algorithmic contest using past Hacker Cup problems, followed by an editorial walkthrough from a finalist.",
        about=(
            "A practice contest built from previous Meta Hacker Cup rounds, run under real contest "
            "conditions: three hours, five problems in ascending difficulty, live scoreboard with penalty "
            "time.\n\n"
            "Immediately afterwards a former Hacker Cup finalist walks through the intended solutions, "
            "including the observations that make the hard problems tractable. Your submissions stay "
            "available afterwards so you can compare against the editorial."
        ),
        event_date=in_days(9, 20, 0),
        end_date=in_days(9, 23, 30),
        duration_minutes=210,
        location="Virtual — online judge",
        city="Remote",
        capacity=3000,
        tags=["Competitive programming", "Algorithms", "Contest", "Scoreboard"],
        agenda=[
            {"time": "8:00 pm", "title": "Contest window opens", "detail": "Five problems, three hours, live scoreboard."},
            {"time": "11:00 pm", "title": "Contest closes", "detail": "Final standings frozen."},
            {"time": "11:10 pm", "title": "Editorial walkthrough", "detail": "Intended solutions problem by problem."},
        ],
        speakers=[{"name": "Arjun Bhatt", "title": "Software Engineer & Hacker Cup Finalist", "company": "Meta"}],
        prizes=["Top 10 receive Meta swag kits", "Top 50 get a detailed code review of their submissions"],
        perks=["Editorial access", "Submissions retained for review"],
        eligibility=["Open to everyone", "Any language supported by the judge"],
        registration_questions=[Q_PRIMARY_LANGUAGE, Q_SKILL_LEVEL],
    ))

    # 6 ── Bootcamp
    rows.append(event(
        slug="ibm-cloud-devops-bootcamp",
        title="IBM Cloud & DevOps Bootcamp — Four Evening Intensive",
        host_company="IBM",
        host_domain="ibm.com",
        host_logo="🟦",
        host_tagline="IBM SkillsBuild",
        event_type="bootcamp",
        mode="Online",
        description="Four consecutive evenings taking a single application from local code to a monitored production deployment on Kubernetes.",
        about=(
            "A four-evening bootcamp built around one continuous thread: you start with a plain "
            "application and finish with it containerised, deployed to Kubernetes, wired to a CI pipeline "
            "and reporting metrics.\n\n"
            "Each evening ends with a hands-on task you must complete before the next session, because "
            "the next session builds directly on it. Attendees who finish all four tasks receive an IBM "
            "SkillsBuild credential."
        ),
        event_date=in_days(15, 19, 0),
        end_date=in_days(18, 21, 30),
        duration_minutes=150,
        location="Virtual — IBM Cloud labs",
        city="Remote",
        capacity=300,
        registration_deadline=in_days(13, 23, 59),
        is_certified=True,
        tags=["Docker", "Kubernetes", "CI/CD", "Observability", "Multi-day"],
        agenda=[
            {"time": "Day 1", "title": "Containerise it", "detail": "Dockerfile, layer caching, image slimming."},
            {"time": "Day 2", "title": "Ship it", "detail": "Kubernetes deployments, services and config."},
            {"time": "Day 3", "title": "Automate it", "detail": "Pipeline from commit to cluster."},
            {"time": "Day 4", "title": "Watch it", "detail": "Metrics, logs and a practical alerting setup."},
        ],
        speakers=[
            {"name": "Nikhil Verma", "title": "Senior DevOps Architect", "company": "IBM"},
            {"name": "Fatima Sheikh", "title": "Site Reliability Engineer", "company": "IBM"},
        ],
        perks=["IBM Cloud lab access", "SkillsBuild credential", "Recordings for 90 days"],
        eligibility=[
            "Comfortable with the command line and basic Git",
            "You must be able to attend all four evenings",
        ],
        registration_questions=[Q_CLOUD_EXPERIENCE, Q_SKILL_LEVEL, Q_LAPTOP],
    ))

    # 7 ── Tech talk
    rows.append(event(
        slug="netflix-streaming-architecture-tech-talk",
        title="Inside Netflix Streaming — An Engineering Tech Talk",
        host_company="Netflix",
        host_domain="netflix.com",
        host_logo="🟥",
        host_tagline="Engineering Blog Live",
        event_type="tech_talk",
        mode="Online",
        description="How Netflix delivers video at scale: adaptive bitrate, edge caching and the chaos engineering practices that keep it up.",
        about=(
            "A one-hour engineering talk on what actually happens between pressing play and seeing a "
            "frame. The speaker covers adaptive bitrate selection, how the Open Connect edge decides what "
            "to cache where, and the failure-injection practices that keep the service resilient.\n\n"
            "Aimed at engineers who are curious about large-scale media delivery. Slides and references "
            "are shared afterwards."
        ),
        event_date=in_days(4, 20, 30),
        duration_minutes=60,
        location="Virtual — YouTube Live",
        city="Remote",
        tags=["Streaming", "CDN", "Chaos engineering", "Architecture"],
        agenda=[
            {"time": "8:30 pm", "title": "Press play", "detail": "The request path end to end."},
            {"time": "8:55 pm", "title": "Edge caching", "detail": "What gets cached where, and why."},
            {"time": "9:15 pm", "title": "Breaking things on purpose", "detail": "Failure injection in production."},
        ],
        speakers=[{"name": "Daniel Osei", "title": "Senior Software Engineer, Playback", "company": "Netflix"}],
        perks=["Slides and reading list"],
        eligibility=["Open to all — no prerequisites"],
        registration_questions=[Q_QUESTION_FOR_PANEL],
    ))

    # 8 ── Ask Me Anything
    rows.append(event(
        slug="adobe-design-engineering-ama",
        title="Adobe Design & Engineering AMA — Ask the Hiring Panel",
        host_company="Adobe",
        host_domain="adobe.com",
        host_logo="🟥",
        host_tagline="Adobe India",
        event_type="ama",
        mode="Online",
        description="An unscripted hour with Adobe interviewers answering submitted questions about portfolios, hiring bars and career paths.",
        about=(
            "No slides. A panel of Adobe engineers and designers who conduct interviews answer questions "
            "submitted during registration, prioritising the ones asked most often.\n\n"
            "Typical ground covered: what makes a portfolio memorable versus forgettable, how the design "
            "and engineering tracks differ in practice, and the honest reasons strong candidates get "
            "rejected. Submit your question when you register so the panel can prepare."
        ),
        event_date=in_days(8, 18, 0),
        duration_minutes=75,
        location="Virtual — Adobe Connect",
        city="Remote",
        capacity=800,
        tags=["Career advice", "Portfolio", "Hiring", "Design"],
        agenda=[
            {"time": "6:00 pm", "title": "Panel introductions", "detail": "Who's answering and what they interview for."},
            {"time": "6:10 pm", "title": "Top submitted questions", "detail": "The ones asked most during registration."},
            {"time": "6:50 pm", "title": "Open floor", "detail": "Live questions from the chat."},
        ],
        speakers=[
            {"name": "Sneha Kulkarni", "title": "Design Manager", "company": "Adobe"},
            {"name": "Rohit Agarwal", "title": "Computer Scientist", "company": "Adobe"},
        ],
        perks=["Answers compiled and emailed afterwards"],
        eligibility=["Open to students and early-career professionals"],
        registration_questions=[Q_QUESTION_FOR_PANEL, Q_PORTFOLIO_REVIEW, Q_TOPICS],
    ))

    # 9 ── Diversity programme
    rows.append(event(
        slug="salesforce-women-in-tech-summit",
        title="Salesforce Women in Tech Summit — Pathways Into Product",
        host_company="Salesforce",
        host_domain="salesforce.com",
        host_logo="🟦",
        host_tagline="Equality Groups",
        event_type="diversity",
        mode="Hybrid",
        description="A half-day summit pairing attendees with Salesforce mentors, plus workshops on negotiation and technical leadership.",
        about=(
            "A half-day programme for women and non-binary students entering technology careers. The "
            "focus is practical rather than motivational: a negotiation workshop with scripts you can "
            "actually use, a session on building technical credibility early, and structured mentor "
            "matching.\n\n"
            "Every attendee leaves matched with a Salesforce mentor for a three-month cycle of monthly "
            "conversations. Travel assistance is available for students outside Hyderabad."
        ),
        event_date=in_days(19, 9, 0),
        end_date=in_days(19, 14, 0),
        duration_minutes=300,
        location="Salesforce Hyderabad + Online",
        venue="Salesforce Tower, HITEC City",
        city="Hyderabad",
        capacity=250,
        registration_deadline=in_days(15, 23, 59),
        is_featured=True,
        tags=["Women in tech", "Mentorship", "Negotiation", "Leadership"],
        agenda=[
            {"time": "9:00 am", "title": "Opening panel", "detail": "Four non-linear career paths into product."},
            {"time": "10:15 am", "title": "Negotiation workshop", "detail": "Scripts, anchoring and when to walk."},
            {"time": "11:45 am", "title": "Technical credibility", "detail": "Being heard in engineering rooms."},
            {"time": "1:00 pm", "title": "Mentor matching", "detail": "Three-month mentorship pairings assigned."},
        ],
        speakers=[
            {"name": "Lakshmi Narayan", "title": "VP of Engineering", "company": "Salesforce"},
            {"name": "Aisha Qureshi", "title": "Director of Product Management", "company": "Salesforce"},
        ],
        perks=["Three-month mentorship", "Travel assistance available", "Lunch provided", "Summit certificate"],
        eligibility=[
            "Open to women and non-binary students and early-career professionals",
            "Undergraduate, postgraduate or up to three years of experience",
        ],
        registration_questions=[Q_COMMUNITY, Q_ROLES, Q_ACCOMMODATION, Q_TOPICS],
    ))

    # 10 ── Info session
    rows.append(event(
        slug="goldman-sachs-engineering-info-session",
        title="Goldman Sachs Engineering — Analyst Programme Info Session",
        host_company="Goldman Sachs",
        host_domain="goldmansachs.com",
        host_logo="🟦",
        host_tagline="Engineering Division",
        event_type="info_session",
        mode="Online",
        description="What the Engineering Analyst Programme involves, how the interview process is structured, and how to prepare for each stage.",
        about=(
            "A straightforward walkthrough of the Goldman Sachs Engineering Analyst Programme: the teams "
            "that take analysts, what the first year looks like week to week, and the full interview "
            "structure from online assessment through superday.\n\n"
            "The team is explicit about what each round tests and what preparation genuinely helps, "
            "including which parts of the process a finance background does and does not matter for."
        ),
        event_date=in_days(7, 17, 30),
        duration_minutes=75,
        location="Virtual — Zoom",
        city="Remote",
        capacity=1000,
        tags=["Analyst programme", "Interview process", "Fintech", "Graduate hiring"],
        agenda=[
            {"time": "5:30 pm", "title": "The programme", "detail": "Teams, rotations and the first-year arc."},
            {"time": "6:00 pm", "title": "The process", "detail": "Every round, and what each one tests."},
            {"time": "6:30 pm", "title": "Preparation", "detail": "What helps, what does not, common mistakes."},
        ],
        speakers=[
            {"name": "Karthik Raman", "title": "Vice President, Engineering", "company": "Goldman Sachs"},
            {"name": "Emily Fernandes", "title": "Campus Recruiting", "company": "Goldman Sachs"},
        ],
        perks=["Preparation guide", "Recording access"],
        eligibility=["Graduating in 2026 or 2027", "All disciplines welcome"],
        registration_questions=[Q_ROLES, Q_TARGET_COMPANIES, Q_QUESTION_FOR_PANEL],
    ))

    # 11 ── Ideathon
    rows.append(event(
        slug="intel-ai-for-good-ideathon",
        title="Intel AI for Good Ideathon — Pitch, No Code Required",
        host_company="Intel",
        host_domain="intel.com",
        host_logo="🟦",
        host_tagline="Intel AI",
        event_type="ideathon",
        mode="Online",
        description="A pitch-only competition judged on problem insight and feasibility rather than implementation — bring an idea, not a repo.",
        about=(
            "An ideathon for people with a sharp problem and no time to build. You submit a written idea, "
            "get written feedback from an Intel mentor, then refine and pitch it live in eight minutes.\n\n"
            "Judging weights problem understanding and feasibility over technical sophistication, which "
            "makes this a good fit for first and second-year students or anyone from a non-CS background "
            "with real domain insight. Shortlisted ideas get engineering support to prototype."
        ),
        event_date=in_days(25, 15, 0),
        end_date=in_days(25, 19, 0),
        duration_minutes=240,
        location="Virtual — Microsoft Teams",
        city="Remote",
        capacity=500,
        registration_deadline=in_days(20, 23, 59),
        tags=["Ideation", "AI for good", "Pitching", "No code"],
        agenda=[
            {"time": "3:00 pm", "title": "Framing session", "detail": "What separates a problem from a solution."},
            {"time": "3:45 pm", "title": "Mentor feedback", "detail": "Written notes on your submitted idea."},
            {"time": "5:00 pm", "title": "Pitch rounds", "detail": "Eight minutes to pitch, four to defend."},
            {"time": "6:30 pm", "title": "Results", "detail": "Shortlist announced for prototype support."},
        ],
        speakers=[{"name": "Deepa Balaraman", "title": "AI Research Manager", "company": "Intel"}],
        prizes=[
            "Top three ideas receive engineering support to build a prototype",
            "Winner gets ₹75,000 in development funding",
        ],
        perks=["Written mentor feedback", "Pitch deck template"],
        eligibility=["Open to all students including non-engineering disciplines", "No prior coding experience needed"],
        registration_questions=[Q_IDEA_SUMMARY, Q_DOMAIN, Q_TEAM_SIZE],
    ))

    # 12 ── Certification drive
    rows.append(event(
        slug="oracle-cloud-certification-drive",
        title="Oracle Cloud Infrastructure Certification Drive",
        host_company="Oracle",
        host_domain="oracle.com",
        host_logo="🟥",
        host_tagline="Oracle University",
        event_type="certification",
        mode="Online",
        description="A guided exam-prep session followed by a free proctored OCI Foundations Associate attempt on the same day.",
        about=(
            "Oracle University runs a three-hour revision session covering the OCI Foundations Associate "
            "exam objectives, with practice questions and explanations for each domain. The proctored "
            "exam follows immediately, and the attempt is free for registered attendees.\n\n"
            "The certification is valid for 18 months and is a recognised credential for cloud "
            "infrastructure roles. If you do not pass, a second free attempt is offered within 30 days."
        ),
        event_date=in_days(17, 10, 0),
        end_date=in_days(17, 16, 0),
        duration_minutes=360,
        location="Virtual — Oracle proctored exam platform",
        city="Remote",
        capacity=400,
        registration_deadline=in_days(14, 23, 59),
        is_certified=True,
        tags=["Certification", "Oracle Cloud", "Free exam voucher", "Exam prep"],
        agenda=[
            {"time": "10:00 am", "title": "Domain revision", "detail": "Core services, identity, networking, billing."},
            {"time": "12:30 pm", "title": "Practice set", "detail": "40 questions with worked explanations."},
            {"time": "2:00 pm", "title": "Proctored exam", "detail": "Live exam attempt, results same day."},
        ],
        speakers=[{"name": "Suresh Pillai", "title": "Oracle University Instructor", "company": "Oracle"}],
        perks=["Free exam voucher", "Second attempt if needed", "Official study guide"],
        eligibility=[
            "Basic understanding of cloud computing concepts",
            "A quiet space and webcam are required for the proctored exam",
            "Government photo ID needed for exam verification",
        ],
        registration_questions=[Q_CLOUD_EXPERIENCE, Q_PRIOR_CERT, Q_LAPTOP],
    ))

    # 13 ── Mock interview marathon
    rows.append(event(
        slug="uber-mock-interview-marathon",
        title="Uber Mock Interview Marathon — Real Interviewers, Real Feedback",
        host_company="Uber",
        host_domain="uber.com",
        host_logo="⬛",
        host_tagline="Uber Engineering India",
        event_type="mock_interview",
        mode="Online",
        description="A one-on-one 45 minute technical mock interview with an Uber engineer, followed by written feedback against the real rubric.",
        about=(
            "Book a slot and sit a genuine 45 minute technical interview with an Uber engineer who "
            "conducts them for real. One coding problem, live collaboration, and the same rubric used "
            "internally.\n\n"
            "Within 48 hours you receive written feedback broken down by problem solving, coding, "
            "communication and testing, with specific examples from your session. Slots are limited "
            "because each one is a real engineer's hour."
        ),
        event_date=in_days(11, 9, 0),
        end_date=in_days(11, 17, 0),
        duration_minutes=45,
        location="Virtual — Uber video platform",
        city="Remote",
        capacity=120,
        registration_deadline=in_days(8, 23, 59),
        is_featured=True,
        tags=["Mock interview", "One-on-one", "Written feedback", "Coding"],
        agenda=[
            {"time": "Your slot", "title": "Technical interview", "detail": "45 minutes, one problem, live coding."},
            {"time": "+48 hours", "title": "Written feedback", "detail": "Scored against the internal rubric."},
        ],
        speakers=[{"name": "Tanvi Joshi", "title": "Senior Software Engineer", "company": "Uber"}],
        perks=["Written rubric-based feedback", "Follow-up resources tailored to your gaps"],
        eligibility=[
            "You should be able to write working code in at least one language",
            "One slot per person so more candidates get a turn",
        ],
        registration_questions=[Q_INTERVIEW_SLOT, Q_PRIMARY_LANGUAGE, Q_SKILL_LEVEL, Q_TARGET_COMPANIES],
    ))

    # 14 ── Conference
    rows.append(event(
        slug="atlassian-engineering-conference-2026",
        title="Atlassian Team Engineering Conference 2026",
        host_company="Atlassian",
        host_domain="atlassian.com",
        host_logo="🟦",
        host_tagline="Atlassian Engineering",
        event_type="conference",
        mode="In Person",
        description="A two-day multi-track conference on developer experience, distributed teams and platform engineering.",
        about=(
            "Two days, three parallel tracks, and a deliberate bias toward talks from people who built "
            "the thing they are describing. Tracks cover developer experience, platform engineering and "
            "the practice of distributed collaboration.\n\n"
            "Between sessions there are open spaces where attendees set the agenda, plus a hallway track "
            "that is genuinely half the value. Student tickets are heavily subsidised."
        ),
        event_date=in_days(38, 9, 0),
        end_date=in_days(39, 18, 0),
        duration_minutes=1080,
        location="Atlassian Bengaluru",
        venue="Atlassian Office, Embassy Tech Village, Devarabeesanahalli",
        city="Bengaluru",
        capacity=700,
        registration_deadline=in_days(32, 23, 59),
        price=999,
        tags=["Conference", "Developer experience", "Platform engineering", "Two-day"],
        agenda=[
            {"time": "Day 1, 9:00 am", "title": "Opening keynote", "detail": "Why developer experience is a business metric."},
            {"time": "Day 1, 11:00 am", "title": "Track sessions", "detail": "Three parallel tracks begin."},
            {"time": "Day 1, 4:00 pm", "title": "Open spaces", "detail": "Attendee-set agenda."},
            {"time": "Day 2, 9:30 am", "title": "Platform deep dives", "detail": "Internal developer platforms in practice."},
            {"time": "Day 2, 3:00 pm", "title": "Closing panel", "detail": "What we would do differently."},
        ],
        speakers=[
            {"name": "Marcus Webb", "title": "Head of Developer Experience", "company": "Atlassian"},
            {"name": "Shruti Desai", "title": "Principal Engineer", "company": "Atlassian"},
            {"name": "Kenji Tanaka", "title": "Engineering Manager, Platform", "company": "Atlassian"},
        ],
        perks=["Both days of talks", "Lunch and refreshments", "Recordings after the event", "Conference swag"],
        eligibility=["Open to all", "Student tickets subsidised — bring your student ID"],
        registration_questions=[Q_TOPICS, Q_ROLES, Q_ACCOMMODATION],
    ))

    # 15 ── Internship drive
    rows.append(event(
        slug="deloitte-summer-internship-drive",
        title="Deloitte Summer Internship Drive — On-the-Spot Shortlisting",
        host_company="Deloitte",
        host_domain="deloitte.com",
        host_logo="🟩",
        host_tagline="Deloitte India Consulting",
        event_type="internship_drive",
        mode="Hybrid",
        description="A single-day drive running aptitude, group discussion and interview rounds back to back, with offers issued the same evening.",
        about=(
            "A complete internship selection process compressed into one day. You clear an aptitude "
            "round in the morning, move to a group discussion, then a technical and HR interview in the "
            "afternoon. Shortlists are announced after each round.\n\n"
            "Selected candidates receive a summer internship offer the same evening, with a stipend and "
            "a pre-placement offer pathway for strong performers. Come prepared as you would for a final "
            "interview — this is the real process, not a practice run."
        ),
        event_date=in_days(14, 8, 30),
        end_date=in_days(14, 19, 0),
        duration_minutes=630,
        location="Deloitte Gurugram + Online rounds",
        venue="Deloitte, DLF Cyber City, Gurugram",
        city="Gurugram",
        capacity=500,
        registration_deadline=in_days(11, 23, 59),
        tags=["Internship", "Same-day offer", "Aptitude", "Group discussion"],
        agenda=[
            {"time": "8:30 am", "title": "Aptitude round", "detail": "Quantitative, logical and verbal sections."},
            {"time": "11:00 am", "title": "Group discussion", "detail": "Shortlisted candidates, eight per group."},
            {"time": "1:30 pm", "title": "Technical interview", "detail": "Fundamentals and project deep dive."},
            {"time": "4:00 pm", "title": "HR interview", "detail": "Fit, motivation and logistics."},
            {"time": "6:30 pm", "title": "Offers released", "detail": "Same-day decisions communicated."},
        ],
        speakers=[{"name": "Anjali Trivedi", "title": "Talent Acquisition Manager", "company": "Deloitte"}],
        perks=["Stipend for selected interns", "Pre-placement offer pathway", "Travel reimbursement for outstation candidates"],
        eligibility=[
            "Pre-final year students graduating in 2027",
            "Minimum 60% aggregate or 6.5 CGPA",
            "No active backlogs at the time of the drive",
        ],
        registration_questions=[Q_ROLES, Q_NOTICE, Q_REPO, Q_ACCOMMODATION],
    ))

    return rows


async def sync_events() -> dict:
    rows = build_events()
    print(f"[INFO] Built {len(rows)} events.")
    created = 0
    updated = 0

    async with async_session_factory() as session:
        existing_rows = (await session.execute(select(Event))).scalars().all()
        by_slug = {r.slug: r for r in existing_rows if r.slug}

        for payload in rows:
            slug = payload["slug"]
            row = by_slug.get(slug)
            if row is None:
                row = Event(slug=slug, event_date=payload["event_date"])
                session.add(row)
                created += 1
            else:
                updated += 1
            for field in FIELDS:
                setattr(row, field, payload[field])

        # Backfill the two events seeded before hosts/types existed so the
        # board renders consistently instead of showing blank logos.
        legacy = [r for r in (await session.execute(select(Event))).scalars().all() if not r.host_company]
        for row in legacy:
            row.host_company = "Carrerpulse Ai"
            row.host_domain = ""
            row.host_logo = "🎓"
            row.host_tagline = "Platform event"
            row.event_type = "career_fair" if "fair" in (row.title or "").lower() else "workshop"
            row.mode = "Online"
            row.city = "Remote"
            row.timezone_label = row.timezone_label or "IST"
            row.duration_minutes = row.duration_minutes or 120
            if not row.tags:
                row.tags = ["Platform hosted"]
            if not row.about:
                row.about = row.description or ""
        if legacy:
            print(f"[INFO] Backfilled {len(legacy)} legacy event(s) with host details.")

        await session.commit()

    print(f"[SUCCESS] Synced events: {created} created, {updated} updated.")
    return {"total": len(rows), "created": created, "updated": updated}


async def main():
    await init_db()
    await sync_events()


if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(0)
