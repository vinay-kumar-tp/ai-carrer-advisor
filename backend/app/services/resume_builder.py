"""AI Resume Builder — template rendering (HTML preview + PDF) and a structured
resume analyzer.

The candidate's resume ``content`` snapshot (see ``profile_service.build_resume_content``)
is rendered into one of four visually distinct templates. HTML is used for the
live preview iframe in the editor; the same content is rendered to PDF (reportlab)
for download. The analyzer inspects the snapshot + a chosen section set and returns
scored, expandable categories mirroring the reference product (Structure, Skill
Level, Contact Info, Reverse Chronology, Bullet Analysis, Spelling & Punctuation).
"""

from __future__ import annotations

import html
import re
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ─── Section catalogue ───────────────────────────────────────────
# The order used across preview, PDF and the section-toggle sidebar.
SECTION_ORDER = [
    "profile",
    "contact",
    "about",
    "education",
    "work_experience",
    "projects",
    "positions",
    "awards",
    "skills",
    "certifications",
    "social",
]

SECTION_LABELS = {
    "profile": "Profile",
    "contact": "Contact Details",
    "about": "About Me",
    "education": "Education",
    "work_experience": "Work Experience",
    "projects": "Projects",
    "positions": "Position Of Responsibility",
    "awards": "Awards and Achievements",
    "skills": "Key Skills",
    "certifications": "Certifications",
    "social": "Social Links",
}

# Ten genuinely distinct templates, inspired by well-known open-source resume
# designs. Each maps to one of three LAYOUT FAMILIES that change the actual page
# structure (not just the colour):
#   single  — one column, section rules under headings (Jake's, Resumake, RenderCV, FAANGPath, ModernCV, Awesome-CV, Awesome Resume)
#   two-col — narrow left rail (skills/contact) + wide main column (Deedy)
#   sidebar — full-height coloured sidebar + main column (AltaCV, Twenty Seconds CV)
#
# Beyond family, each template tunes: accent colour, ink colour, header style
# (left / center / band / sidebar), heading style (rule / bar / caps / plain),
# font family, and whether it is strictly ATS-plain (no colour blocks).
TEMPLATES = {
    "Jake's Resume": {
        "accent": "#000000", "ink": "#111111", "family": "single", "header": "center",
        "headings": "rule", "font": "serif", "ats_safe": True,
        "desc": "The LaTeX classic. Centered name, thin rules under section headings.",
    },
    "Deedy": {
        "accent": "#1f6feb", "ink": "#1b1f24", "family": "two-col", "header": "left",
        "headings": "caps", "font": "sans", "ats_safe": False,
        "desc": "Compact two-column. Skills and details in a left rail, experience on the right.",
    },
    "Awesome-CV": {
        "accent": "#dc3522", "ink": "#26292c", "family": "single", "header": "center",
        "headings": "bar", "font": "sans", "ats_safe": False,
        "desc": "Elegant centered header with a coloured accent and clean section bars.",
    },
    "AltaCV": {
        "accent": "#0e6e6e", "ink": "#22303a", "family": "sidebar", "header": "sidebar",
        "headings": "bar", "font": "sans", "ats_safe": False,
        "desc": "Coloured sidebar for contact and skills, main column for experience.",
    },
    "ModernCV": {
        "accent": "#3b5bdb", "ink": "#1f2933", "family": "single", "header": "left",
        "headings": "sidebar-rule", "font": "sans", "ats_safe": False,
        "desc": "Left-aligned name with a coloured vertical rule beside each heading.",
    },
    "Resumake": {
        "accent": "#2b6cb0", "ink": "#1a202c", "family": "single", "header": "center",
        "headings": "rule", "font": "sans", "ats_safe": False,
        "desc": "Clean, evenly spaced single column with understated blue headers.",
    },
    "RenderCV": {
        "accent": "#004f90", "ink": "#222222", "family": "single", "header": "center",
        "headings": "rule-thin", "font": "serif", "ats_safe": False,
        "desc": "Minimalist typographic single column, tight and print-perfect.",
    },
    "FAANGPath": {
        "accent": "#111111", "ink": "#111111", "family": "single", "header": "left",
        "headings": "caps", "font": "sans", "ats_safe": True,
        "desc": "Ultra-plain, ATS-safe. No colour, bold uppercase section headings.",
    },
    "Awesome Resume": {
        "accent": "#8b3fbf", "ink": "#241243", "family": "single", "header": "center",
        "headings": "bar", "font": "sans", "ats_safe": False,
        "desc": "Bold accent header band with pill skill chips.",
    },
    "Twenty Seconds CV": {
        "accent": "#e67e22", "ink": "#2c3e50", "family": "sidebar", "header": "sidebar",
        "headings": "caps", "font": "sans", "ats_safe": False,
        "desc": "Warm coloured sidebar with a timeline-style main column.",
    },
}

DEFAULT_TEMPLATE = "Jake's Resume"

_FONT_STACK = {
    "serif": "'Georgia','Times New Roman',serif",
    "sans": "'Segoe UI',Arial,Helvetica,sans-serif",
}


def template_meta() -> list[dict]:
    return [
        {
            "id": k,
            "accent": v["accent"],
            "layout": v["family"],
            "family": v["family"],
            "font": v["font"],
            "ats_safe": v["ats_safe"],
            "description": v["desc"],
        }
        for k, v in TEMPLATES.items()
    ]


# ─── Section counts (drives the sidebar "n/n" badges) ────────────

def section_counts(content: dict) -> dict:
    c = content or {}
    def n(key):
        v = c.get(key)
        return len(v) if isinstance(v, list) else 0
    return {
        "profile": 1 if c.get("name") else 0,
        "contact": 1 if (c.get("email") or c.get("phone")) else 0,
        "about": 1 if (c.get("about") or "").strip() else 0,
        "education": n("educations"),
        "work_experience": n("work_experiences"),
        "projects": n("projects"),
        "positions": n("positions"),
        "awards": n("awards"),
        "skills": 1 if (c.get("skills")) else 0,
        "certifications": n("certifications"),
        "social": 1 if any((c.get("social") or {}).values()) else 0,
    }


def default_sections(content: dict) -> list[str]:
    counts = section_counts(content)
    return [s for s in SECTION_ORDER if counts.get(s, 0) > 0] or ["profile", "contact"]


# ─── Small helpers ───────────────────────────────────────────────

def _e(v) -> str:
    return html.escape(str(v)) if v not in (None, "") else ""


def _social_links(social: dict) -> list[tuple[str, str]]:
    if not social:
        return []
    labels = {
        "linkedin_url": "LinkedIn", "github_url": "GitHub", "portfolio_url": "Portfolio",
        "dribbble_url": "Dribbble", "behance_url": "Behance",
    }
    out = []
    for key, label in labels.items():
        if social.get(key):
            out.append((label, social[key]))
    for extra in social.get("other_links") or []:
        if isinstance(extra, dict) and extra.get("url"):
            out.append((extra.get("label") or "Link", extra["url"]))
    return out


def _edu_line(edu: dict) -> str:
    bits = [edu.get("degree"), edu.get("specialization")]
    head = " — ".join(b for b in bits if b)
    yrs = " – ".join(b for b in [edu.get("start_year"), edu.get("end_year")] if b)
    return head, edu.get("institute", ""), yrs


# ─── HTML preview renderer ───────────────────────────────────────

# Which sections live in the narrow rail for two-column / sidebar families.
_RAIL_SECTIONS = ("contact", "social", "skills", "certifications", "awards")


def _build_section_html(content: dict, active: set, keys) -> list[tuple[str, str]]:
    """Render each active section to (key, html). Order follows SECTION_ORDER."""
    out: list[tuple[str, str]] = []

    def on(sec):
        return sec in active and sec in keys

    if on("about") and (content.get("about") or "").strip():
        out.append(("about", f'<p class="para">{_e(content["about"])}</p>'))

    if on("education") and content.get("educations"):
        rows = []
        for edu in content["educations"]:
            head, inst, yrs = _edu_line(edu)
            score = ""
            if edu.get("cgpa") is not None:
                score = f' · CGPA {_e(edu.get("cgpa"))}/{_e(edu.get("cgpa_scale") or 10)}'
            elif edu.get("percentage") is not None:
                score = f' · {_e(edu.get("percentage"))}%'
            rows.append(
                f'<div class="entry"><div class="entry-top"><b>{_e(inst)}</b>'
                f'<span class="when">{_e(yrs)}</span></div>'
                f'<div class="entry-sub">{_e(head)}{score}</div></div>'
            )
        out.append(("education", "".join(rows)))

    if on("work_experience") and content.get("work_experiences"):
        rows = []
        for job in content["work_experiences"]:
            when = " – ".join(b for b in [job.get("start_date"), "Present" if job.get("is_current") else job.get("end_date")] if b)
            bullets = "".join(f"<li>{_e(h)}</li>" for h in (job.get("highlights") or []))
            rows.append(
                f'<div class="entry"><div class="entry-top"><b>{_e(job.get("role"))}</b>'
                f'<span class="when">{_e(when)}</span></div>'
                f'<div class="entry-sub">{_e(job.get("company"))}{" · " + _e(job.get("location")) if job.get("location") else ""}</div>'
                f'{"<ul>" + bullets + "</ul>" if bullets else ""}</div>'
            )
        out.append(("work_experience", "".join(rows)))

    if on("projects") and content.get("projects"):
        rows = []
        for pr in content["projects"]:
            tech = ", ".join(pr.get("tech_stack") or [])
            bullets = "".join(f"<li>{_e(h)}</li>" for h in (pr.get("highlights") or []))
            desc = f'<div class="entry-sub">{_e(pr.get("description"))}</div>' if pr.get("description") else ""
            techln = f'<div class="tech">{_e(tech)}</div>' if tech else ""
            body = f'<ul>{bullets}</ul>' if bullets else ""
            rows.append(
                f'<div class="entry"><div class="entry-top"><b>{_e(pr.get("title"))}</b></div>'
                f'{desc}{techln}{body}</div>'
            )
        out.append(("projects", "".join(rows)))

    if on("positions") and content.get("positions"):
        rows = []
        for pos in content["positions"]:
            when = " – ".join(b for b in [pos.get("start_date"), pos.get("end_date")] if b)
            org = _e(pos.get("organization") or pos.get("department") or pos.get("event_name"))
            bullets = "".join(f"<li>{_e(h)}</li>" for h in (pos.get("highlights") or []))
            orgln = f'<div class="entry-sub">{org}</div>' if org else ""
            body = f'<ul>{bullets}</ul>' if bullets else ""
            rows.append(
                f'<div class="entry"><div class="entry-top"><b>{_e(pos.get("title"))}</b>'
                f'<span class="when">{_e(when)}</span></div>{orgln}{body}</div>'
            )
        out.append(("positions", "".join(rows)))

    if on("awards") and content.get("awards"):
        rows = "".join(
            f'<li><b>{_e(a.get("title"))}</b>'
            f'{" — " + _e(a.get("issued_by")) if a.get("issued_by") else ""}'
            f'{" (" + _e(a.get("issue_date")) + ")" if a.get("issue_date") else ""}</li>'
            for a in content["awards"]
        )
        out.append(("awards", f"<ul>{rows}</ul>"))

    if on("skills") and content.get("skills"):
        chips = "".join(f'<span class="chip">{_e(s)}</span>' for s in content["skills"])
        out.append(("skills", f'<div class="chips">{chips}</div>'))

    if on("certifications") and content.get("certifications"):
        rows = "".join(
            f'<li><b>{_e(c.get("name"))}</b>'
            f'{" — " + _e(c.get("issuer")) if c.get("issuer") else ""}'
            f'{" · " + _e(c.get("conclusion")) if c.get("conclusion") else ""}</li>'
            for c in content["certifications"]
        )
        out.append(("certifications", f"<ul>{rows}</ul>"))

    return out


def _sections_markup(content: dict, active: set, keys) -> str:
    parts = []
    for key, inner in _build_section_html(content, active, keys):
        if inner:
            parts.append(f'<section><h2>{_e(SECTION_LABELS[key])}</h2>{inner}</section>')
    return "".join(parts)


def render_html(content: dict, template: str, sections: list[str] | None) -> str:
    content = content or {}
    tpl = TEMPLATES.get(template, TEMPLATES[DEFAULT_TEMPLATE])
    accent = tpl["accent"]
    family = tpl["family"]
    header = tpl["header"]
    active = set(sections if sections is not None else default_sections(content))

    def on(sec):
        return sec in active

    name = _e(content.get("name") or "Your Name")
    headline = _e(content.get("headline"))
    contacts = [c for c in [_e(content.get("email")), _e(content.get("phone")), _e(content.get("location"))] if c]
    links = _social_links(content.get("social") or {})
    link_html = " · ".join(f'<a href="{_e(u)}">{_e(l)}</a>' for l, u in links)

    # Header (main-column header for single/two-col; sidebar family renders its
    # own identity inside the rail).
    def header_block():
        inner = f"<h1>{name}</h1>"
        if headline:
            inner += f'<div class="headline">{headline}</div>'
        if on("contact") and contacts:
            inner += f'<div class="contacts">{" &nbsp;|&nbsp; ".join(contacts)}</div>'
        if on("social") and link_html:
            inner += f'<div class="links">{link_html}</div>'
        return f'<header class="hdr hdr-{header}">{inner}</header>'

    css = _template_css(tpl)

    if family == "single":
        # One column: header, then every enabled section top to bottom.
        body = header_block() + _sections_markup(content, active, set(SECTION_ORDER))
        page = f'<div class="page fam-single">{body}</div>'

    elif family == "two-col":
        # Narrow left rail (rail sections) + wide main (everything else).
        rail_keys = [s for s in _RAIL_SECTIONS if s != "contact"]
        main_keys = [s for s in SECTION_ORDER if s not in rail_keys]
        rail = _rail_identity(name, headline, contacts, link_html, on) + _sections_markup(content, active, set(rail_keys))
        main = _sections_markup(content, active, set(main_keys))
        page = (
            f'<div class="page fam-twocol">'
            f'<aside class="rail">{rail}</aside>'
            f'<div class="main">{header_block()}{main}</div>'
            f'</div>'
        )

    else:  # sidebar
        rail_keys = list(_RAIL_SECTIONS)
        main_keys = [s for s in SECTION_ORDER if s not in rail_keys]
        rail = _rail_identity(name, headline, contacts, link_html, on) + _sections_markup(content, active, set(rail_keys))
        main = _sections_markup(content, active, set(main_keys))
        page = (
            f'<div class="page fam-sidebar">'
            f'<aside class="sidebar-rail">{rail}</aside>'
            f'<div class="main">{main}</div>'
            f'</div>'
        )

    return (
        '<!doctype html><html><head><meta charset="utf-8">'
        f"<style>{css}</style></head><body>{page}</body></html>"
    )


def _rail_identity(name, headline, contacts, link_html, on) -> str:
    """Compact identity block shown at the top of a rail/sidebar."""
    inner = f'<div class="rail-name">{name}</div>'
    if headline:
        inner += f'<div class="rail-headline">{headline}</div>'
    contact_bits = list(contacts) if on("contact") else []
    if contact_bits:
        inner += '<div class="rail-contact">' + "".join(f"<div>{c}</div>" for c in contact_bits) + "</div>"
    if on("social") and link_html:
        inner += f'<div class="rail-links">{link_html}</div>'
    return f'<div class="rail-id">{inner}</div>'


def _heading_css(accent: str, ink: str, style: str) -> str:
    """CSS for h2 section headings, per template heading style."""
    if style == "rule":
        return (f"h2{{font-size:12.5px;text-transform:uppercase;letter-spacing:.8px;color:{ink};"
                f"border-bottom:1.4px solid {ink};padding-bottom:3px;margin:0 0 8px;}}")
    if style == "rule-thin":
        return (f"h2{{font-size:11.5px;text-transform:uppercase;letter-spacing:1.4px;color:{accent};"
                f"border-bottom:.8px solid #cbd5e1;padding-bottom:2px;margin:0 0 7px;}}")
    if style == "bar":
        return (f"h2{{font-size:12px;text-transform:uppercase;letter-spacing:1.2px;color:#fff;"
                f"background:{accent};padding:3px 9px;border-radius:3px;margin:0 0 8px;display:inline-block;}}")
    if style == "sidebar-rule":
        return (f"h2{{font-size:12.5px;text-transform:uppercase;letter-spacing:.8px;color:{accent};"
                f"border-left:3px solid {accent};padding:1px 0 1px 8px;margin:0 0 8px;}}")
    # caps
    return (f"h2{{font-size:12.5px;text-transform:uppercase;letter-spacing:1.6px;color:{accent};"
            f"font-weight:800;margin:0 0 7px;}}")


def _template_css(tpl: dict) -> str:
    accent = tpl["accent"]
    ink = tpl["ink"]
    family = tpl["family"]
    font = _FONT_STACK[tpl["font"]]
    heading = _heading_css(accent, ink, tpl["headings"])
    ats = tpl.get("ats_safe")

    # Chips: plain text list for ATS-safe templates, coloured pills otherwise.
    if ats:
        chips = (".chips{display:block;}"
                 ".chip{display:inline;font-size:11px;color:#333;}"
                 ".chip:not(:last-child):after{content:', ';}")
    else:
        chips = (".chips{display:flex;flex-wrap:wrap;gap:5px;}"
                 f".chip{{font-size:10.5px;background:{accent}18;color:{accent};"
                 f"border:1px solid {accent}55;padding:2px 9px;border-radius:11px;}}")

    common = f"""
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:{font}; color:{ink}; background:#fff; }}
.page {{ max-width:820px; margin:0 auto; background:#fff; }}
h1 {{ font-size:26px; margin:0 0 3px; color:{ink}; letter-spacing:.3px; }}
.headline {{ font-size:12.5px; color:{accent}; font-weight:600; margin-bottom:5px; }}
.contacts {{ font-size:11px; color:#475569; }}
.links {{ font-size:11px; margin-top:3px; }}
a {{ color:{accent}; text-decoration:none; }}
section {{ margin-top:15px; }}
{heading}
.para {{ font-size:11.5px; line-height:1.55; margin:0; color:#334155; }}
.entry {{ margin-bottom:9px; }}
.entry-top {{ display:flex; justify-content:space-between; align-items:baseline; gap:10px; }}
.entry-top b {{ font-size:12px; }}
.when {{ font-size:10.5px; color:#64748b; white-space:nowrap; }}
.entry-sub {{ font-size:11px; color:#475569; margin-top:1px; }}
.tech {{ font-size:10.5px; color:{accent}; margin-top:2px; font-style:italic; }}
ul {{ margin:5px 0 0; padding-left:16px; }}
li {{ font-size:11px; line-height:1.5; color:#334155; margin-bottom:2px; }}
{chips}
.hdr {{ margin-bottom:14px; }}
.hdr-center {{ text-align:center; }}
"""

    if family == "single":
        band = ""
        if tpl["headings"] == "bar" and tpl["header"] == "center":
            # Awesome-CV / Awesome Resume: subtle rule under the centered header.
            band = f".fam-single .hdr-center{{border-bottom:2px solid {accent};padding-bottom:10px;}}"
        return common + f"""
.fam-single {{ padding:38px 44px; }}
{band}
"""

    if family == "two-col":
        return common + f"""
.fam-twocol {{ display:grid; grid-template-columns:225px 1fr; min-height:100%; }}
.fam-twocol .rail {{ background:#f4f6fb; padding:32px 20px; border-right:1px solid #e6eaf4; }}
.fam-twocol .main {{ padding:32px 30px; }}
.rail-id {{ margin-bottom:12px; }}
.rail-name {{ font-size:20px; font-weight:800; color:{ink}; line-height:1.15; }}
.rail-headline {{ font-size:11px; color:{accent}; font-weight:600; margin-top:3px; }}
.rail-contact {{ font-size:10.5px; color:#475569; margin-top:8px; line-height:1.7; word-break:break-word; }}
.rail-links {{ font-size:10.5px; margin-top:5px; line-height:1.7; }}
.fam-twocol .rail section {{ margin-top:14px; }}
.fam-twocol .main .hdr {{ display:none; }}
.fam-twocol .rail .chips {{ display:flex; flex-direction:column; gap:3px; }}
.fam-twocol .rail .chip {{ border:none; background:none; padding:0; color:{ink}; }}
"""

    # sidebar
    return common + f"""
.fam-sidebar {{ display:grid; grid-template-columns:240px 1fr; min-height:100%; }}
.fam-sidebar .sidebar-rail {{ background:{accent}; color:#fff; padding:34px 22px; }}
.fam-sidebar .sidebar-rail h2 {{ color:#fff; border-color:rgba(255,255,255,.55);
    background:none; padding-left:0; border-left:none; border-bottom:1px solid rgba(255,255,255,.4); }}
.fam-sidebar .sidebar-rail .entry-sub,
.fam-sidebar .sidebar-rail li,
.fam-sidebar .sidebar-rail .rail-contact,
.fam-sidebar .sidebar-rail .when {{ color:#eef4f4; }}
.fam-sidebar .sidebar-rail b {{ color:#fff; }}
.fam-sidebar .sidebar-rail a {{ color:#fff; text-decoration:underline; }}
.fam-sidebar .sidebar-rail .chips {{ display:flex; flex-wrap:wrap; gap:4px; }}
.fam-sidebar .sidebar-rail .chip {{ background:rgba(255,255,255,.16); color:#fff; border:none; }}
.rail-id {{ margin-bottom:14px; }}
.rail-name {{ font-size:21px; font-weight:800; line-height:1.15; color:#fff; }}
.rail-headline {{ font-size:11.5px; color:#eef4f4; font-weight:600; margin-top:3px; }}
.rail-contact {{ font-size:10.5px; margin-top:10px; line-height:1.8; word-break:break-word; }}
.rail-links {{ font-size:10.5px; margin-top:5px; }}
.fam-sidebar .main {{ padding:34px 30px; }}
"""


# ─── PDF renderer (reportlab, template-aware) ────────────────────

def _pdf_font(tpl: dict) -> tuple[str, str]:
    """Return (regular, bold) reportlab font names for the template's family."""
    if tpl["font"] == "serif":
        return "Times-Roman", "Times-Bold"
    return "Helvetica", "Helvetica-Bold"


def render_pdf(content: dict, template: str, sections: list[str] | None) -> bytes:
    content = content or {}
    tpl = TEMPLATES.get(template, TEMPLATES[DEFAULT_TEMPLATE])
    accent = colors.HexColor(tpl["accent"])
    ink = colors.HexColor(tpl["ink"])
    muted = colors.HexColor("#5b6675")
    active = set(sections if sections is not None else default_sections(content))
    center_header = tpl["header"] == "center"
    hstyle = tpl["headings"]
    font_reg, font_bold = _pdf_font(tpl)

    base = getSampleStyleSheet()
    align = TA_CENTER if center_header else TA_LEFT
    # Bar-style headings render white-on-accent, so they need a different colour.
    head_color = colors.white if hstyle == "bar" else accent
    st = {
        "name": ParagraphStyle("name", parent=base["Title"], fontName=font_bold, fontSize=21, leading=24, textColor=ink, alignment=align, spaceAfter=2),
        "headline": ParagraphStyle("hl", parent=base["Normal"], fontName=font_reg, fontSize=10, leading=13, textColor=accent, alignment=align, spaceAfter=2),
        "meta": ParagraphStyle("meta", parent=base["Normal"], fontName=font_reg, fontSize=8.5, leading=12, textColor=muted, alignment=align),
        "section": ParagraphStyle("sec", parent=base["Heading2"], fontName=font_bold, fontSize=10.5, leading=13, textColor=head_color, spaceBefore=10, spaceAfter=3),
        "section_bar": ParagraphStyle("secbar", parent=base["Heading2"], fontName=font_bold, fontSize=10.5, leading=15, textColor=colors.white, backColor=accent, spaceBefore=10, spaceAfter=4, leftIndent=5, borderPadding=(2, 4, 2, 4)),
        "item": ParagraphStyle("item", parent=base["Normal"], fontName=font_reg, fontSize=9.5, leading=12.5, textColor=ink),
        "sub": ParagraphStyle("sub", parent=base["Normal"], fontName=font_reg, fontSize=8.7, leading=12, textColor=muted),
        "bullet": ParagraphStyle("b", parent=base["Normal"], fontName=font_reg, fontSize=9, leading=12, textColor=ink),
    }

    story: list = []

    def sec_title(title):
        label = _e(title).upper()
        if hstyle == "bar":
            story.append(Paragraph(label, st["section_bar"]))
            return
        story.append(Paragraph(label, st["section"]))
        if hstyle == "caps":
            story.append(Spacer(1, 1))  # caps style: no rule
        elif hstyle == "rule-thin":
            story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#cbd5e1"), spaceBefore=1, spaceAfter=5))
        elif hstyle == "sidebar-rule":
            story.append(HRFlowable(width="100%", thickness=0.8, color=accent, spaceBefore=1, spaceAfter=5))
        else:  # rule
            rule_color = ink if hstyle == "rule" and tpl.get("ats_safe") else accent
            story.append(HRFlowable(width="100%", thickness=1.1, color=rule_color, spaceBefore=1, spaceAfter=5))

    def on(s):
        return s in active

    # Header
    story.append(Paragraph(_e(content.get("name") or "Your Name"), st["name"]))
    if content.get("headline"):
        story.append(Paragraph(_e(content["headline"]), st["headline"]))
    if on("contact"):
        meta = " | ".join(x for x in [_e(content.get("email")), _e(content.get("phone")), _e(content.get("location"))] if x)
        if meta:
            story.append(Paragraph(meta, st["meta"]))
    if on("social"):
        links = _social_links(content.get("social") or {})
        if links:
            story.append(Paragraph(" | ".join(f'<a href="{_e(u)}" color="{tpl["accent"]}">{_e(l)}</a>' for l, u in links), st["meta"]))
    # A thin divider under a centered header, mirroring the HTML.
    if center_header:
        story.append(HRFlowable(width="100%", thickness=1.0, color=accent, spaceBefore=5, spaceAfter=2))
    story.append(Spacer(1, 4))

    if on("about") and (content.get("about") or "").strip():
        sec_title(SECTION_LABELS["about"])
        story.append(Paragraph(_e(content["about"]), st["item"]))

    if on("education") and content.get("educations"):
        sec_title(SECTION_LABELS["education"])
        for edu in content["educations"]:
            head, inst, yrs = _edu_line(edu)
            story.append(Paragraph(f'<b>{_e(inst)}</b>  <font size=8 color="#64748b">{_e(yrs)}</font>', st["item"]))
            extra = _e(head)
            if edu.get("cgpa") is not None:
                extra += f' · CGPA {_e(edu.get("cgpa"))}/{_e(edu.get("cgpa_scale") or 10)}'
            if extra:
                story.append(Paragraph(extra, st["sub"]))

    if on("work_experience") and content.get("work_experiences"):
        sec_title(SECTION_LABELS["work_experience"])
        for job in content["work_experiences"]:
            when = " – ".join(b for b in [job.get("start_date"), "Present" if job.get("is_current") else job.get("end_date")] if b)
            story.append(Paragraph(f'<b>{_e(job.get("role"))}</b>  <font size=8 color="#64748b">{_e(when)}</font>', st["item"]))
            story.append(Paragraph(_e(job.get("company")), st["sub"]))
            _bullets(story, job.get("highlights"), st["bullet"])

    if on("projects") and content.get("projects"):
        sec_title(SECTION_LABELS["projects"])
        for pr in content["projects"]:
            story.append(Paragraph(f'<b>{_e(pr.get("title"))}</b>', st["item"]))
            if pr.get("description"):
                story.append(Paragraph(_e(pr["description"]), st["sub"]))
            _bullets(story, pr.get("highlights"), st["bullet"])

    if on("positions") and content.get("positions"):
        sec_title(SECTION_LABELS["positions"])
        for pos in content["positions"]:
            when = " – ".join(b for b in [pos.get("start_date"), pos.get("end_date")] if b)
            story.append(Paragraph(f'<b>{_e(pos.get("title"))}</b>  <font size=8 color="#64748b">{_e(when)}</font>', st["item"]))
            org = pos.get("organization") or pos.get("department") or pos.get("event_name")
            if org:
                story.append(Paragraph(_e(org), st["sub"]))
            _bullets(story, pos.get("highlights"), st["bullet"])

    if on("awards") and content.get("awards"):
        sec_title(SECTION_LABELS["awards"])
        _bullets(story, [
            f'{a.get("title")}' + (f' — {a.get("issued_by")}' if a.get("issued_by") else '')
            for a in content["awards"]
        ], st["bullet"])

    if on("skills") and content.get("skills"):
        sec_title(SECTION_LABELS["skills"])
        story.append(Paragraph(", ".join(_e(s) for s in content["skills"]), st["item"]))

    if on("certifications") and content.get("certifications"):
        sec_title(SECTION_LABELS["certifications"])
        _bullets(story, [
            f'{c.get("name")}' + (f' — {c.get("issuer")}' if c.get("issuer") else '')
            for c in content["certifications"]
        ], st["bullet"])

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=14 * mm, bottomMargin=14 * mm)
    doc.build(story)
    return buffer.getvalue()


def _bullets(story, items, style):
    items = [i for i in (items or []) if i]
    if not items:
        return
    story.append(
        ListFlowable(
            [ListItem(Paragraph(_e(i), style), leftIndent=8) for i in items],
            bulletType="bullet", start="•", leftIndent=10,
        )
    )


# ─── Structured resume analyzer ──────────────────────────────────

_ACTION_VERBS = (
    "achieved", "managed", "led", "built", "developed", "designed", "improved",
    "delivered", "launched", "spearheaded", "optimized", "created", "implemented",
    "reduced", "increased", "automated", "engineered", "architected", "coordinated",
    "mentored", "analyzed", "streamlined",
)

_WEAK_OPENERS = ("responsible for", "worked on", "helped with", "involved in", "duties included")

# A small, dependency-free spell/style check.
_COMMON_MISSPELLINGS = {
    "recieve": "receive", "responsibilty": "responsibility", "acheive": "achieve",
    "seperate": "separate", "developement": "development", "managment": "management",
    "enviroment": "environment", "sucessful": "successful", "occured": "occurred",
    "definately": "definitely", "experiance": "experience", "knowlege": "knowledge",
    "priviledge": "privilege", "publically": "publicly", "wich": "which",
    "teh": "the", "adn": "and", "collegue": "colleague", "goverment": "government",
}


def _all_bullets(content: dict) -> list[str]:
    out: list[str] = []
    for job in content.get("work_experiences") or []:
        out.extend(job.get("highlights") or [])
    for pr in content.get("projects") or []:
        out.extend(pr.get("highlights") or [])
    for pos in content.get("positions") or []:
        out.extend(pos.get("highlights") or [])
    return [b for b in out if isinstance(b, str) and b.strip()]


def _check(passed: bool, ok_msg: str, bad_msg: str) -> dict:
    return {"status": "pass" if passed else "fail", "message": ok_msg if passed else bad_msg}


def analyze(content: dict, sections: list[str] | None = None) -> dict:
    content = content or {}
    active = set(sections if sections is not None else default_sections(content))
    counts = section_counts(content)

    def shown(sec):
        return sec in active

    # ── Structure ──
    structure_checks = []
    has_about = shown("about") and bool((content.get("about") or "").strip())
    structure_checks.append(_check(
        has_about,
        "Summary section is present.",
        "Summary section is missing or empty. Add a brief professional summary highlighting your key strengths.",
    ))
    has_exp = shown("work_experience") and counts["work_experience"] > 0
    structure_checks.append(_check(
        has_exp,
        f"Experience section contains {counts['work_experience']} entr{'y' if counts['work_experience'] == 1 else 'ies'}.",
        "Experience section is required but missing. Add your work history with roles, companies, and responsibilities.",
    ))
    edu_n = counts["education"] if shown("education") else 0
    structure_checks.append(_check(edu_n > 0, f"Education section contains {edu_n} entr{'y' if edu_n == 1 else 'ies'}.", "Add at least one education entry."))
    sk_n = len(content.get("skills") or []) if shown("skills") else 0
    structure_checks.append(_check(sk_n > 0, f"Skills section contains {sk_n} skill{'' if sk_n == 1 else 's'}.", "Add a Skills section with your core competencies."))
    cert_n = counts["certifications"] if shown("certifications") else 0
    if cert_n > 0:
        structure_checks.append(_check(True, f"Certifications section contains {cert_n} entr{'y' if cert_n == 1 else 'ies'}, which adds value.", ""))
    structure_score = sum(1 for c in structure_checks if c["status"] == "pass")
    structure_total = len(structure_checks)

    # ── Skill Level Analysis ──
    skills = content.get("skills") or []
    skill_checks = [
        _check(len(skills) >= 5, f"{len(skills)} skills listed — good breadth.", f"Only {len(skills)} skills listed. Aim for 6-12 relevant skills."),
        _check(len(skills) <= 20, "Skill list is focused.", "Too many skills can dilute focus — keep the most relevant 12-15."),
    ]
    # crude hard/soft split
    soft = {"communication", "leadership", "teamwork", "collaboration", "problem solving", "time management", "adaptability"}
    hard = [s for s in skills if s.lower() not in soft]
    skill_checks.append(_check(len(hard) >= 3, f"{len(hard)} technical/hard skills detected.", "Add more concrete technical skills relevant to your target roles."))
    skill_score = sum(1 for c in skill_checks if c["status"] == "pass")

    # ── Contact Info ── (score out of 5)
    contact_items = [
        ("Email", bool(content.get("email"))),
        ("Phone", bool(content.get("phone"))),
        ("Location", bool(content.get("location"))),
        ("LinkedIn", bool((content.get("social") or {}).get("linkedin_url"))),
        ("Portfolio/GitHub", bool((content.get("social") or {}).get("github_url") or (content.get("social") or {}).get("portfolio_url"))),
    ]
    contact_checks = [_check(ok, f"{label} present.", f"{label} is missing.") for label, ok in contact_items]
    contact_score = sum(1 for _, ok in contact_items if ok)

    # ── Reverse Chronology ── (score out of 20)
    def _end_year(entry):
        if entry.get("is_current"):
            return 9999
        for key in ("end_year", "end_date"):
            m = re.search(r"(19|20)\d{2}", str(entry.get(key) or ""))
            if m:
                return int(m.group())
        return 0
    chrono_checks = []
    ordered = True
    for group_key, label in (("work_experiences", "Work experience"), ("educations", "Education")):
        entries = content.get(group_key) or []
        years = [_end_year(e) for e in entries]
        in_order = all(years[i] >= years[i + 1] for i in range(len(years) - 1))
        if len(entries) > 1:
            chrono_checks.append(_check(in_order, f"{label} is in reverse-chronological order.", f"{label} is not in reverse-chronological order (most recent first)."))
            ordered = ordered and in_order
    if not chrono_checks:
        chrono_checks.append(_check(True, "Single-entry sections — chronology is fine.", ""))
    chrono_score = 20 if ordered else 12

    # ── Bullet Analysis ── (score out of 50)
    bullets = _all_bullets(content)
    total_b = len(bullets)
    with_verb = sum(1 for b in bullets if b.strip().split()[0].lower().rstrip(":,.") in _ACTION_VERBS) if bullets else 0
    with_number = sum(1 for b in bullets if re.search(r"\d", b))
    weak = [b for b in bullets if any(b.lower().startswith(w) for w in _WEAK_OPENERS)]
    bullet_checks = [
        _check(total_b >= 4, f"{total_b} bullet points across your experience.", "Add more bullet points describing what you did and its impact."),
        _check(total_b == 0 or with_verb >= max(1, total_b // 2), f"{with_verb}/{total_b} bullets start with a strong action verb.", f"Only {with_verb}/{total_b} bullets start with an action verb — lead with verbs like led, built, improved."),
        _check(total_b == 0 or with_number >= max(1, total_b // 3), f"{with_number}/{total_b} bullets include quantified impact.", f"Only {with_number}/{total_b} bullets are quantified — add numbers, %, or scale."),
        _check(not weak, "No weak/passive bullet openers found.", f"{len(weak)} bullet(s) use weak openers (e.g. 'responsible for') — rewrite them actively."),
    ]
    if total_b == 0:
        bullet_score = 10
    else:
        ratio = (with_verb + with_number) / (2 * total_b)
        bullet_score = int(round(20 + ratio * 30))
        bullet_score = max(10, min(50, bullet_score))

    # ── Spelling & Punctuation ── (score out of 100)
    text = _plain(content)
    words = re.findall(r"[A-Za-z']+", text.lower())
    misspelled = sorted({w for w in words if w in _COMMON_MISSPELLINGS})
    double_space = "  " in text
    spelling_checks = [
        _check(not misspelled, "No common misspellings detected.", "Possible misspellings: " + ", ".join(f"{w} → {_COMMON_MISSPELLINGS[w]}" for w in misspelled[:6])),
        _check(not double_space, "Spacing is consistent.", "Double spaces found — tidy up spacing for a clean ATS parse."),
    ]
    spelling_score = 100 - (len(misspelled) * 8) - (0 if not double_space else 5)
    spelling_score = max(40, min(100, spelling_score))

    def cat(key, label, icon, checks, score=None, total=None):
        return {
            "key": key, "label": label, "icon": icon,
            "checks": checks,
            "score": score, "total": total,
            "passed": sum(1 for c in checks if c["status"] == "pass"),
            "count": len(checks),
        }

    categories = [
        cat("structure", "Structure", "layout", structure_checks, structure_score, structure_total),
        cat("skill", "Skill Level Analysis", "briefcase", skill_checks, skill_score, len(skill_checks)),
        cat("contact", "Contact Info", "phone", contact_checks, contact_score, 5),
        cat("chronology", "Reverse Chronology", "trending-up", chrono_checks, chrono_score, 20),
        cat("bullets", "Bullet Analysis", "list", bullet_checks, bullet_score, 50),
        cat("spelling", "Spelling & Punctuation", "spell-check", spelling_checks, spelling_score, 100),
    ]

    # Overall = weighted normalization to a 0-100 ATS-style figure.
    struct_pct = structure_score / max(structure_total, 1)
    contact_pct = contact_score / 5
    chrono_pct = chrono_score / 20
    bullet_pct = bullet_score / 50
    spell_pct = spelling_score / 100
    skill_pct = skill_score / max(len(skill_checks), 1)
    overall = int(round(100 * (
        0.30 * struct_pct + 0.15 * skill_pct + 0.15 * contact_pct +
        0.10 * chrono_pct + 0.20 * bullet_pct + 0.10 * spell_pct
    )))

    return {"overall_score": max(0, min(100, overall)), "categories": categories}


def _plain(content: dict) -> str:
    parts = [content.get("about") or "", " ".join(content.get("skills") or [])]
    parts.extend(_all_bullets(content))
    for edu in content.get("educations") or []:
        parts.append(" ".join(filter(None, [edu.get("institute"), edu.get("degree"), edu.get("specialization")])))
    for c in content.get("certifications") or []:
        parts.append(" ".join(filter(None, [c.get("name"), c.get("issuer")])))
    return "\n".join(p for p in parts if p)
