import os
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, KeepTogether, PageBreak,
    Image, Table, TableStyle,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# =========================
# CONFIG
# =========================
SCRIPT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = SCRIPT_DIR / "assets"
CSV_PATH = SCRIPT_DIR / "responses.csv"
OUTPUT_DIR = SCRIPT_DIR / "output_pdfs"
BOUQUET_PATH = ASSETS_DIR / "bouquet.png"
FONT_REGULAR = ASSETS_DIR / "Caveat-Regular.ttf"
FONT_BOLD = ASSETS_DIR / "Caveat-Bold.ttf"

COL_TIMESTAMP = "Timestamp"
COL_YOUR_NAME = "Your Name"
COL_DEPT = "Your Department/Team"
COL_WOMAN = "Name of the Woman You Appreciate"
COL_GAIN = "What did you gain from having her around?"
COL_REMEMBER = "A little note she should always remember \U0001f49c"

MAKE_COMBINED_PDF = True
COMBINED_PDF_NAME = "ALL_WOMEN_GIVE_TO_GAIN_NOTES.pdf"

PAGE_W, PAGE_H = A4
MARGIN = 1.2 * cm
USABLE_W = PAGE_W - 2 * MARGIN

COL_GAP = 4 * mm
CARD_COL_W = (USABLE_W - COL_GAP) / 2

ACCENT = colors.HexColor("#6A1B9A")
CARD_BORDER = colors.HexColor("#C9A96E")
TEXT_COLOR = colors.HexColor("#333333")
SUBTLE = colors.HexColor("#888888")
CREAM = colors.HexColor("#FFFDF5")


# ──────────────────────────
# Font registration
# ──────────────────────────
def register_fonts():
    pdfmetrics.registerFont(TTFont("Caveat", str(FONT_REGULAR)))
    pdfmetrics.registerFont(TTFont("Caveat-Bold", str(FONT_BOLD)))


# ──────────────────────────
# Bouquet image preparation
# ──────────────────────────
_prepared_bouquet: str | None = None


def prepare_bouquet() -> str:
    global _prepared_bouquet
    if _prepared_bouquet and os.path.exists(_prepared_bouquet):
        return _prepared_bouquet

    out_path = ASSETS_DIR / "bouquet_clean.png"
    img = PILImage.open(BOUQUET_PATH).convert("RGBA")
    pixels = img.load()
    w, h = img.size
    threshold = 40
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if r < threshold and g < threshold and b < threshold:
                pixels[x, y] = (r, g, b, 0)
    img.save(str(out_path), "PNG")
    _prepared_bouquet = str(out_path)
    return _prepared_bouquet


# ──────────────────────────
# Helpers
# ──────────────────────────
def safe_filename(name: str) -> str:
    name = (name or "").strip()
    name = re.sub(r"[^\w\s.-]", "", name)
    name = re.sub(r"\s+", " ", name)
    return (name[:120] or "Unknown").strip()


def normalize_cell(x) -> str:
    if pd.isna(x):
        return ""
    return str(x).strip()


def escape_xml(text: str) -> str:
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def format_gains(gain_text: str) -> str:
    gain_text = (gain_text or "").strip()
    gain_text = re.sub(r"\s*[;,]\s*", ", ", gain_text)
    return gain_text


def ensure_columns(df: pd.DataFrame):
    needed = [COL_WOMAN, COL_GAIN, COL_REMEMBER, COL_YOUR_NAME, COL_DEPT]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing columns in CSV: {missing}\n"
            "Tip: Open responses.csv and compare header row with COL_* constants."
        )


# ──────────────────────────
# Styles (compact for two-column cards)
# ──────────────────────────
def build_styles():
    base = getSampleStyleSheet()

    compact = {
        "dear": ParagraphStyle(
            "CDear", parent=base["Normal"],
            fontName="Caveat-Bold", fontSize=12, leading=15,
            textColor=TEXT_COLOR, spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "CBody", parent=base["BodyText"],
            fontName="Caveat", fontSize=11, leading=14,
            textColor=TEXT_COLOR, spaceAfter=2,
        ),
        "gain": ParagraphStyle(
            "CGain", parent=base["BodyText"],
            fontName="Caveat", fontSize=9.5, leading=12,
            textColor=SUBTLE, spaceBefore=1, spaceAfter=2,
        ),
        "sign_off": ParagraphStyle(
            "CSignOff", parent=base["Normal"],
            fontName="Caveat-Bold", fontSize=11, leading=13,
            textColor=TEXT_COLOR, alignment=TA_RIGHT,
            spaceBefore=3, spaceAfter=0,
        ),
        "sender_name": ParagraphStyle(
            "CSenderName", parent=base["Normal"],
            fontName="Caveat-Bold", fontSize=11.5, leading=14,
            textColor=ACCENT, alignment=TA_RIGHT,
            spaceBefore=0, spaceAfter=0,
        ),
        "sender_dept": ParagraphStyle(
            "CSenderDept", parent=base["Normal"],
            fontName="Caveat", fontSize=9, leading=11,
            textColor=SUBTLE, alignment=TA_RIGHT,
        ),
    }

    wide = {
        "dear": ParagraphStyle(
            "WDear", parent=base["Normal"],
            fontName="Caveat-Bold", fontSize=18, leading=24,
            textColor=TEXT_COLOR, spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "WBody", parent=base["BodyText"],
            fontName="Caveat", fontSize=15, leading=21,
            textColor=TEXT_COLOR, spaceAfter=4,
        ),
        "gain": ParagraphStyle(
            "WGain", parent=base["BodyText"],
            fontName="Caveat", fontSize=13, leading=17,
            textColor=SUBTLE, spaceBefore=2, spaceAfter=4,
        ),
        "sign_off": ParagraphStyle(
            "WSignOff", parent=base["Normal"],
            fontName="Caveat-Bold", fontSize=15, leading=19,
            textColor=TEXT_COLOR, alignment=TA_RIGHT,
            spaceBefore=6, spaceAfter=0,
        ),
        "sender_name": ParagraphStyle(
            "WSenderName", parent=base["Normal"],
            fontName="Caveat-Bold", fontSize=16, leading=20,
            textColor=ACCENT, alignment=TA_RIGHT,
            spaceBefore=0, spaceAfter=0,
        ),
        "sender_dept": ParagraphStyle(
            "WSenderDept", parent=base["Normal"],
            fontName="Caveat", fontSize=12, leading=15,
            textColor=SUBTLE, alignment=TA_RIGHT,
        ),
    }

    return {
        "page_subtitle": ParagraphStyle(
            "PageSubtitle", parent=base["Normal"],
            fontName="Caveat", fontSize=13, leading=16,
            textColor=SUBTLE, alignment=TA_CENTER, spaceAfter=2,
        ),
        "woman_name": ParagraphStyle(
            "WomanName", parent=base["Heading2"],
            fontName="Caveat-Bold", fontSize=20, leading=24,
            textColor=TEXT_COLOR, alignment=TA_CENTER,
            spaceBefore=2, spaceAfter=2,
        ),
        "letter_body": ParagraphStyle(
            "LetterBody", parent=base["BodyText"],
            fontName="Caveat", fontSize=11, leading=14,
            textColor=TEXT_COLOR, spaceAfter=2,
        ),
        "compact": compact,
        "wide": wide,
    }


# ──────────────────────────
# Letter card builder (compact, for 2-col grid)
# ──────────────────────────
def build_letter_card(woman: str, remember: str, gain: str,
                      sender: str, dept: str, styles,
                      wide: bool = False) -> Table:
    """Build a single bordered letter card. Use wide=True for full-width single card."""
    s = styles["wide"] if wide else styles["compact"]

    rows = []
    rows.append([Paragraph(f"Dear {escape_xml(woman)},", s["dear"])])

    if remember:
        rows.append([Paragraph(escape_xml(remember), s["body"])])

    if gain:
        rows.append([Paragraph(
            f"<i>You gave me: {escape_xml(gain)}</i>", s["gain"]
        )])

    rows.append([Paragraph("With appreciation,", s["sign_off"])])
    if sender:
        rows.append([Paragraph(escape_xml(sender), s["sender_name"])])
    if dept:
        rows.append([Paragraph(escape_xml(dept), s["sender_dept"])])

    inner_w = (USABLE_W - 8 * mm) if wide else (CARD_COL_W - 2 * mm)
    pad = 16 if wide else 8
    pad_v = 12 if wide else 7

    card = Table(rows, colWidths=[inner_w])
    card.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), pad),
        ("RIGHTPADDING", (0, 0), (-1, -1), pad),
        ("TOPPADDING", (0, 0), (0, 0), pad_v),
        ("TOPPADDING", (0, 1), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -2), 0),
        ("BOTTOMPADDING", (0, -1), (-1, -1), pad_v),
        ("BACKGROUND", (0, 0), (-1, -1), CREAM),
        ("BOX", (0, 0), (-1, -1), 1, CARD_BORDER),
        ("ROUNDEDCORNERS", [3, 3, 3, 3]),
    ]))
    return card


def cards_to_two_column_rows(cards: list) -> list:
    """Arrange card flowables into a two-column Table rows list."""
    result = []
    for i in range(0, len(cards), 2):
        left = cards[i]
        right = cards[i + 1] if i + 1 < len(cards) else Paragraph("", ParagraphStyle("empty", fontSize=1))
        result.append([left, right])
    return result


# ──────────────────────────
# Page-level callbacks
# ──────────────────────────
def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#E8DCC8"))
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, MARGIN - 0.15 * cm, PAGE_W - MARGIN, MARGIN - 0.15 * cm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(SUBTLE)
    canvas.drawRightString(PAGE_W - MARGIN, MARGIN - 0.4 * cm, f"Page {doc.page}")
    canvas.restoreState()


# ──────────────────────────
# Story builder (per woman)
# ──────────────────────────
def build_woman_story(df_woman: pd.DataFrame, woman: str, styles) -> list:
    story = []

    bouquet_path = prepare_bouquet()
    story.append(Spacer(1, 2 * mm))
    story.append(Image(bouquet_path, width=6 * cm, height=6 * cm, hAlign="CENTER"))
    story.append(Spacer(1, 2 * mm))

    story.append(Paragraph(f"For {escape_xml(woman)}", styles["woman_name"]))
    story.append(Paragraph(
        "A little bouquet of appreciation from your colleagues",
        styles["page_subtitle"],
    ))
    story.append(Spacer(1, 3 * mm))

    if COL_TIMESTAMP in df_woman.columns:
        try:
            df_woman = df_woman.copy()
            df_woman["_ts"] = pd.to_datetime(
                df_woman[COL_TIMESTAMP], format="mixed", dayfirst=False, errors="coerce"
            )
            df_woman = df_woman.sort_values("_ts")
        except Exception:
            pass

    card_data = []
    for _, row in df_woman.iterrows():
        sender = normalize_cell(row.get(COL_YOUR_NAME, ""))
        dept = normalize_cell(row.get(COL_DEPT, ""))
        gain = format_gains(normalize_cell(row.get(COL_GAIN, "")))
        remember = normalize_cell(row.get(COL_REMEMBER, ""))

        if not remember and not gain:
            continue

        card_data.append((sender, dept, gain, remember))

    if not card_data:
        story.append(Paragraph(
            "No notes yet \u2014 but you are appreciated!",
            styles["letter_body"],
        ))
        return story

    if len(card_data) == 1:
        sender, dept, gain, remember = card_data[0]
        card = build_letter_card(woman, remember, gain, sender, dept, styles, wide=True)
        story.append(card)
    else:
        cards = [
            build_letter_card(woman, rem, gn, snd, dpt, styles, wide=False)
            for snd, dpt, gn, rem in card_data
        ]
        grid_rows = cards_to_two_column_rows(cards)
        grid = Table(
            grid_rows,
            colWidths=[CARD_COL_W, CARD_COL_W],
            spaceBefore=0,
            spaceAfter=0,
        )
        grid.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(grid)

    return story


# ──────────────────────────
# PDF writer
# ──────────────────────────
def write_pdf(path: str, story):
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        title="Give to Gain \u2014 Women\u2019s Day Appreciation",
        author="Office Team",
    )
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)


# ──────────────────────────
# Main
# ──────────────────────────
def main():
    register_fonts()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = pd.read_csv(str(CSV_PATH))
    df.columns = df.columns.str.strip()
    ensure_columns(df)

    df[COL_WOMAN] = df[COL_WOMAN].astype(str).str.split(r"\s*[,;]\s*", regex=True)
    df = df.explode(COL_WOMAN)
    df[COL_WOMAN] = df[COL_WOMAN].str.strip()

    styles = build_styles()
    grouped = df.groupby(COL_WOMAN, dropna=False)

    women_groups = []
    created = 0

    for woman, g in grouped:
        woman_name = normalize_cell(woman)
        if not woman_name or woman_name.lower() == "nan":
            continue

        story = build_woman_story(g, woman_name, styles)

        out_path = OUTPUT_DIR / (safe_filename(woman_name) + ".pdf")
        write_pdf(out_path, story)
        created += 1

        if MAKE_COMBINED_PDF:
            women_groups.append((woman_name, g))

    if MAKE_COMBINED_PDF and women_groups:
        combined_story = []
        for woman_name, g in women_groups:
            combined_story.extend(build_woman_story(g, woman_name, styles))
            combined_story.append(PageBreak())
        if isinstance(combined_story[-1], PageBreak):
            combined_story = combined_story[:-1]
        write_pdf(OUTPUT_DIR / COMBINED_PDF_NAME, combined_story)

    print(f"\u2705 Done! Created {created} PDF files in: {OUTPUT_DIR}")
    if MAKE_COMBINED_PDF:
        print(f"\U0001f4c4 Combined PDF: {OUTPUT_DIR / COMBINED_PDF_NAME}")


if __name__ == "__main__":
    main()
