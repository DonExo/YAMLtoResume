"""
generate_pdf.py
---------------
Pure rendering engine. Reads a dict (parsed from cv_data.yaml) and
returns the PDF as bytes. No side-effects, no file I/O — the caller
decides what to do with the output.
"""

import io
import os
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, Image,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

W, H = A4

_BASE = os.path.dirname(os.path.abspath(__file__))

# ── Register DejaVu for Unicode symbol support ────────────────────────────────
try:
    pdfmetrics.registerFont(TTFont(
        'DejaVu', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    CONTACT_FONT = 'DejaVu'
except Exception:
    CONTACT_FONT = 'Helvetica'

# ── Palette ───────────────────────────────────────────────────────────────────
DARK   = colors.HexColor("#1A2332")
ACCENT = colors.HexColor("#2563EB")
LIGHT  = colors.HexColor("#F1F5F9")
MID    = colors.HexColor("#64748B")
RULE   = colors.HexColor("#CBD5E1")


# ── Style helpers ─────────────────────────────────────────────────────────────
def S(name, **kw):
    return ParagraphStyle(name, **kw)


STYLES = {
    "name":      S("Name",    fontName="Helvetica-Bold",   fontSize=22,  textColor=DARK,   leading=26, alignment=TA_CENTER),
    "role":      S("Role",    fontName="Helvetica",         fontSize=10,  textColor=ACCENT, leading=14, spaceAfter=2, alignment=TA_CENTER),
    "contact":   S("Contact", fontName=CONTACT_FONT,        fontSize=8.5, textColor=MID,    leading=14, alignment=TA_CENTER),
    "section":   S("Section", fontName="Helvetica-Bold",   fontSize=9,   textColor=ACCENT, leading=12, spaceBefore=8, spaceAfter=2),
    "company":   S("Company", fontName="Helvetica-Bold",   fontSize=9.5, textColor=DARK,   leading=13),
    "date":      S("Date",    fontName="Helvetica-Oblique", fontSize=8.5, textColor=MID,    leading=12),
    "bullet":    S("Bullet",  fontName="Helvetica",         fontSize=8.5, textColor=DARK,   leading=12.5, leftIndent=10, spaceAfter=1.5),
    "highlight": S("Hl",      fontName="Helvetica-Bold",   fontSize=8.5, textColor=DARK,   leading=12.5, leftIndent=10, spaceAfter=1.5),
    "about":     S("About",   fontName="Helvetica",         fontSize=8.5, textColor=DARK,   leading=13),
    "skill":     S("Skill",   fontName="Helvetica",         fontSize=8.5, textColor=DARK,   leading=12),
    "edu":       S("Edu",     fontName="Helvetica",         fontSize=8.5, textColor=DARK,   leading=12),
    "edu_sub":   S("EduSub",  fontName="Helvetica",         fontSize=8,   textColor=MID,    leading=12),
}


# ── Circular photo helper ─────────────────────────────────────────────────────

def _make_circle_png(src_path: str, size_px: int = 400) -> str:
    """
    Centre-crops src_path to a square, applies a circular alpha mask,
    writes to a temp PNG and returns its path. Requires Pillow.
    """
    from PIL import Image as PILImage, ImageDraw

    img  = PILImage.open(src_path).convert("RGBA")
    w, h = img.size
    side = min(w, h)
    img  = img.crop(((w - side) // 2, (h - side) // 2,
                     (w + side) // 2, (h + side) // 2))
    img  = img.resize((size_px, size_px), PILImage.LANCZOS)

    mask = PILImage.new("L", (size_px, size_px), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size_px, size_px), fill=255)
    img.putalpha(mask)

    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    img.save(tmp.name, "PNG")
    return tmp.name


# ── Shared flowable helpers ───────────────────────────────────────────────────

def rule():
    return HRFlowable(width="100%", thickness=0.5, color=RULE, spaceAfter=4, spaceBefore=1)


def section_header(title):
    return [Paragraph(title.upper(), STYLES["section"]), rule()]


def job_block(company, period, bullets, highlight=None):
    items = []
    header = Table(
        [[Paragraph(company, STYLES["company"]), Paragraph(period, STYLES["date"])]],
        colWidths=["72%", "28%"],
    )
    header.setStyle(TableStyle([
        ("ALIGN",         (1, 0), (1, 0), "RIGHT"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    items.append(header)
    if highlight:
        items.append(Paragraph(
            f'<font color="#2563EB">★</font>  <b>{highlight}</b>',
            STYLES["highlight"],
        ))
    for b in bullets:
        items.append(Paragraph(
            f'<font color="#2563EB">▸</font>  {b}',
            STYLES["bullet"],
        ))
    items.append(Spacer(1, 5))
    return KeepTogether(items)


# ── Main entry point ──────────────────────────────────────────────────────────
def generate(data: dict) -> bytes:
    """
    Accepts parsed YAML data dict, returns PDF as bytes.
    """
    buf = io.BytesIO()

    meta = data.get("meta", {})
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=10 * mm,  bottomMargin=10 * mm,
        title=meta.get("pdf_title", data["header"]["name"]),
        author=data["header"]["name"],
    )

    story = []
    hdr   = data["header"]

    # ── Header ────────────────────────────────────────────────────────────────
    inner_w = W - 36 * mm

    contact_text = hdr.get("contact_line1", "")
    if hdr.get("contact_line2"):
        contact_text += f'<br/>{hdr["contact_line2"]}'

    text_block = [
        Paragraph(hdr["name"], STYLES["name"]),
        Spacer(1, 3),
        Paragraph(hdr["role"], STYLES["role"]),
        Spacer(1, 5),
        Paragraph(contact_text, STYLES["contact"]),
    ]

    photo_path = hdr.get("photo", "")
    abs_photo  = os.path.join(_BASE, photo_path) if photo_path and not os.path.isabs(photo_path) else photo_path
    if not abs_photo or not os.path.exists(abs_photo):
        abs_photo = os.path.join(_BASE, "static", "default.png")
    if os.path.exists(abs_photo):
        PHOTO_SIZE  = 33 * mm
        PHOTO_PAD_L = 4 * mm   # nudge photo away from the left edge
        circle_png  = _make_circle_png(abs_photo)
        photo_img   = Image(circle_png, width=PHOTO_SIZE, height=PHOTO_SIZE)

        photo_col_w = PHOTO_SIZE + PHOTO_PAD_L + 4 * mm
        text_col_w  = inner_w - photo_col_w

        inner = Table([[photo_img, text_block]], colWidths=[photo_col_w, text_col_w])
        inner.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN",         (1, 0), (1, 0),   "CENTER"),
            ("LEFTPADDING",   (0, 0), (0,  0),  PHOTO_PAD_L),
            ("LEFTPADDING",   (1, 0), (1,  0),  0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
    else:
        # No photo and no default found — centred single-column layout
        inner = Table([[text_block]], colWidths=[inner_w])
        inner.setStyle(TableStyle([
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ]))

    header_table = Table([[inner]], colWidths=[inner_w])
    header_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), LIGHT),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    # ── Profile ───────────────────────────────────────────────────────────────
    if data.get("profile"):
        story += section_header("Profile")
        story.append(Paragraph(data["profile"].strip(), STYLES["about"]))
        story.append(Spacer(1, 7))

    # ── Experience ────────────────────────────────────────────────────────────
    if data.get("experience"):
        story += section_header("Experience")
        for job in data["experience"]:
            story.append(job_block(
                company=job["company"],
                period=job["period"],
                bullets=job.get("bullets", []),
                highlight=job.get("highlight"),
            ))

    # ── Skills ────────────────────────────────────────────────────────────────
    if data.get("skills"):
        story += section_header("Technical Skills")
        for sk in data["skills"]:
            row = Table(
                [[Paragraph(f'<b>{sk["label"]}</b>', STYLES["skill"]),
                  Paragraph(sk["value"], STYLES["skill"])]],
                colWidths=["22%", "78%"],
            )
            row.setStyle(TableStyle([
                ("TOPPADDING",    (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LEFTPADDING",   (0, 0), (-1, -1), 0),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
            ]))
            story.append(row)
        story.append(Spacer(1, 7))

    # ── Education ─────────────────────────────────────────────────────────────
    if data.get("education"):
        story += section_header("Education")
        for edu in data["education"]:
            story.append(Paragraph(
                f'<b>{edu["degree"]}</b> · {edu["institution"]}',
                STYLES["edu"],
            ))
            if edu.get("detail"):
                story.append(Paragraph(edu["detail"], STYLES["edu_sub"]))

    doc.build(story)
    return buf.getvalue()