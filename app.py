# =========================
# PDF REPORT GENERATOR
# =========================
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
from datetime import datetime

def generate_pdf_report(username, hours, attendance, previous, sleep,
                        motivation, teacher, school, internet,
                        final_score, grade, remark):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    # ── Color Palette ──
    DARK       = colors.HexColor("#050912")
    TEAL       = colors.HexColor("#00ffd5")
    BLUE       = colors.HexColor("#0072ff")
    PURPLE     = colors.HexColor("#7c3aed")
    LIGHT      = colors.HexColor("#dce3f0")
    MUTED      = colors.HexColor("#6b7a99")
    CARD_BG    = colors.HexColor("#0d1526")
    BORDER     = colors.HexColor("#1a2744")

    grade_colors = {
        "A+": colors.HexColor("#00ffd5"),
        "A":  colors.HexColor("#0072ff"),
        "B":  colors.HexColor("#7c3aed"),
        "C":  colors.HexColor("#f59e0b"),
        "D":  colors.HexColor("#ef4444"),
    }
    grade_color = grade_colors.get(grade, TEAL)

    styles = getSampleStyleSheet()

    def style(name, **kw):
        s = ParagraphStyle(name, **kw)
        return s

    S_TITLE = style("S_TITLE",
        fontName="Helvetica-Bold", fontSize=26, textColor=LIGHT,
        alignment=TA_CENTER, spaceAfter=4)
    S_BRAND = style("S_BRAND",
        fontName="Helvetica-Bold", fontSize=13, textColor=TEAL,
        alignment=TA_CENTER, spaceAfter=2)
    S_SUB = style("S_SUB",
        fontName="Helvetica", fontSize=10, textColor=MUTED,
        alignment=TA_CENTER, spaceAfter=2)
    S_SECTION = style("S_SECTION",
        fontName="Helvetica-Bold", fontSize=11, textColor=TEAL,
        spaceAfter=10, spaceBefore=14, leftIndent=4)
    S_NORMAL = style("S_NORMAL",
        fontName="Helvetica", fontSize=10, textColor=LIGHT,
        spaceAfter=6, leading=16)
    S_SCORE = style("S_SCORE",
        fontName="Helvetica-Bold", fontSize=60, textColor=TEAL,
        alignment=TA_CENTER, spaceAfter=0)
    S_GRADE = style("S_GRADE",
        fontName="Helvetica-Bold", fontSize=22, textColor=grade_color,
        alignment=TA_CENTER, spaceAfter=4)
    S_REMARK = style("S_REMARK",
        fontName="Helvetica", fontSize=13, textColor=LIGHT,
        alignment=TA_CENTER, spaceAfter=0)
    S_FOOTER = style("S_FOOTER",
        fontName="Helvetica", fontSize=8, textColor=MUTED,
        alignment=TA_CENTER)
    S_TH = style("S_TH",
        fontName="Helvetica-Bold", fontSize=10, textColor=LIGHT,
        alignment=TA_CENTER)
    S_TD = style("S_TD",
        fontName="Helvetica", fontSize=10, textColor=LIGHT,
        alignment=TA_LEFT)
    S_TD_C = style("S_TD_C",
        fontName="Helvetica", fontSize=10, textColor=LIGHT,
        alignment=TA_CENTER)

    story = []

    # ── HEADER ──
    story.append(Paragraph("🎓 EduPredict", S_BRAND))
    story.append(Paragraph("AI Student Performance Report", S_TITLE))
    story.append(Paragraph(
        f"Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}  |  Student: {username}",
        S_SUB))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=TEAL, spaceAfter=14))

    # ── SCORE CARD ──
    score_data = [
        [Paragraph(str(final_score), S_SCORE)],
        [Paragraph(f"Grade: {grade}", S_GRADE)],
        [Paragraph(remark, S_REMARK)],
    ]
    score_table = Table(score_data, colWidths=[16*cm])
    score_table.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), CARD_BG),
        ("ROUNDEDCORNERS", [12]),
        ("BOX",         (0,0), (-1,-1), 1.5, grade_color),
        ("ALIGN",       (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING",  (0,0), (-1,-1), 18),
        ("BOTTOMPADDING",(0,-1),(-1,-1), 18),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING",(0,0), (-1,-1), 12),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.5*cm))

    # ── ACADEMIC INPUTS ──
    story.append(Paragraph("📐 Academic Inputs", S_SECTION))

    def bar_cell(value, max_val, color=TEAL):
        pct = max(0, min(1, value / max_val))
        filled = int(pct * 30)
        empty  = 30 - filled
        bar = f'<font color="#{color.hexval()[2:]}">{"█" * filled}</font><font color="#1a2744">{"█" * empty}</font>'
        return Paragraph(bar, style("bar",
            fontName="Courier", fontSize=9, textColor=LIGHT))

    acad_data = [
        [Paragraph("Metric", S_TH), Paragraph("Value", S_TH),
         Paragraph("Visual", S_TH), Paragraph("Max", S_TH)],
        [Paragraph("Hours Studied / Day", S_TD),
         Paragraph(f"{hours} hrs", S_TD_C),
         bar_cell(hours, 24, TEAL),
         Paragraph("24 hrs", S_TD_C)],
        [Paragraph("Attendance", S_TD),
         Paragraph(f"{attendance}%", S_TD_C),
         bar_cell(attendance, 100, BLUE),
         Paragraph("100%", S_TD_C)],
        [Paragraph("Previous Score", S_TD),
         Paragraph(f"{previous}/100", S_TD_C),
         bar_cell(previous, 100, PURPLE),
         Paragraph("100", S_TD_C)],
        [Paragraph("Sleep Hours / Day", S_TD),
         Paragraph(f"{sleep} hrs", S_TD_C),
         bar_cell(sleep, 12, TEAL),
         Paragraph("12 hrs", S_TD_C)],
    ]
    acad_table = Table(acad_data, colWidths=[5.5*cm, 2.5*cm, 5.5*cm, 2.5*cm])
    acad_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  CARD_BG),
        ("BACKGROUND",    (0,1), (-1,-1), colors.HexColor("#0a1020")),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.HexColor("#0a1020"), CARD_BG]),
        ("BOX",           (0,0), (-1,-1), 0.8, BORDER),
        ("INNERGRID",     (0,0), (-1,-1), 0.5, BORDER),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LINEBELOW",     (0,0), (-1,0),  1.5, TEAL),
    ]))
    story.append(acad_table)
    story.append(Spacer(1, 0.4*cm))

    # ── ENVIRONMENTAL FACTORS ──
    story.append(Paragraph("🎛️ Environmental Factors", S_SECTION))

    def env_badge(val, pos_vals, colors_map):
        color = colors_map.get(val, MUTED)
        return Paragraph(f'<font color="#{color.hexval()[2:]}">{val}</font>',
            style("badge", fontName="Helvetica-Bold", fontSize=10,
                  textColor=color, alignment=TA_CENTER))

    mot_colors = {"High": colors.HexColor("#00ffd5"), "Medium": colors.HexColor("#f59e0b"), "Low": colors.HexColor("#ef4444")}
    tq_colors  = {"Good": colors.HexColor("#00ffd5"), "Average": colors.HexColor("#f59e0b"), "Poor": colors.HexColor("#ef4444")}
    bin_colors = {"Yes": colors.HexColor("#00ffd5"), "No": colors.HexColor("#ef4444"),
                  "Private": colors.HexColor("#00ffd5"), "Public": colors.HexColor("#0072ff")}

    env_data = [
        [Paragraph("Factor", S_TH), Paragraph("Your Value", S_TH),
         Paragraph("Factor", S_TH), Paragraph("Your Value", S_TH)],
        [Paragraph("Motivation Level", S_TD),
         env_badge(motivation, [], mot_colors),
         Paragraph("Teacher Quality", S_TD),
         env_badge(teacher, [], tq_colors)],
        [Paragraph("School Type", S_TD),
         env_badge(school, [], bin_colors),
         Paragraph("Internet Access", S_TD),
         env_badge(internet, [], bin_colors)],
    ]
    env_table = Table(env_data, colWidths=[4.5*cm, 3.5*cm, 4.5*cm, 3.5*cm])
    env_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  CARD_BG),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),  [colors.HexColor("#0a1020"), CARD_BG]),
        ("BOX",           (0,0), (-1,-1), 0.8, BORDER),
        ("INNERGRID",     (0,0), (-1,-1), 0.5, BORDER),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 9),
        ("BOTTOMPADDING", (0,0), (-1,-1), 9),
        ("LINEBELOW",     (0,0), (-1,0),  1.5, BLUE),
    ]))
    story.append(env_table)
    story.append(Spacer(1, 0.4*cm))

    # ── PERFORMANCE INSIGHTS ──
    story.append(HRFlowable(width="100%", thickness=0.8, color=BORDER, spaceAfter=10))
    story.append(Paragraph("💡 Performance Insights", S_SECTION))

    insights = []
    if hours < 4:
        insights.append("Study hours are low. Try to study at least 5-6 hours daily for better results.")
    elif hours >= 7:
        insights.append("Excellent study hours! Consistent effort is your biggest strength.")

    if attendance < 70:
        insights.append("Attendance is below 70%. Regular attendance significantly impacts performance.")
    elif attendance >= 90:
        insights.append("Outstanding attendance! Your regularity gives you a strong foundation.")

    if sleep < 6:
        insights.append("You're sleeping less than 6 hours. Adequate sleep improves memory and focus.")
    elif 7 <= sleep <= 9:
        insights.append("Good sleep schedule! 7-9 hours is ideal for academic performance.")

    if motivation == "Low":
        insights.append("Motivation is low. Set small daily goals and track your progress to stay motivated.")
    elif motivation == "High":
        insights.append("High motivation is your superpower — keep that energy going!")

    if teacher == "Poor":
        insights.append("Consider supplementing with online resources to compensate for teaching quality.")

    if internet == "No":
        insights.append("No internet access can limit resources. Use school/library internet for study materials.")

    if not insights:
        insights.append("You have a balanced academic profile. Keep maintaining your current habits!")

    for tip in insights:
        story.append(Paragraph(f"• {tip}", S_NORMAL))

    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=10))

    # ── FOOTER ──
    story.append(Paragraph(
        f"EduPredict AI | Student Performance Portal | Confidential Report for {username}",
        S_FOOTER))
    story.append(Paragraph(
        "This report is generated by a machine learning model trained on 12,000+ student records.",
        S_FOOTER))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
