"""Renders the aggregated profile into a downloadable PDF ("Download Profile As PDF")."""

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ACCENT = colors.HexColor("#e8891f")
INK = colors.HexColor("#1f2937")
MUTED = colors.HexColor("#6b7280")


def _styles():
    base = getSampleStyleSheet()
    return {
        "name": ParagraphStyle("name", parent=base["Title"], fontSize=20, leading=24, textColor=INK, alignment=TA_LEFT, spaceAfter=2),
        "headline": ParagraphStyle("headline", parent=base["Normal"], fontSize=9.5, leading=13, textColor=MUTED, spaceAfter=2),
        "meta": ParagraphStyle("meta", parent=base["Normal"], fontSize=8.5, leading=12, textColor=MUTED),
        "section": ParagraphStyle("section", parent=base["Heading2"], fontSize=11, leading=14, textColor=ACCENT, spaceBefore=10, spaceAfter=4),
        "item": ParagraphStyle("item", parent=base["Normal"], fontSize=9.5, leading=13, textColor=INK),
        "sub": ParagraphStyle("sub", parent=base["Normal"], fontSize=8.5, leading=12, textColor=MUTED),
        "bullet": ParagraphStyle("bullet", parent=base["Normal"], fontSize=9, leading=12.5, textColor=INK),
    }


def _txt(value) -> str:
    return escape(str(value)) if value not in (None, "") else ""


def _join(parts, sep=" • ") -> str:
    return sep.join(_txt(p) for p in parts if p not in (None, "", []))


def _date_range(start, end, ongoing=False) -> str:
    if ongoing or (start and not end):
        return f"{_txt(start)} – Present" if start else "Present"
    if start and end:
        return f"{_txt(start)} – {_txt(end)}"
    return _txt(start or end)


def _bullets(items, style) -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(_txt(i), style), leftIndent=10) for i in items if str(i).strip()],
        bulletType="bullet",
        bulletFontSize=6,
        bulletColor=ACCENT,
        leftIndent=12,
        spaceBefore=1,
    )


def build_profile_pdf(data: dict) -> bytes:
    styles = _styles()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title=f"{data['full_name']} — Profile",
        author=data["full_name"],
    )

    basic, contact, personal, social = data["basic"], data["contact"], data["personal"], data["social"]
    flow = []

    # ── Header ──
    flow.append(Paragraph(_txt(data["full_name"]), styles["name"]))
    if basic.get("headline"):
        flow.append(Paragraph(_txt(basic["headline"]), styles["headline"]))

    contact_line = _join([contact.get("email"), contact.get("phone"), basic.get("location"), basic.get("experience_level")])
    if contact_line:
        flow.append(Paragraph(contact_line, styles["meta"]))

    links = _join(
        [social.get("linkedin_url"), social.get("github_url"), social.get("portfolio_url")]
        + [link.get("url") for link in social.get("other_links") or []],
        sep="  |  ",
    )
    if links:
        flow.append(Paragraph(links, styles["meta"]))

    id_line = _join([
        f"ID: {basic['enrollment_id']}" if basic.get("enrollment_id") else "",
        _join([personal.get("city"), personal.get("state"), personal.get("country")], sep=", "),
        f"Profile completeness: {data['completion']['percentage']}%",
    ])
    if id_line:
        flow.append(Paragraph(id_line, styles["meta"]))

    flow.append(Spacer(1, 4))
    flow.append(Table([[""]], colWidths=[doc.width], rowHeights=[1.2],
                      style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), ACCENT)])))

    def section(title: str):
        flow.append(Paragraph(title.upper(), styles["section"]))

    # ── About ──
    if data.get("about_me"):
        section("About Me")
        flow.append(Paragraph(_txt(data["about_me"]), styles["item"]))

    # ── Skills ──
    if data.get("skills"):
        section("Skills")
        flow.append(Paragraph(_join([s["name"] for s in data["skills"]], sep=" · "), styles["item"]))

    # ── Education ──
    if data.get("educations"):
        section("Education")
        for edu in data["educations"]:
            flow.append(Paragraph(f"<b>{_txt(edu['institute'])}</b>", styles["item"]))
            score = ""
            if edu.get("cgpa") is not None:
                score = f"CGPA {edu['cgpa']}/{edu.get('cgpa_scale') or 10}"
            if edu.get("percentage") is not None:
                score = _join([score, f"{edu['percentage']}%"], sep=" – ")
            flow.append(Paragraph(
                _join([edu.get("degree"), edu.get("specialization"),
                       _date_range(edu.get("start_year"), edu.get("end_year"), edu.get("is_current")), score]),
                styles["sub"],
            ))
            semesters = [s for s in edu.get("semesters") or [] if s.get("cgpa") is not None]
            if semesters:
                rows = [["Semester", "CGPA", "Ongoing Backlogs", "Total Backlogs"]]
                for sem in semesters:
                    rows.append([
                        _txt(sem.get("semester")),
                        _txt(sem.get("cgpa")),
                        _txt(sem.get("ongoing_backlogs") if sem.get("ongoing_backlogs") is not None else "--"),
                        _txt(sem.get("total_backlogs") if sem.get("total_backlogs") is not None else "--"),
                    ])
                table = Table(rows, colWidths=[doc.width * 0.2] * 4, hAlign="LEFT")
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2fb")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), INK),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d8dEEA")),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]))
                flow.append(Spacer(1, 3))
                flow.append(table)
            flow.append(Spacer(1, 4))

    academic = data.get("academic_summary") or {}
    school = _join([
        f"Class 10: {academic['class_10_percentage']}%" if academic.get("class_10_percentage") is not None else "",
        academic.get("class_10_board"),
        f"Class 12: {academic['class_12_percentage']}%" if academic.get("class_12_percentage") is not None else "",
        academic.get("class_12_board"),
    ])
    if school:
        flow.append(Paragraph(school, styles["sub"]))

    # ── Work experience ──
    if data.get("work_experiences"):
        section("Work Experience")
        for job in data["work_experiences"]:
            flow.append(Paragraph(f"<b>{_txt(job['role'])}</b> — {_txt(job['company'])}", styles["item"]))
            flow.append(Paragraph(
                _join([job.get("employment_type"), job.get("location"),
                       _date_range(job.get("start_date"), job.get("end_date"), job.get("is_current"))]),
                styles["sub"],
            ))
            if job.get("highlights"):
                flow.append(_bullets(job["highlights"], styles["bullet"]))
            flow.append(Spacer(1, 4))

    # ── Positions of responsibility ──
    if data.get("positions"):
        section("Position of Responsibility")
        for pos in data["positions"]:
            flow.append(Paragraph(f"<b>{_txt(pos['title'])}</b>", styles["item"]))
            flow.append(Paragraph(
                _join([pos.get("event_name"), pos.get("department"), pos.get("organization"),
                       _date_range(pos.get("start_date"), pos.get("end_date"))]),
                styles["sub"],
            ))
            if pos.get("highlights"):
                flow.append(_bullets(pos["highlights"], styles["bullet"]))
            flow.append(Spacer(1, 4))

    # ── Projects ──
    if data.get("projects"):
        section("Projects")
        for project in data["projects"]:
            title = f"<b>{_txt(project['title'])}</b>"
            if project.get("tech_stack"):
                title += f" — <i>{_join(project['tech_stack'], sep=', ')}</i>"
            flow.append(Paragraph(title, styles["item"]))
            meta = _join([project.get("subtitle"),
                          _date_range(project.get("start_date"), project.get("end_date"), project.get("is_ongoing")),
                          project.get("project_url"), project.get("repo_url")])
            if meta:
                flow.append(Paragraph(meta, styles["sub"]))
            if project.get("description"):
                flow.append(Paragraph(_txt(project["description"]), styles["bullet"]))
            if project.get("highlights"):
                flow.append(_bullets(project["highlights"], styles["bullet"]))
            flow.append(Spacer(1, 4))

    # ── Awards ──
    if data.get("awards"):
        section("Awards & Achievements")
        for award in data["awards"]:
            flow.append(Paragraph(f"<b>{_txt(award['title'])}</b>", styles["item"]))
            flow.append(Paragraph(
                _join([award.get("issued_by"), award.get("issue_date"), award.get("achievement_type"), award.get("award_url")]),
                styles["sub"],
            ))
            if award.get("description"):
                flow.append(Paragraph(_txt(award["description"]), styles["bullet"]))
            flow.append(Spacer(1, 3))

    # ── Certifications ──
    if data.get("certifications"):
        section("Certifications")
        for cert in data["certifications"]:
            flow.append(Paragraph(f"<b>{_txt(cert['name'])}</b>", styles["item"]))
            flow.append(Paragraph(
                _join([cert.get("issuer"), cert.get("specialization"), cert.get("course_duration"),
                       cert.get("validity"), cert.get("conclusion")]),
                styles["sub"],
            ))
            scores = _join([
                f"Pre-assessment: {cert['pre_assessment_score']}" if cert.get("pre_assessment_score") else "",
                f"Marks: {cert['marks_obtained']}" if cert.get("marks_obtained") else "",
                f"Points: {cert['points_earned']}" if cert.get("points_earned") else "",
            ])
            if scores:
                flow.append(Paragraph(scores, styles["sub"]))
            flow.append(Spacer(1, 3))

    # ── Benchmarks ──
    benchmarks = data.get("benchmarks") or {}
    score_keys = ("total_score", "analytical_score", "logical_score", "verbal_score", "quantitative_score")
    filled = [
        (stage, row)
        for stage, row in benchmarks.items()
        if row and any(row.get(key) is not None for key in score_keys)
    ]
    if filled:
        section("Employability Benchmarks")
        rows = [["Stage", "Analytical", "Logical", "Verbal", "Quantitative", "Total"]]
        for stage, row in filled:
            rows.append([
                stage.title(),
                _txt(row.get("analytical_score") if row.get("analytical_score") is not None else "--"),
                _txt(row.get("logical_score") if row.get("logical_score") is not None else "--"),
                _txt(row.get("verbal_score") if row.get("verbal_score") is not None else "--"),
                _txt(row.get("quantitative_score") if row.get("quantitative_score") is not None else "--"),
                _txt(row.get("total_score") if row.get("total_score") is not None else "--"),
            ])
        table = Table(rows, colWidths=[doc.width / 6] * 6, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2fb")),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d8dEEA")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        flow.append(table)

    # ── Program / mentorship / training ──
    program, mentorship, training = data.get("program") or {}, data.get("mentorship") or {}, data.get("training") or []
    program_line = _join([
        program.get("program_name"),
        f"Year {program['program_year']}" if program.get("program_year") else "",
        f"Institution rating {program['institution_rating']}" if program.get("institution_rating") else "",
    ] + [f"{e.get('label')}: {e.get('value')}" for e in program.get("program_extra") or []])
    mentorship_line = _join([
        "Mentee" if mentorship.get("is_mentee") else "",
        f"Mentor: {mentorship['mentor_name']}" if mentorship.get("mentor_name") else "",
        mentorship.get("mentorship_notes"),
    ])
    training_line = _join([_join([t.get("name"), t.get("status"), t.get("score")], sep=" ") for t in training], sep="; ")
    if program_line or mentorship_line or training_line:
        section("Program & Training")
        for line in (program_line, mentorship_line, training_line):
            if line:
                flow.append(Paragraph(line, styles["sub"]))

    # ── Job preferences ──
    prefs = data.get("job_preferences") or {}
    pref_line = _join([
        _join(prefs.get("open_for") or [], sep=", "),
        _join(prefs.get("job_roles") or [], sep=", "),
        _join(prefs.get("preferred_locations") or [], sep=", "),
        prefs.get("industry"),
        f"Expected CTC {prefs['expected_ctc']}/{prefs.get('ctc_period') or 'Year'}" if prefs.get("expected_ctc") else "",
        "Available for hire" if prefs.get("available_for_hire") else "",
        "Open to relocation" if prefs.get("willing_to_relocate") else "",
    ])
    if pref_line:
        section("Job Preferences")
        flow.append(Paragraph(pref_line, styles["sub"]))

    doc.build(flow)
    return buffer.getvalue()
