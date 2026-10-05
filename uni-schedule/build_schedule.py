"""Weekly university timetable on the PKKI letterhead, A4 landscape.

The letterhead is specified for A4 portrait (595.28 x 842 pt). Here the page
is rotated: every frame inset, the wordmark offset above the top rule and the
footer baseline are carried over unchanged, measured from the same edges.

    python3 build_schedule.py   ->   plan-zajec-2026-27.pdf
"""

from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = Path(__file__).parent
FONTS = HERE / "fonts"
OUT = HERE / "plan-zajec-2026-27.pdf"

# ── palette ────────────────────────────────────────────────────────────────
PAPER = HexColor("#FAF9F6")
INK = HexColor("#111110")
MUTED = HexColor("#A3A39E")

# ── geometry (portrait spec rotated to landscape) ──────────────────────────
PW, PH = 595.28, 842.0  # portrait reference
W, H = PH, PW  # landscape page: 842 x 595.28
RULE_W = 0.75
RULE_TOP = H - (PH - 808.64)  # 33.36 pt from the top edge
RULE_BOTTOM = 33.51
RULE_LEFT = 33.36
RULE_RIGHT = W - (PW - 561.86)  # 33.42 pt from the right edge

M_LEFT = 46.5
M_RIGHT = W - 46.5
M_TOP = RULE_TOP - 16
M_BOTTOM = RULE_BOTTOM + 16

WORDMARK_BASELINE = RULE_TOP + (815 - 808.64)
WORDMARK_SIZE = 28.5
WORDMARK_TRACK = 27.2
FOOTER_Y = 15.5

pdfmetrics.registerFont(TTFont("Silkscreen-Bold", FONTS / "Silkscreen-Bold-subset.ttf"))
pdfmetrics.registerFont(TTFont("GeistMono", FONTS / "GeistMono-Regular.ttf"))
pdfmetrics.registerFont(TTFont("GeistMono-SemiBold", FONTS / "GeistMono-SemiBold.ttf"))
REG, SEMI = "GeistMono", "GeistMono-SemiBold"

# ── data ───────────────────────────────────────────────────────────────────
# Source: the student's group list (variant C) and the faculty e-mail of
# 1 Oct 2026. `kind` drives the block style: "wyk" = lecture (solid),
# anything else = outlined.
DAYS = ["poniedziałek", "wtorek", "środa", "czwartek", "piątek", "sobota"]

CLASSES = [
    # day, start, end, subject, form, lecturer, kind
    (0, "16:00", "17:30", "Python", "wykład", "Jabłonowski", "wyk"),
    (1, "17:45", "19:15", "Python", "ćwiczenia · gr. 2", "Rutka", "cw"),
    (1, "19:30", "21:00", "Etyka", "", "Kaczmarek", "inne"),
    (2, "16:00", "17:30", "Matematyka", "wykład", "Skałba", "wyk"),
    (2, "17:45", "19:15", "Matematyka", "ćwiczenia", "Skałba", "cw"),
    (3, "16:00", "17:30", "Filozofia", "", "Jamrozik", "inne"),
    (3, "17:45", "19:15", "Kognitywistyka", "", "Komorowska-Mach,\nSękowski", "inne"),
]
FREE_DAY = 4
SATURDAY = (5, "Praktyczne projekty", "gr. 1", "Jabłonowski",
            ["druga połowa", "semestru", "", "godziny", "do potwierdzenia"])

NOTES = [
    ("Start", "Zajęcia rozpoczynają się 2 października 2026."),
    ("Zapisy", "Trzeba być zapisanym w USOS na wszystkie zajęcia z programu "
               "studiów — wybierać przedmioty właściwe dla swojego roku. "
               "Program: aik.uw.edu.pl/?page_id=6743"),
    ("BHP", "Zapisy w późniejszym terminie — informacja przyjdzie mailem."),
    ("POWI", "Podstawy ochrony własności intelektualnej: problem z zapisami "
             "zgłoszony do pełnomocnika ds. USOS (A. Krzyżanek). Nie ponawiać "
             "maili — czekać na wiadomość."),
]

T0, T1 = 16 * 60, 21 * 60  # visible time window


def minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


# ── text helpers ───────────────────────────────────────────────────────────
def text(c, x, y, s, font, size, color, char_space=0.0, align="left"):
    width = pdfmetrics.stringWidth(s, font, size) + char_space * max(len(s) - 1, 0)
    if align == "right":
        x -= width
    elif align == "center":
        x -= width / 2
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.setCharSpace(char_space)
    t.setFillColor(color)
    t.textOut(s)
    c.drawText(t)
    return width


def wrap(s, font, size, max_w):
    lines = []
    for para in s.split("\n"):
        line = ""
        for word in para.split(" "):
            trial = f"{line} {word}".strip()
            if pdfmetrics.stringWidth(trial, font, size) <= max_w:
                line = trial
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def hline(c, x0, x1, y, color=MUTED, width=RULE_W):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x0, y, x1, y)


def section_heading(c, x, y, w, label):
    """8.8/12 SemiBold caps, charSpace 1.8, hairline rule below."""
    text(c, x, y, label.upper(), SEMI, 8.8, INK, char_space=1.8)
    hline(c, x, x + w, y - 5)
    return y - 5 - 12


# ── letterhead ─────────────────────────────────────────────────────────────
def letterhead(c, page_no):
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    hline(c, 0, W, RULE_TOP)
    hline(c, 0, W, RULE_BOTTOM)
    c.setStrokeColor(MUTED)
    c.setLineWidth(RULE_W)
    c.line(RULE_LEFT, 0, RULE_LEFT, H)
    c.line(RULE_RIGHT, 0, RULE_RIGHT, H)

    c.setFillColor(MUTED)
    c.setFont("Silkscreen-Bold", WORDMARK_SIZE)
    for i, ch in enumerate("PKKI"):
        c.drawString(M_LEFT + i * WORDMARK_TRACK, WORDMARK_BASELINE, ch)

    text(c, W / 2, FOOTER_Y, "https://pukaki.vercel.app", REG, 7.4, MUTED, align="center")
    if page_no > 1:
        text(c, RULE_RIGHT - 13, FOOTER_Y, str(page_no), REG, 7.4, MUTED, align="right")


# ── page body ──────────────────────────────────────────────────────────────
def header(c):
    y = M_TOP - 17
    text(c, M_LEFT, y, "Plan zajęć", SEMI, 17, INK, char_space=1.6)
    meta = " · ".join([
        "Uniwersytet Warszawski",
        "AiK",
        "semestr zimowy 2026/27",
        "od 2 października 2026",
    ])
    text(c, M_LEFT, y - 15, meta, REG, 7.2, MUTED)

    n = len(CLASSES)
    hours = sum(minutes(e) - minutes(s) for _, s, e, *_ in CLASSES) / 60
    summary = f"{n} spotkań tygodniowo · {hours:.1f} h".replace(".", ",") + " · piątek wolny"
    text(c, M_RIGHT, y - 15, summary, REG, 7.2, MUTED, align="right")
    return y - 15 - 22


def block(c, x, y_top, w, h, start, end, subject, form, lecturer, kind):
    pad = 6
    solid = kind == "wyk"
    if solid:
        c.setFillColor(INK)
        c.rect(x, y_top - h, w, h, stroke=0, fill=1)
        fg, sub = PAPER, PAPER
    else:
        c.setFillColor(PAPER)
        c.setStrokeColor(INK)
        c.setLineWidth(RULE_W)
        c.rect(x, y_top - h, w, h, stroke=1, fill=1)
        fg, sub = INK, MUTED

    y = y_top - pad - 7
    text(c, x + pad, y, f"{start}–{end}", REG, 7, sub)
    y -= 15
    text(c, x + pad, y, subject, SEMI, 8.4, fg)
    if form:
        y -= 11.2
        text(c, x + pad, y, form, REG, 7.6, fg)

    lines = wrap(lecturer, REG, 7, w - 2 * pad)
    yb = y_top - h + pad + 2 + (len(lines) - 1) * 10
    for ln in lines:
        text(c, x + pad, yb, ln, REG, 7, sub)
        yb -= 10


def timetable(c, y_top, y_bottom):
    y = section_heading(c, M_LEFT, y_top, M_RIGHT - M_LEFT, "Tydzień")

    axis_w = 34
    gutter = 6
    grid_x = M_LEFT + axis_w
    col_w = (M_RIGHT - grid_x - gutter * (len(DAYS) - 1)) / len(DAYS)
    col_x = [grid_x + i * (col_w + gutter) for i in range(len(DAYS))]

    # day headers
    y -= 2
    for i, day in enumerate(DAYS):
        muted = i == FREE_DAY
        text(c, col_x[i], y, day.upper(), SEMI, 8.4, MUTED if muted else INK, char_space=0.6)
    y -= 10

    g_top, g_bottom = y, y_bottom
    per_min = (g_top - g_bottom) / (T1 - T0)

    def ty(m):
        return g_top - (m - T0) * per_min

    # hour lines + labels
    for m in range(T0, T1 + 1, 60):
        yy = ty(m)
        hline(c, M_LEFT, M_RIGHT, yy, width=0.35)
        label_y = yy - 9 if m < T1 else yy + 3
        text(c, M_LEFT, label_y, f"{m // 60}:00", REG, 7, MUTED)

    # classes
    for day, s, e, subject, form, lecturer, kind in CLASSES:
        top, bot = ty(minutes(s)), ty(minutes(e))
        block(c, col_x[day], top, col_w, top - bot, s, e, subject, form, lecturer, kind)

    # free day
    mid = (g_top + g_bottom) / 2
    text(c, col_x[FREE_DAY] + col_w / 2, mid, "wolne", REG, 7.6, MUTED, align="center")

    # saturday: hours not yet known, so it is not pinned to the time axis
    day, subject, group, lecturer, note = SATURDAY
    x, top, bot = col_x[day], g_top - 4, g_bottom + 4
    c.setStrokeColor(INK)
    c.setLineWidth(RULE_W)
    c.setDash(2, 2.5)
    c.setFillColor(PAPER)
    c.rect(x, bot, col_w, top - bot, stroke=1, fill=1)
    c.setDash()
    pad = 6
    yy = top - pad - 7
    text(c, x + pad, yy, "soboty", REG, 7, MUTED)
    yy -= 15
    for ln in wrap(subject, SEMI, 8.4, col_w - 2 * pad):
        text(c, x + pad, yy, ln, SEMI, 8.4, INK)
        yy -= 11.5
    text(c, x + pad, yy + 0.3, group, REG, 7.6, INK)
    yy -= 11.2 + 6
    for ln in note:
        if ln:
            text(c, x + pad, yy, ln, REG, 7.6, INK)
        yy -= 11.2
    text(c, x + pad, bot + pad + 2, lecturer, REG, 7, MUTED)


LEGEND_W, BAND_GAP, NOTE_LABEL_W, NOTE_COL_GAP = 190, 24, 48, 18
NOTES_W = (M_RIGHT - M_LEFT) - LEGEND_W - BAND_GAP
NOTE_COL_W = (NOTES_W - NOTE_COL_GAP) / 2
NOTE_COLS = [NOTES[:2], NOTES[2:]]


def note_lines(body):
    return wrap(body, REG, 7.4, NOTE_COL_W - NOTE_LABEL_W)


def footer_sections(c, y_top):
    legend_w = LEGEND_W
    notes_x = M_LEFT + LEGEND_W + BAND_GAP
    notes_w = NOTES_W

    # legend
    y = section_heading(c, M_LEFT, y_top, legend_w, "Legenda")
    sw, sh = 22, 9
    rows = [("wyk", "wykład"), ("cw", "ćwiczenia, pozostałe"), ("dash", "termin do potwierdzenia")]
    for kind, label in rows:
        yb = y - 2
        if kind == "wyk":
            c.setFillColor(INK)
            c.rect(M_LEFT, yb, sw, sh, stroke=0, fill=1)
        else:
            c.setStrokeColor(INK)
            c.setLineWidth(RULE_W)
            if kind == "dash":
                c.setDash(2, 2.5)
            c.setFillColor(PAPER)
            c.rect(M_LEFT, yb, sw, sh, stroke=1, fill=1)
            c.setDash()
        text(c, M_LEFT + sw + 8, yb + 1.5, label, REG, 7.6, INK)
        y -= 14

    # notes from the faculty e-mail
    y = section_heading(c, notes_x, y_top, notes_w, "Uwagi organizacyjne")
    label_w, col_gap, half = NOTE_LABEL_W, NOTE_COL_GAP, NOTE_COL_W
    bottom = y
    for ci, items in enumerate(NOTE_COLS):
        x = notes_x + ci * (half + col_gap)
        yy = y
        for label, body in items:
            text(c, x, yy, label, SEMI, 7.6, INK)
            for ln in note_lines(body):
                text(c, x + label_w, yy, ln, REG, 7.4, INK)
                yy -= 10.8
            yy -= 4
        bottom = min(bottom, yy)
    return bottom


def footer_height():
    """Height the bottom band needs, from its heading baseline to the last
    line's baseline (plus descender room)."""
    legend = 2 * 14 + 2
    notes = max(
        sum(len(note_lines(body)) * 10.8 + 4 for _, body in col) - 4 - 10.8
        for col in NOTE_COLS
    )
    return 17 + max(legend, notes) + 3


def build():
    c = canvas.Canvas(str(OUT), pagesize=(W, H))
    c.setTitle("Plan zajęć — semestr zimowy 2026/27")
    c.setAuthor("PKKI")
    letterhead(c, 1)

    y = header(c)
    band_top = M_BOTTOM + footer_height()
    timetable(c, y, band_top + 22)
    footer_sections(c, band_top)

    c.showPage()
    c.save()
    print(f"wrote {OUT}")


if __name__ == "__main__":
    build()
