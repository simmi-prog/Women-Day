import os
import re
from datetime import datetime

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, KeepTogether, PageBreak
)

# =========================
# CONFIG (matches your form)
# =========================
CSV_PATH = "responses.csv"
OUTPUT_DIR = "output_pdfs"

COL_TIMESTAMP = "Timestamp"  # google forms default
COL_YOUR_NAME = "Your Name"
COL_DEPT = "Your Department/Team"
COL_WOMAN = "Name of the Woman You Appreciate"
COL_APPRECIATE = "What do you appreciate about her?"
COL_GAIN = "What did you gain because of her?"
COL_REMEMBER = "A short note you want her to remember"

# Layout preferences
MAKE_COMBINED_PDF = True
COMBINED_PDF_NAME = "ALL_WOMEN_GIVE_TO_GAIN_NOTES.pdf"

# Page margins
MARGIN_LEFT = 1.6 * cm
MARGIN_RIGHT = 1.6 * cm
MARGIN_TOP = 1.6 * cm
MARGIN_BOTTOM = 1.6 * cm

# Aesthetic accent (subtle purple)
ACCENT = colors.HexColor("#6A1B9A")
LIGHT_ACCENT = colors.HexColor("#EFE6F7")
TEXT = colors.HexColor("#222222")
SUBTLE = colors.HexColor("#666666")


def safe_filename(name: str) -> str:
    name = (name or "").strip()
    name = re.sub(r"[^\w\s.-]", "", name)
    name = re.sub(r"\s+", " ", name)
    return (name[:120] or "Unknown").strip()


def normalize_cell(x) -> str:
    if pd.isna(x):
        return ""
    return str(x).strip()


def ensure_columns(df: pd.DataFrame):
    needed = [COL_WOMAN, COL_APPRECIATE, COL_GAIN, COL_REMEMBER, COL_YOUR_NAME, COL_DEPT]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(
            "Missing columns in CSV:\n"
            f"{missing}\n\n"
            "Tip: Open responses.csv and compare header row with COL_* constants in the script."
        )


def build_styles():
    base = getSampleStyleSheet()

    title = ParagraphStyle(
        "Title",
        parent=base["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=ACCENT,
        spaceAfter=6,
    )

    subtitle = ParagraphStyle(
        "Subtitle",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        textColor=SUBTLE,
        spaceAfter=12,
    )

    woman_name = ParagraphStyle(
        "WomanName",
        parent=base["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=TEXT,
        spaceBefore=4,
        spaceAfter=10,
    )

    section = ParagraphStyle(
        "Section",
        parent=base["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=16,
        textColor=ACCENT,
        spaceBefore=10,
        spaceAfter=6,
    )

    body = ParagraphStyle(
        "Body",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        textColor=TEXT,
        spaceAfter=6,
    )

    quote = ParagraphStyle(
        "Quote",
        parent=base["BodyText"],
        fontName="Helvetica-Oblique",
        fontSize=11,
        leading=16,
        textColor=TEXT,
        backColor=LIGHT_ACCENT,
        borderPadding=8,
        spaceBefore=6,
        spaceAfter=8,
    )

    meta = ParagraphStyle(
        "Meta",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=12,
        textColor=SUBTLE,
        spaceBefore=0,
        spaceAfter=0,
    )

    small = ParagraphStyle(
        "Small",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=SUBTLE,
    )

    return {
        "title": title,
        "subtitle": subtitle,
        "woman_name": woman_name,
        "section": section,
        "body": body,
        "quote": quote,
        "meta": meta,
        "small": small,
    }


def header_footer(canvas, doc):
    canvas.saveState()
    # Footer line
    canvas.setStrokeColor(LIGHT_ACCENT)
    canvas.setLineWidth(1)
    canvas.line(MARGIN_LEFT, MARGIN_BOTTOM - 0.2 * cm, A4[0] - MARGIN_RIGHT, MARGIN_BOTTOM - 0.2 * cm)

    canvas.setFont("Helvetica", 8.5)
    canvas.setFillColor(SUBTLE)
    canvas.drawString(MARGIN_LEFT, MARGIN_BOTTOM - 0.55 * cm, "Give to Gain — Women’s Day Appreciation")
    canvas.drawRightString(A4[0] - MARGIN_RIGHT, MARGIN_BOTTOM - 0.55 * cm, f"Page {doc.page}")
    canvas.restoreState()


def format_gains(gain_text: str) -> str:
    """
    Google Forms checkbox responses in CSV usually come as:
    "Confidence, Skill, Other: something"
    We keep it as a clean comma-separated line.
    """
    gain_text = (gain_text or "").strip()
    # Normalize separators
    gain_text = re.sub(r"\s*,\s*", ", ", gain_text)
    return gain_text


def build_woman_story(df_woman: pd.DataFrame, woman: str, styles):
    story = []
    today = datetime.now().strftime("%d %b %Y")

    story.append(Paragraph("Give to Gain — Women’s Day Appreciation", styles["title"]))
    story.append(Paragraph(f"A collection of appreciation notes • {today}", styles["subtitle"]))

    story.append(Paragraph(f"For: {woman}", styles["woman_name"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Appreciation Notes", styles["section"]))

    # Sort by timestamp if available
    if COL_TIMESTAMP in df_woman.columns:
        # best-effort sort; forms timestamp is usually parseable
        try:
            df_woman = df_woman.copy()
            df_woman["_ts"] = pd.to_datetime(df_woman[COL_TIMESTAMP], errors="coerce")
            df_woman = df_woman.sort_values("_ts")
        except Exception:
            pass

    blocks = []
    for _, row in df_woman.iterrows():
        appreciator = normalize_cell(row.get(COL_YOUR_NAME, ""))
        dept = normalize_cell(row.get(COL_DEPT, ""))
        msg = normalize_cell(row.get(COL_APPRECIATE, ""))
        gain = format_gains(normalize_cell(row.get(COL_GAIN, "")))
        remember = normalize_cell(row.get(COL_REMEMBER, ""))

        if not msg:
            continue

        # Build one "card-like" block
        block = []

        # Main appreciation text
        block.append(Paragraph(f"“{escape_for_paragraph(msg)}”", styles["quote"]))

        # Gain line (if present)
        if gain:
            block.append(Paragraph(f"<b>Gained:</b> {escape_for_paragraph(gain)}", styles["body"]))

        # Remember line (if present)
        if remember:
            block.append(Paragraph(f"<b>Remember:</b> {escape_for_paragraph(remember)}", styles["body"]))

        # Signature line — ONLY if name provided (no Anonymous label)
        meta_parts = []
        if appreciator:
            meta_parts.append(f"— {escape_for_paragraph(appreciator)}")
        # Dept can be useful even if name is blank, but keep it subtle
        if dept:
            # show dept only if name exists OR you want it regardless; here we show it regardless but subtle
            meta_parts.append(f"{escape_for_paragraph(dept)}")

        if meta_parts:
            block.append(Paragraph(" • ".join(meta_parts), styles["meta"]))

        # Divider space
        block.append(Spacer(1, 10))
        blocks.append(KeepTogether(block))

    if not blocks:
        story.append(Paragraph("No responses yet.", styles["body"]))
    else:
        story.extend(blocks)

    return story


def escape_for_paragraph(text: str) -> str:
    """Reportlab Paragraph uses a mini-HTML; escape special chars safely."""
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def write_pdf(path: str, story):
    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        leftMargin=MARGIN_LEFT,
        rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title="Give to Gain — Women’s Day Appreciation",
        author="Office Team",
    )
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = pd.read_csv(CSV_PATH)
    df.columns = df.columns.str.strip()
    ensure_columns(df)

    # Clean key columns
    df[COL_WOMAN] = df[COL_WOMAN].astype(str).str.strip()
    df[COL_APPRECIATE] = df[COL_APPRECIATE].astype(str).str.strip()

    styles = build_styles()

    # Group by woman
    grouped = df.groupby(COL_WOMAN, dropna=False)

    combined_story = []
    created = 0

    for woman, g in grouped:
        woman_name = normalize_cell(woman)
        if not woman_name or woman_name.lower() == "nan":
            continue

        story = build_woman_story(g, woman_name, styles)

        out_name = safe_filename(woman_name) + ".pdf"
        out_path = os.path.join(OUTPUT_DIR, out_name)
        write_pdf(out_path, story)
        created += 1

        if MAKE_COMBINED_PDF:
            combined_story.extend(story)
            combined_story.append(PageBreak())

    if MAKE_COMBINED_PDF and combined_story:
        combined_path = os.path.join(OUTPUT_DIR, COMBINED_PDF_NAME)
        # Remove trailing extra PageBreak if present
        if isinstance(combined_story[-1], PageBreak):
            combined_story = combined_story[:-1]
        write_pdf(combined_path, combined_story)

    print(f"✅ Done! Created {created} PDF files in: {OUTPUT_DIR}")
    if MAKE_COMBINED_PDF:
        print(f"📄 Combined PDF: {os.path.join(OUTPUT_DIR, COMBINED_PDF_NAME)}")


if __name__ == "__main__":
    main()