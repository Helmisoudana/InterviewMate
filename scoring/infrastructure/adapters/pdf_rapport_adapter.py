from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)

from scoring.domain.entities.rapport_score import RapportScore
COULEUR_PRINCIPALE = colors.HexColor("#1F2937")   
COULEUR_ACCENT = colors.HexColor("#2563EB")       
COULEUR_TEXTE = colors.HexColor("#374151")        
COULEUR_LIGNE = colors.HexColor("#D1D5DB")        
COULEUR_FOND_ENTETE = colors.HexColor("#F3F4F6")   

def _construire_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="TitrePrincipal",
        fontName="Helvetica-Bold",
        fontSize=20,
        textColor=COULEUR_PRINCIPALE,
        spaceAfter=10,
        alignment=TA_LEFT,
    ))

    styles.add(ParagraphStyle(
        name="SousTitre",
        fontName="Helvetica",
        fontSize=10,
        textColor=COULEUR_TEXTE,
        spaceAfter=16,
        alignment=TA_LEFT,
    ))

    styles.add(ParagraphStyle(
        name="TitreSection",
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=COULEUR_PRINCIPALE,
        spaceBefore=18,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name="TexteCourant",
        fontName="Helvetica",
        fontSize=10,
        textColor=COULEUR_TEXTE,
        leading=14,
    ))

    styles.add(ParagraphStyle(
        name="PuceListe",
        fontName="Helvetica",
        fontSize=10,
        textColor=COULEUR_TEXTE,
        leading=14,
        leftIndent=14,
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        name="CelluleEnTete",
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=colors.white,
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        name="CelluleTexte",
        fontName="Helvetica",
        fontSize=9,
        textColor=COULEUR_TEXTE,
        leading=12,
    ))

    return styles


def _formater_score(valeur) -> str:
    if valeur is None:
        return "N/A"
    return f"{valeur:.1f} / 10"


def generer_pdf_rapport(rapport: RapportScore, chemin_sortie: str, nom_candidat: str = "") -> str:
   
    styles = _construire_styles()
    story = []

    story.append(Paragraph("Rapport d'entretien", styles["TitrePrincipal"]))
    sous_titre = f"Session : {rapport.session_id}"
    if nom_candidat:
        sous_titre = f"Candidat : {nom_candidat}  |  {sous_titre}"
    story.append(Paragraph(sous_titre, styles["SousTitre"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COULEUR_LIGNE, spaceAfter=14))

    story.append(Paragraph("Synthèse des scores", styles["TitreSection"]))

    donnees_scores = [
        ["Score global", "Score technique", "Score communication"],
        [
            _formater_score(rapport.score_global),
            _formater_score(rapport.score_technique),
            _formater_score(rapport.score_communication),
        ],
    ]
    table_scores = Table(donnees_scores, colWidths=[5.5 * cm] * 3)
    table_scores.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COULEUR_ACCENT),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("FONTSIZE", (0, 1), (-1, 1), 13),
        ("TEXTCOLOR", (0, 1), (-1, 1), COULEUR_PRINCIPALE),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 0.5, COULEUR_LIGNE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, COULEUR_LIGNE),
    ]))
    story.append(table_scores)

    if rapport.points_forts:
        story.append(Paragraph("Points forts", styles["TitreSection"]))
        for point in rapport.points_forts:
            story.append(Paragraph(f"&bull;&nbsp;&nbsp;{point}", styles["PuceListe"]))

    if rapport.points_faibles:
        story.append(Paragraph("Points à améliorer", styles["TitreSection"]))
        for point in rapport.points_faibles:
            story.append(Paragraph(f"&bull;&nbsp;&nbsp;{point}", styles["PuceListe"]))

    if rapport.recommandations:
        story.append(Paragraph("Recommandations", styles["TitreSection"]))
        for reco in rapport.recommandations:
            story.append(Paragraph(f"&bull;&nbsp;&nbsp;{reco}", styles["PuceListe"]))

    if rapport.evaluations:
        story.append(Paragraph("Détail des échanges", styles["TitreSection"]))

        entetes = ["Ordre", "Question", "Réponse", "Qualité", "Score", "Remarque"]
        lignes = [[Paragraph(h, styles["CelluleEnTete"]) for h in entetes]]

        for ev in sorted(rapport.evaluations, key=lambda e: e.ordre):
            lignes.append([
                Paragraph(str(ev.ordre), styles["CelluleTexte"]),
                Paragraph(ev.question, styles["CelluleTexte"]),
                Paragraph(ev.reponse, styles["CelluleTexte"]),
                Paragraph(ev.qualite_percue, styles["CelluleTexte"]),
                Paragraph(f"{ev.score_technique:.1f}", styles["CelluleTexte"]),
                Paragraph(ev.remarque or "-", styles["CelluleTexte"]),
            ])

        largeurs = [1.3 * cm, 4.2 * cm, 4.2 * cm, 2.3 * cm, 1.6 * cm, 3.4 * cm]
        table_echanges = Table(lignes, colWidths=largeurs, repeatRows=1)
        table_echanges.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), COULEUR_ACCENT),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (4, 0), (4, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, COULEUR_LIGNE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COULEUR_FOND_ENTETE]),
        ]))
        story.append(table_echanges)

    doc = SimpleDocTemplate(
        chemin_sortie,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        title="Rapport d'entretien",
    )
    doc.build(story)

    return chemin_sortie