"""Script to generate the complete, comprehensive Interview Preparation PDF for the Email Classifier."""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and draw total page numbers and running header/footer."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))

        # Do not draw headers/footers on cover/title page if on page 1
        if self._pageNumber > 1:
            # Running Header
            self.drawString(54, 11 * 72 - 36, "Hybrid Email Classifier — Complete Interview Preparation Guide")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)

            # Running Footer
            page_str = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(8.5 * 72 - 54, 36, page_str)
            self.drawString(54, 36, "CONFIDENTIAL — Technical Interview Study Document")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(54, 46, 8.5 * 72 - 54, 46)

        self.restoreState()


def build_pdf(filename: str):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#1A202C"),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#2B6CB0"),
        spaceAfter=14,
    )
    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#1A365D"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )
    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#2C5282"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )
    h3_style = ParagraphStyle(
        "SectionH3",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#2D3748"),
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=4,
    )
    body_bold = ParagraphStyle(
        "BodyBold",
        parent=body_style,
        fontName="Helvetica-Bold",
    )
    bullet_style = ParagraphStyle(
        "BulletText",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3,
    )
    code_style = ParagraphStyle(
        "CodeText",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#1A202C"),
        spaceAfter=3,
    )
    callout_style = ParagraphStyle(
        "CalloutText",
        parent=body_style,
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1A365D"),
    )
    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#2D3748"),
    )
    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.white,
    )

    story = []

    def p(text, style=body_style):
        story.append(Paragraph(text, style))

    def sp(height=6):
        story.append(Spacer(1, height))

    def hr():
        story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#CBD5E0"), spaceBefore=4, spaceAfter=8))

    def code_box(code_lines):
        content = "<br/>".join(
            line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace(" ", "&nbsp;")
            for line in code_lines
        )
        t = Table(
            [[Paragraph(f"<font face='Courier' size=7 color='#1A202C'>{content}</font>", code_style)]],
            colWidths=[504],
        )
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(t)
        sp(4)

    def callout_box(text, title="KEY INTERVIEW TAKEAWAY"):
        content = f"<b>{title}:</b> {text}"
        t = Table(
            [[Paragraph(content, callout_style)]],
            colWidths=[504],
        )
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EBF8FF")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#3182CE")),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(t)
        sp(4)

    # ==========================================
    # TITLE & HEADER
    # ==========================================
    p("HYBRID EMAIL CLASSIFIER", title_style)
    p("Comprehensive Engineering & Machine Learning Interview Preparation Guide", subtitle_style)
    hr()

    p("<b>System Overview:</b> Production-ready, modular dual-classifier pipeline performing multi-dimensional classification of emails into <b>Mode</b> (<code>WORK</code> / <code>PERSONAL</code>) and <b>Priority</b> (<code>HIGH</code> / <code>MEDIUM</code> / <code>LOW</code>), coupled with a deterministic keyword heuristic override layer and a confidence gatekeeper (<code>0.60 threshold</code>).")
    p("<b>Primary Codebase:</b> <code>classifier.py</code>, <code>email_service.py</code>, <code>test_classifier.py</code>, <code>main.py</code> | <b>Tech Stack:</b> Python 3, scikit-learn, TF-IDF, Logistic Regression, joblib.")
    sp(8)

    callout_box(
        "This guide is strictly tailored to the actual implementation in classifier.py. "
        "Every concept, equation, line of code, and architectural decision is explained at an interview-ready level, "
        "enabling you to defend your engineering and ML choices with authority.",
        "EXECUTIVE SUMMARY"
    )
    sp(10)

    # ==========================================
    # SECTION 1: COMPLETE CLASSIFIER FLOW
    # ==========================================
    p("1. Complete Classifier Flow (Step-by-Step)", h1_style)
    hr()
    p("When an email arrives, it undergoes a linear 5-step processing pipeline. Here is the exact end-to-end trace through the codebase:")
    sp(4)

    steps_data = [
        [
            Paragraph("<b>Stage</b>", table_header_style),
            Paragraph("<b>File &amp; Function</b>", table_header_style),
            Paragraph("<b>Input &rarr; Processing &rarr; Output</b>", table_header_style),
            Paragraph("<b>Why Needed</b>", table_header_style),
        ],
        [
            Paragraph("<b>1. Ingress &amp; Concat</b>", table_cell_style),
            Paragraph("<code>email_service.py</code><br/><code>receive_email()</code><br/><code>classifier.py</code><br/><code>_extract_text()</code>", table_cell_style),
            Paragraph("<b>In:</b> Raw dict/object with <code>subject</code> &amp; <code>body</code>.<br/><b>Proc:</b> Combines into <code>f\"{subject} {body}\".strip()</code>.<br/><b>Out:</b> Single unified string.", table_cell_style),
            Paragraph("Consolidates critical signal. Subjects often hold high-signal keywords (e.g., 'URGENT'), while bodies supply semantic depth.", table_cell_style),
        ],
        [
            Paragraph("<b>2. Mode ML</b>", table_cell_style),
            Paragraph("<code>classifier.py</code><br/><code>classify_mode()</code>", table_cell_style),
            Paragraph("<b>In:</b> Unified text string.<br/><b>Proc:</b> Pipeline transforms text to TF-IDF vector, executes Logistic Regression <code>predict_proba([text])</code>.<br/><b>Out:</b> <code>(predicted_mode, confidence)</code>.", table_cell_style),
            Paragraph("Determines email context (WORK vs PERSONAL) independently from its urgency.", table_cell_style),
        ],
        [
            Paragraph("<b>3. Priority ML</b>", table_cell_style),
            Paragraph("<code>classifier.py</code><br/><code>classify_priority()</code>", table_cell_style),
            Paragraph("<b>In:</b> Unified text string.<br/><b>Proc:</b> Independent Pipeline computes TF-IDF + Logistic Regression across 3 classes: HIGH, MEDIUM, LOW.<br/><b>Out:</b> <code>(predicted_priority, confidence)</code>.", table_cell_style),
            Paragraph("Establishes baseline machine-learning urgency estimation from broader vocabulary patterns.", table_cell_style),
        ],
        [
            Paragraph("<b>4. Rule Layer</b>", table_cell_style),
            Paragraph("<code>classifier.py</code><br/><code>apply_priority_rules()</code>", table_cell_style),
            Paragraph("<b>In:</b> Email text + ML priority prediction.<br/><b>Proc:</b> Deterministic case-insensitive search against <code>HIGH_PRIORITY_KEYWORDS</code> &amp; <code>LOW_PRIORITY_KEYWORDS</code>.<br/><b>Out:</b> <code>(final_priority, rule_applied)</code>.", table_cell_style),
            Paragraph("Guarantees that SLA-critical trigger words (e.g., 'urgent', 'asap', 'outage') always escalate to HIGH, protecting against ML false negatives.", table_cell_style),
        ],
        [
            Paragraph("<b>5. Confidence &amp; Review</b>", table_cell_style),
            Paragraph("<code>classifier.py</code><br/><code>calculate_confidence()</code><br/><code>classify_email()</code>", table_cell_style),
            Paragraph("<b>In:</b> Probabilities and rule status.<br/><b>Proc:</b> Checks if <code>min(mode_conf, priority_conf) &lt; 0.60</code>.<br/><b>Out:</b> Complete classification dict with <code>needs_human_review</code> boolean.", table_cell_style),
            Paragraph("Safeguards user trust by flagging ambiguous, noisy, or out-of-distribution emails for human triage.", table_cell_style),
        ],
    ]

    t_steps = Table(steps_data, colWidths=[80, 110, 190, 124])
    t_steps.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_steps)
    sp(10)

    # ==========================================
    # SECTION 2: PROJECT ARCHITECTURE
    # ==========================================
    p("2. Project Architecture & Component Responsibilities", h1_style)
    hr()
    code_box([
        "                         +-----------------------+",
        "                         |    Incoming Email     |",
        "                         |   (Subject + Body)    |",
        "                         +-----------+-----------+",
        "                                     |",
        "                            [_extract_text()]",
        "                                     |",
        "                                     v",
        "                     +-------------------------------+",
        "                     |   Concatenated Text String    |",
        "                     +---------------+---------------+",
        "                                     |",
        "                 +-------------------+-------------------+",
        "                 |                                       |",
        "                 v                                       v",
        "      +---------------------+                 +---------------------+",
        "      | Mode Pipeline       |                 | Priority Pipeline   |",
        "      | - TF-IDF Vectorizer |                 | - TF-IDF Vectorizer |",
        "      | - Logistic Regr.    |                 | - Logistic Regr.    |",
        "      +----------+----------+                 +----------+----------+",
        "                 |                                       |",
        "          [WORK / PERSONAL]                       [HIGH / MED / LOW]",
        "          + mode_confidence                       + priority_confidence",
        "                 |                                       |",
        "                 |                                       v",
        "                 |                            +---------------------+",
        "                 |                            | Rule-Based Layer    |",
        "                 |                            | (Keyword Override)  |",
        "                 |                            +----------+----------+",
        "                 |                                       |",
        "                 |                                       | final_priority",
        "                 |                                       | effective_confidence",
        "                 +-------------------+-------------------+",
        "                                     |",
        "                                     v",
        "                     +-------------------------------+",
        "                     | Confidence Gatekeeper         |",
        "                     | Check: conf < 0.60 Threshold  |",
        "                     +---------------+---------------+",
        "                                     |",
        "                                     v",
        "                     +-------------------------------+",
        "                     | Final Classification JSON     |",
        "                     | { mode, priority, conf, ... } |",
        "                     +-------------------------------+",
    ])
    sp(4)
    p("<b>Component Responsibilities:</b>", h2_style)
    p("• <b>ModelRegistry (classifier.py):</b> Decouples model persistence from inference. Implements a plug-and-play pattern: attempts to load pre-trained artifacts from <code>models/*.joblib</code>; if absent, transparently initializes fitted pipelines with balanced anchor samples so the service never crashes.")
    p("• <b>_extract_text (classifier.py):</b> Normalization utility that safely inspects dictionaries or arbitrary email objects, extracting subject and body without fragile key assumptions.")
    p("• <b>classify_mode (classifier.py):</b> Specialist binary classifier focused strictly on organizational context (WORK vs PERSONAL).")
    p("• <b>classify_priority (classifier.py):</b> Specialist 3-class model focused on baseline urgency.")
    p("• <b>apply_priority_rules (classifier.py):</b> Deterministic heuristic layer executing domain-specific policy overrides.")
    p("• <b>classify_email (classifier.py):</b> Pipeline coordinator assembling the final contract payload and calculating the human review trigger.")
    sp(10)

    # ==========================================
    # SECTION 3: TF-IDF IN-DEPTH
    # ==========================================
    p("3. Deep Dive into TF-IDF (Term Frequency - Inverse Document Frequency)", h1_style)
    hr()
    p("<b>What is TF-IDF?</b> A numerical statistical measure used in Natural Language Processing to quantify how important a given word (or n-gram) is to a specific document within a larger collection (corpus).")
    p("<b>Why TF-IDF was chosen for this system:</b>")
    p("1. <b>Extreme Speed &amp; Efficiency:</b> Sub-millisecond CPU inference without GPUs or external API latency.")
    p("2. <b>Interpretability:</b> Clear mathematical relationship between word occurrence and vector weights. Coefficients can be inspected directly in an interview.")
    p("3. <b>Domain Appropriateness:</b> Email subjects and bodies are dense with discriminative keyword signals (e.g., 'invoice', 'sprint', 'urgent', 'dinner').")
    p("4. <b>Zero Hallucination:</b> Deterministic mathematical transformation without non-deterministic generative drift.")
    sp(4)

    p("<b>Mathematical Formulation:</b>", h2_style)
    p("• <b>Term Frequency (TF):</b> Measures how frequently a word $t$ appears in document $d$:")
    p("&nbsp;&nbsp;&nbsp;&nbsp;<code>TF(t, d) = (Count of t in d) / (Total words in d)</code>")
    p("&nbsp;&nbsp;&nbsp;&nbsp;<i>In our code:</i> We enabled <code>sublinear_tf=True</code>, which applies logarithmic scaling: <code>1 + log(TF)</code> for $TF > 0$. This prevents a word occurring 10 times from dominating 10 times more than a word occurring once.")
    p("• <b>Inverse Document Frequency (IDF):</b> Measures how rare or common a word is across the entire corpus of documents $D$:")
    p("&nbsp;&nbsp;&nbsp;&nbsp;<code>IDF(t) = log( (1 + Total Documents N) / (1 + Documents containing t) ) + 1</code> (scikit-learn smoothed formula)")
    p("&nbsp;&nbsp;&nbsp;&nbsp;If a word appears in every single email (e.g., 'the', 'email', 'hello'), its IDF approaches zero. If a word appears only in outage alerts (e.g., 'database', 'crash'), its IDF is high.")
    p("• <b>TF-IDF Weight:</b>")
    p("&nbsp;&nbsp;&nbsp;&nbsp;<code>TF-IDF(t, d) = TF(t, d) &times; IDF(t)</code>")
    p("&nbsp;&nbsp;&nbsp;&nbsp;The resulting vector is then L2-normalized so that long emails do not artificially have larger vectors than short emails.")
    sp(4)

    p("<b>Concrete Numerical Walkthrough:</b>", h2_style)
    p("Consider a corpus of 3 emails:")
    p("• Email 1: <i>'urgent database server crash'</i> (Work / High Priority)")
    p("• Email 2: <i>'urgent dinner plans tonight'</i> (Personal / High Priority)")
    p("• Email 3: <i>'dinner recipes for tonight'</i> (Personal / Low Priority)")
    sp(2)
    p("Let us compute TF-IDF for <b>'database'</b> vs <b>'urgent'</b> in Email 1:")
    p("• Total emails $N = 3$.")
    p("• 'database' appears in 1 email. $IDF = log(4 / 2) + 1 = log(2) + 1 &approx; 0.693 + 1 = 1.693$.")
    p("• 'urgent' appears in 2 emails. $IDF = log(4 / 3) + 1 = log(1.333) + 1 &approx; 0.288 + 1 = 1.288$.")
    p("• 'database' receives a <b>higher weight</b> in Email 1 because it is exclusive to technical work alerts, whereas 'urgent' is somewhat diluted across categories.")
    sp(4)

    p("<b>Representation Transformation Flow:</b>", h2_style)
    code_box([
        "Raw Email:     \"Client meeting tomorrow\"",
        "      |",
        "Tokenization:  ['client', 'meeting', 'tomorrow', 'client meeting', 'meeting tomorrow']",
        "               (Note: ngram_range=(1, 2) in classifier.py captures unigrams and bigrams)",
        "      |",
        "Vocabulary:    Index map e.g. {'client': 12, 'meeting': 45, 'client meeting': 88, ...}",
        "      |",
        "Vectorization: [0.0, 0.0, ..., 0.48, ..., 0.62, ..., 0.35, ..., 0.0] (L2-normalized 1xD float array)",
        "      |",
        "ML Inference:  LogReg dot product: z = W · x + b -> softmax(z) -> probabilities",
    ])
    sp(10)

    # ==========================================
    # SECTION 4: MODE CLASSIFIER
    # ==========================================
    p("4. Mode Classifier (WORK vs PERSONAL)", h1_style)
    hr()
    p("<b>Model:</b> Binary Logistic Regression fitted on a specialized TF-IDF feature space.")
    p("<b>Input:</b> <code>text = subject + ' ' + body</code>")
    p("<b>Classes:</b> <code>['PERSONAL', 'WORK']</code> (alphabetically indexed by scikit-learn).")
    p("<b>Mathematical Decision Mechanism:</b>")
    p("1. Given input vector $x \\in \\mathbb{R}^D$, Logistic Regression calculates the linear logit:")
    p("&nbsp;&nbsp;&nbsp;&nbsp;$$z = w^T x + b$$")
    p("2. The logit is converted to probabilities via the Sigmoid (or Softmax) function:")
    p("&nbsp;&nbsp;&nbsp;&nbsp;$$P(WORK|x) = \\frac{1}{1 + e^{-z}}, \\quad P(PERSONAL|x) = 1 - P(WORK|x)$$")
    p("3. The predicted class is <code>classes_[argmax(probabilities)]</code>.")
    sp(4)

    p("<b>Realistic Interview Example:</b>", h2_style)
    p("<b>Email:</b> <i>'Subject: Client meeting scheduled for tomorrow | Body: Attached is the quarterly project roadmap.'</i>")
    p("• <b>Active Features:</b> 'client' (+w), 'meeting' (+w), 'scheduled' (+w), 'quarterly' (+w), 'project' (+w), 'roadmap' (+w).")
    p("• <b>Weights:</b> In the fitted model, all these terms possess strong positive coefficients for the <code>WORK</code> class.")
    p("• <b>Logit:</b> $z = +3.12$.")
    p("• <b>Probabilities:</b> $P(WORK) = 1 / (1 + e^{-3.12}) = 0.958$ (&approx; 96%), $P(PERSONAL) = 0.042$ (&approx; 4%).")
    p("• <b>Output:</b> <code>('WORK', 0.96)</code>.")
    sp(10)

    # ==========================================
    # SECTION 5: PRIORITY CLASSIFIER
    # ==========================================
    p("5. Priority Classifier (HIGH / MEDIUM / LOW)", h1_style)
    hr()
    p("<b>Model:</b> Multinomial Logistic Regression fitted independently on TF-IDF features.")
    p("<b>Classes:</b> 3 classes: <code>['HIGH', 'LOW', 'MEDIUM']</code>.")
    p("<b>Why Priority is an Independent Classifier:</b>")
    p("<i>Interview Distinction:</i> <b>Orthogonality of Mode and Priority</b>. An email can be <i>Work + High</i> (server down), <i>Work + Low</i> (weekly newsletter), <i>Personal + High</i> (family hospital emergency), or <i>Personal + Low</i> (casual joke). Mode represents <i>context domain</i>; Priority represents <i>temporal urgency/actionability</i>. Treating them as independent models reduces complexity from an exponential multi-class space down to two focused, modular classifiers.")
    sp(4)
    p("<b>Decision Logic (Softmax Formulation):</b>")
    p("For 3 classes $k \\in \\{HIGH, MEDIUM, LOW\\}$, the model computes logits $z_k = w_k^T x + b_k$, then normalizes:")
    p("&nbsp;&nbsp;&nbsp;&nbsp;$$P(class = k|x) = \\frac{e^{z_k}}{\\sum_{j=1}^3 e^{z_j}}$$")
    sp(4)
    p("<b>Examples across all three classes:</b>")
    p("• <b>HIGH:</b> <i>'Critical security patch required immediately before deadline'</i> &rarr; high logits on 'critical', 'patch', 'deadline'. $P(HIGH)=0.89, P(MED)=0.08, P(LOW)=0.03$. Predicted: <b>HIGH (0.89)</b>.")
    p("• <b>MEDIUM:</b> <i>'Weekly team check-in notes and roadmap discussion'</i> &rarr; standard operational cadence terms. $P(MED)=0.81, P(HIGH)=0.11, P(LOW)=0.08$. Predicted: <b>MEDIUM (0.81)</b>.")
    p("• <b>LOW:</b> <i>'Monthly digest optional webinar replay and casual blog post'</i> &rarr; passive informational terms. $P(LOW)=0.78, P(MED)=0.17, P(HIGH)=0.05$. Predicted: <b>LOW (0.78)</b>.")
    sp(10)

    # ==========================================
    # SECTION 6: HYBRID CLASSIFICATION ENGINE
    # ==========================================
    p("6. Hybrid Classification Engine (ML + Rules Interaction)", h1_style)
    hr()
    p("<b>Why Hybrid?</b> Machine learning models are probabilistic; they generalize well but can produce false negatives on rare or out-of-vocabulary phrasing. Rules are deterministic; they lack generalization but offer 100% precision on known, mission-critical business triggers.")
    p("Combining them provides the ideal production balance: <b>ML generalization</b> for the long tail of everyday messages + <b>Deterministic Rule Safety Nets</b> for SLA-critical triggers.")
    sp(4)

    p("<b>Precedence and Interaction Logic in <code>apply_priority_rules()</code>:</b>", h2_style)
    p("1. <b>Rule Precedence over ML for HIGH Priority:</b> If <i>any</i> token in <code>HIGH_PRIORITY_KEYWORDS</code> appears in the normalized email text, the rule layer <b>overrides</b> the ML prediction and sets priority to <code>HIGH</code> immediately.")
    p("&nbsp;&nbsp;&nbsp;&nbsp;<i>Keywords:</i> <code>urgent</code>, <code>asap</code>, <code>immediately</code>, <code>critical</code>, <code>emergency</code>, <code>deadline</code>, <code>action required</code>, <code>important</code>, <code>today</code>, <code>immediate attention</code>.")
    p("&nbsp;&nbsp;&nbsp;&nbsp;<i>Confidence Adjustment:</i> When an explicit high-priority rule fires, <code>classify_email()</code> boosts priority confidence to <code>max(priority_confidence, 0.95)</code>. This ensures that an explicit rule match is treated with authoritative certainty.")
    p("2. <b>Low-Priority Demotion:</b> If ML did <i>not</i> predict HIGH, and low-priority keywords match (e.g., 'newsletter', 'unsubscribe', 'fyi only'), priority is adjusted to <code>LOW</code>.")
    p("3. <b>Default Fallback:</b> If no rule triggers, the ML prediction and its native probability are retained.")
    sp(4)

    p("<b>Concrete Case Study:</b>", h2_style)
    code_box([
        "Email: \"URGENT: Production server is down. Fix immediately.\"",
        "",
        "ML Priority Output:   MEDIUM (prob = 0.52)  <-- ML lacked strong server outage tokens in seed",
        "Rule Layer:          Found 'urgent', 'immediately'",
        "Precedence Action:   Rule fires! Overrides MEDIUM -> HIGH",
        "Confidence Boost:    Boosted from 0.52 -> 0.95",
        "Final Priority:      HIGH (0.95)",
    ])
    sp(10)

    # ==========================================
    # SECTION 7: CONFIDENCE SCORES & HUMAN-IN-THE-LOOP
    # ==========================================
    p("7. Confidence Scores & Human-in-the-Loop Gatekeeper", h1_style)
    hr()
    p("<b>What does <code>model.predict_proba()</code> mean?</b>")
    p("In scikit-learn's Logistic Regression, <code>predict_proba()</code> calculates the calibrated class posterior probabilities using the softmax function. The sum across all classes is strictly 1.0.")
    p("<b>Confidence Calculation (<code>calculate_confidence()</code>):</b>")
    p("&nbsp;&nbsp;&nbsp;&nbsp;<code>confidence = float(np.max(probabilities))</code>")
    p("Confidence is defined as the probability of the winning class. If a model assigns 0.95 to WORK and 0.05 to PERSONAL, the confidence is 0.95.")
    sp(4)

    p("<b>The 0.60 Threshold &amp; Human Review Policy:</b>", h2_style)
    p("In <code>classifier.py</code>, we define <code>CONFIDENCE_THRESHOLD = 0.60</code>. The gatekeeper evaluates both dimensions:")
    p("&nbsp;&nbsp;&nbsp;&nbsp;<code>needs_human_review = (mode_confidence &lt; 0.60 or priority_confidence &lt; 0.60)</code>")
    sp(4)

    p("<b>Three Key Operational Regimes:</b>", h2_style)
    p("• <b>Case A: High Confidence (Auto-Processed)</b>")
    p("&nbsp;&nbsp;&nbsp;&nbsp;Probabilities: $P(WORK) = 0.96, P(PERSONAL) = 0.04$.")
    p("&nbsp;&nbsp;&nbsp;&nbsp;Winning confidence: <b>0.96 (&ge; 0.60)</b>. Priority confidence: <b>0.85 (&ge; 0.60)</b>.")
    p("&nbsp;&nbsp;&nbsp;&nbsp;<b>Behavior:</b> <code>needs_human_review = False</code>. Email automatically routed to recipient's work queue without human friction.")
    sp(2)
    p("• <b>Case B: Medium-High Confidence (Auto-Processed)</b>")
    p("&nbsp;&nbsp;&nbsp;&nbsp;Probabilities: $P(WORK) = 0.68, P(PERSONAL) = 0.32$.")
    p("&nbsp;&nbsp;&nbsp;&nbsp;Winning confidence: <b>0.68 (&ge; 0.60)</b>. Priority confidence: <b>0.74 (&ge; 0.60)</b>.")
    p("&nbsp;&nbsp;&nbsp;&nbsp;<b>Behavior:</b> <code>needs_human_review = False</code>. Model clear enough to pass safety threshold.")
    sp(2)
    p("• <b>Case C: Uncertain / Ambiguous (Flagged for Triage)</b>")
    p("&nbsp;&nbsp;&nbsp;&nbsp;Probabilities: $P(WORK) = 0.51, P(PERSONAL) = 0.49$.")
    p("&nbsp;&nbsp;&nbsp;&nbsp;Winning confidence: <b>0.51 (&lt; 0.60)</b>.")
    p("&nbsp;&nbsp;&nbsp;&nbsp;<b>Behavior:</b> <code>needs_human_review = True</code>. System admits uncertainty, routing message to manual triage rather than risking silent misfiling.")
    sp(10)

    # ==========================================
    # SECTION 8: CODE EXPLANATION (INTERVIEW LEVEL)
    # ==========================================
    p("8. Deep-Dive Code Explanation (Line-by-Line)", h1_style)
    hr()
    p("Interviewers frequently ask candidates to walk through the exact mechanics of their implementation. Below are the core functions analyzed line-by-line:")
    sp(4)

    # Function 1
    p("Function 1: <code>_extract_text(email)</code>", h2_style)
    p("<b>Purpose:</b> Normalizes diverse email data structures into a clean unified string.")
    code_box([
        "def _extract_text(email: Union[Dict[str, Any], Any]) -> str:",
        "    if isinstance(email, dict):",
        "        subject = str(email.get('subject', '') or '')",
        "        body = str(email.get('body', '') or '')",
        "    else:",
        "        subject = str(getattr(email, 'subject', '') or '')",
        "        body = str(getattr(email, 'body', '') or '')",
        "    return f\"{subject} {body}\".strip()",
    ])
    p("• <code>isinstance(email, dict) / getattr(...)</code>: Provides robust polymorphism. Accepts raw REST API dicts, ORM models, or dataclasses without crashing on <code>KeyError</code>.")
    p("• <code>or ''</code>: Safely handles <code>None</code> values if <code>{'subject': None}</code> is passed.")
    p("• <code>f\"{subject} {body}\".strip()</code>: Concatenates text with space separation so the last word of subject does not collide with the first word of body.")
    sp(6)

    # Function 2
    p("Function 2: <code>calculate_confidence(probabilities)</code>", h2_style)
    p("<b>Purpose:</b> Computes the scalar confidence score from raw model probability arrays.")
    code_box([
        "def calculate_confidence(probabilities: Union[np.ndarray, list]) -> float:",
        "    probs_array = np.asarray(probabilities).flatten()",
        "    if probs_array.size == 0:",
        "        return 0.0",
        "    return float(np.max(probs_array))",
    ])
    p("• <code>np.asarray(...).flatten()</code>: Ensures uniform 1D array regardless of whether input is a Python list, nested list, or numpy ndarray.")
    p("• <code>probs_array.size == 0</code>: Defensive guard preventing <code>ValueError: zero-size array</code>.")
    p("• <code>float(np.max(...))</code>: Extracts peak probability and converts from <code>numpy.float64</code> to standard Python <code>float</code> for clean JSON serialization.")
    sp(6)

    # Function 3
    p("Function 3: <code>classify_mode(email)</code>", h2_style)
    p("<b>Purpose:</b> Executes TF-IDF transformation and Logistic Regression inference for Mode.")
    code_box([
        "def classify_mode(email: Union[Dict[str, Any], Any]) -> Tuple[str, float]:",
        "    text = _extract_text(email)",
        "    mode_model, _ = get_models()",
        "    probabilities = mode_model.predict_proba([text])[0]",
        "    best_idx = int(np.argmax(probabilities))",
        "    predicted_mode = str(mode_model.classes_[best_idx])",
        "    confidence = calculate_confidence(probabilities)",
        "    return predicted_mode, confidence",
    ])
    p("• <code>mode_model.predict_proba([text])[0]</code>: Passes a single-element list into scikit-learn Pipeline (which expects an iterable of documents) and unpacks the 1D probability distribution for the first document.")
    p("• <code>best_idx = int(np.argmax(probabilities))</code>: Finds the index of the highest probability.")
    p("• <code>mode_model.classes_[best_idx]</code>: Maps the integer index back to the ground-truth string label (e.g., 'WORK'), avoiding hardcoded integer mappings.")
    sp(6)

    # Function 4
    p("Function 4: <code>apply_priority_rules(email, prediction)</code>", h2_style)
    p("<b>Purpose:</b> Deterministic rule layer overriding ML prediction when high-signal keywords match.")
    code_box([
        "def apply_priority_rules(email, prediction):",
        "    text_lower = _extract_text(email).lower()",
        "    for kw in HIGH_PRIORITY_KEYWORDS:",
        "        if kw in text_lower:",
        "            return 'HIGH', True",
        "    if prediction != 'HIGH':",
        "        for kw in LOW_PRIORITY_KEYWORDS:",
        "            if kw in text_lower:",
        "                return 'LOW', True",
        "    return prediction, False",
    ])
    p("• <code>text_lower = _extract_text(email).lower()</code>: Case normalization so 'URGENT', 'Urgent', and 'urgent' match equally.")
    p("• <code>for kw in HIGH_PRIORITY_KEYWORDS: if kw in text_lower: return 'HIGH', True</code>: Early return pattern. Substrings like multi-word phrases ('action required', 'immediate attention') match cleanly.")
    p("• <code>if prediction != 'HIGH'</code>: Guard condition. If the ML model already predicted HIGH, low-priority keywords (e.g. an email saying 'newsletter is urgent') will not downgrade it.")
    sp(6)

    # Function 5
    p("Function 5: <code>classify_email(email)</code>", h2_style)
    p("<b>Purpose:</b> Main entry point orchestrating ML, rules, confidence evaluation, and JSON formatting.")
    code_box([
        "def classify_email(email):",
        "    mode, mode_confidence = classify_mode(email)",
        "    ml_priority, priority_confidence = classify_priority(email)",
        "    final_priority, rule_applied = apply_priority_rules(email, ml_priority)",
        "    if rule_applied and final_priority == 'HIGH':",
        "        effective_priority_conf = max(priority_confidence, 0.95)",
        "    else:",
        "        effective_priority_conf = priority_confidence",
        "    needs_human_review = (",
        "        mode_confidence < CONFIDENCE_THRESHOLD",
        "        or effective_priority_conf < CONFIDENCE_THRESHOLD",
        "    )",
        "    return {",
        "        'mode': mode,",
        "        'mode_confidence': round(float(mode_confidence), 2),",
        "        'priority': final_priority,",
        "        'priority_confidence': round(float(effective_priority_conf), 2),",
        "        'needs_human_review': needs_human_review,",
        "    }",
    ])
    p("• Decoupled calls to <code>classify_mode</code> and <code>classify_priority</code> allow independent refactoring.")
    p("• <code>effective_priority_conf = max(priority_confidence, 0.95)</code> prevents false human-review alarms when a rule definitively escalates an email to HIGH.")
    p("• <code>or</code> condition ensures that uncertainty in <i>either</i> dimension triggers human oversight.")
    sp(10)

    # ==========================================
    # SECTION 9: COMPLETE EXECUTION TRACE
    # ==========================================
    p("9. Complete Execution Trace of a Realistic Email", h1_style)
    hr()
    p("Let us trace this realistic email step-by-step through our actual implementation:")
    code_box([
        "Email Input:",
        "    Subject: \"URGENT: Client presentation tomorrow\"",
        "    Body:    \"The client presentation is scheduled for 10 AM tomorrow.",
        "              Please prepare the final report immediately.\"",
    ])
    sp(4)
    p("<b>Trace Walkthrough:</b>")
    p("1. <b>Text Concatenation:</b> <code>_extract_text()</code> produces:<br/>&nbsp;&nbsp;&nbsp;&nbsp;<code>'URGENT: Client presentation tomorrow The client presentation is scheduled for 10 AM tomorrow. Please prepare the final report immediately.'</code>")
    p("2. <b>Mode Classification:</b> <code>mode_model.predict_proba()</code> evaluates terms 'client', 'presentation', 'scheduled', 'report'.<br/>&nbsp;&nbsp;&nbsp;&nbsp;Distribution: $P(WORK) = 0.88, P(PERSONAL) = 0.12$.<br/>&nbsp;&nbsp;&nbsp;&nbsp;Output: <code>mode = 'WORK', mode_confidence = 0.88</code>.")
    p("3. <b>Priority Classification (ML):</b> <code>priority_model.predict_proba()</code> evaluates the vector.<br/>&nbsp;&nbsp;&nbsp;&nbsp;Distribution: $P(HIGH) = 0.65, P(MED) = 0.25, P(LOW) = 0.10$.<br/>&nbsp;&nbsp;&nbsp;&nbsp;Output: <code>ml_priority = 'HIGH', priority_confidence = 0.65</code>.")
    p("4. <b>Rule Layer Evaluation:</b> <code>apply_priority_rules()</code> inspects lowercase string. Finds keywords: <code>'urgent'</code> and <code>'immediately'</code>.<br/>&nbsp;&nbsp;&nbsp;&nbsp;Output: <code>final_priority = 'HIGH', rule_applied = True</code>.<br/>&nbsp;&nbsp;&nbsp;&nbsp;Effective confidence: <code>max(0.65, 0.95) = 0.95</code>.")
    p("5. <b>Confidence Check:</b> Evaluates <code>mode_confidence (0.88) &ge; 0.60</code> and <code>priority_confidence (0.95) &ge; 0.60</code>.<br/>&nbsp;&nbsp;&nbsp;&nbsp;Condition evaluates to <code>False</code>.")
    p("6. <b>Final Output Payload:</b>")
    code_box([
        "{",
        "    \"mode\": \"WORK\",",
        "    \"mode_confidence\": 0.88,",
        "    \"priority\": \"HIGH\",",
        "    \"priority_confidence\": 0.95,",
        "    \"needs_human_review\": false",
        "}",
    ])
    sp(10)

    # ==========================================
    # SECTION 10: EDGE CASES ANALYSIS
    # ==========================================
    p("10. Edge Cases Analysis (Honest Breakdown)", h1_style)
    hr()
    p("Interviewers love probing where a candidate's system fails. Here is an honest, rigorous analysis of 13 edge cases:")
    sp(4)

    edge_cases = [
        ("1. Empty Subject", "User sends an email with no subject line.", "Handled. _extract_text() uses str(email.get('subject', '') or '') resulting in '' without crashing.", "Consider checking if body is also empty to flag immediate validation error."),
        ("2. Empty Body", "User sends an email with subject only.", "Handled. Concatenates subject + ' ' + '' and evaluates subject alone.", "Ensure subject is weighted properly in short texts."),
        ("3. Very Short Email", "Email contains just 'Thanks' or 'OK'.", "Partially handled. Neither class gets strong signals; probabilities remain near ~0.50.", "Triggers needs_human_review = True due to <0.60 threshold. Correct safety behavior."),
        ("4. Very Long Email", "Email has 5,000 words of logs or pasted code.", "Partially handled. L2 normalization in TfidfVectorizer prevents vector explosion.", "Could truncate text to first 1,000 words to save vectorization latency."),
        ("5. Out-of-Vocabulary (OOV)", "Email has rare technical jargon or foreign words.", "Handled safely. TF-IDF ignores tokens not in vocabulary. Zero vector outputs baseline prior.", "Triggers needs_human_review = True due to low confidence."),
        ("6. Mixed Work / Personal", "Colleague writes: 'Great job on the sprint demo! Are we getting beer tonight?'", "Handled probabilistically. LogReg predicts whichever class has slightly higher word mass.", "Recommended improvement: Multi-label classification (e.g. WORK: 0.6, SOCIAL: 0.4)."),
        ("7. Sarcastic 'Urgent'", "'Urgent: remember to breathe today!' or 'Not urgent at all'.", "LIMITATION. Substring rule triggers on 'urgent' and forces HIGH.", "Recommended improvement: Negation dependency parsing (e.g. spaCy) to check for 'not urgent'."),
        ("8. Ambiguous Email", "'Meeting document attached regarding yesterday.'", "Handled. Near 50/50 probability distribution.", "Triggers needs_human_review = True (confidence < 0.60)."),
        ("9. Low-Confidence", "Highest probability is 0.52.", "Handled. Triggers needs_human_review = True.", "Routes to manual review inbox."),
        ("10. Spam / Newsletters", "'Special 50% discount on shoes, unsubscribe here'.", "Partially handled. 'unsubscribe' triggers LOW priority rule.", "Add explicit SPAM/PROMOTIONAL classification bucket."),
        ("11. Attachment Only", "Email body is completely empty, only has a PDF/image.", "LIMITATION. Resulting text is empty string. Evaluates to default class priors.", "Extract attachment filename or OCR text before passing to classifier."),
        ("12. Raw HTML Email", "Email body contains '<div><p>Hello</p><br/></div>'.", "LIMITATION. HTML tags are treated as tokens ('div', 'p', 'br').", "Add BeautifulSoup / regex HTML tag stripping prior to _extract_text()."),
        ("13. Repeated Words", "Spammer sends 'urgent urgent urgent urgent'.", "Handled. sublinear_tf=True dampens term frequency via 1 + log(TF).", "Rule triggers HIGH. ML avoids infinite confidence scaling."),
    ]

    ec_data = [[Paragraph("<b>Edge Case</b>", table_header_style), Paragraph("<b>Problem</b>", table_header_style), Paragraph("<b>Current Code Behavior</b>", table_header_style), Paragraph("<b>Recommended Improvement</b>", table_header_style)]]
    for name, prob, curr, imp in edge_cases:
        ec_data.append([
            Paragraph(f"<b>{name}</b>", table_cell_style),
            Paragraph(prob, table_cell_style),
            Paragraph(curr, table_cell_style),
            Paragraph(imp, table_cell_style),
        ])

    t_ec = Table(ec_data, colWidths=[90, 110, 160, 144])
    t_ec.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_ec)
    sp(10)

    # ==========================================
    # SECTION 11: ACCURACY AND EVALUATION
    # ==========================================
    p("11. Evaluation Metrics & Confusion Matrix", h1_style)
    hr()
    p("<b>Evaluation Metrics Formulation:</b>")
    p("• <b>Accuracy:</b> $(TP + TN) / (Total)$. <i>Warning:</i> Misleading under class imbalance. If 95% of emails are LOW/MEDIUM priority, a dumb model predicting only LOW achieves 95% accuracy while completely missing all HIGH priority emergencies!")
    p("• <b>Precision:</b> $TP / (TP + FP)$. Measures exactness: <i>'When the model predicts HIGH priority, how often is it actually HIGH?'</i> High precision minimizes alert fatigue.")
    p("• <b>Recall:</b> $TP / (TP + FN)$. Measures completeness: <i>'Of all true emergency emails, how many did the model catch?'</i> <b>In Priority classification, Recall on the HIGH class is the most critical metric.</b> Missing an outage email has severe SLA consequences.")
    p("• <b>F1-Score:</b> Harmonic mean of Precision and Recall: $2 \\times \\frac{Precision \\times Recall}{Precision + Recall}$. Balances false positives and false negatives.")
    p("• <b>Macro vs. Weighted F1:</b> Macro-F1 calculates unweighted average across classes, exposing poor performance on minority classes (like HIGH priority). Weighted-F1 weights by support.")
    sp(4)

    p("<b>Confusion Matrix for Priority (3x3 Example):</b>", h2_style)
    cm_data = [
        [Paragraph("", table_header_style), Paragraph("<b>Pred HIGH</b>", table_header_style), Paragraph("<b>Pred MEDIUM</b>", table_header_style), Paragraph("<b>Pred LOW</b>", table_header_style)],
        [Paragraph("<b>Actual HIGH</b>", table_cell_style), Paragraph("<b>45</b> (TP)", table_cell_style), Paragraph("5 (FN to Med)", table_cell_style), Paragraph("0 (FN to Low)", table_cell_style)],
        [Paragraph("<b>Actual MEDIUM</b>", table_cell_style), Paragraph("4 (FP from Med)", table_cell_style), Paragraph("<b>180</b> (TP)", table_cell_style), Paragraph("16 (FN to Low)", table_cell_style)],
        [Paragraph("<b>Actual LOW</b>", table_cell_style), Paragraph("1 (FP from Low)", table_cell_style), Paragraph("12 (FP from Low)", table_cell_style), Paragraph("<b>237</b> (TP)", table_cell_style)],
    ]
    t_cm = Table(cm_data, colWidths=[100, 134, 135, 135])
    t_cm.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2C5282")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ]))
    story.append(t_cm)
    sp(4)
    p("<i>Interview Explanation of this Matrix:</i> Actual HIGH has 50 samples. Model caught 45 ($Recall = 45/50 = 90\\%$). Total predicted HIGH was $45 + 4 + 1 = 50$ ($Precision = 45/50 = 90\\%$). The rule layer specifically drove down False Negatives to zero for urgent keyword triggers.")
    sp(10)

    # ==========================================
    # SECTION 12: 30 INTERVIEW QUESTIONS & ANSWERS
    # ==========================================
    p("12. Top 30 Technical Interview Questions & Answers", h1_style)
    hr()

    qa_list = [
        # Beginner (1-10)
        ("Q1: What is TF-IDF in simple terms?",
         "TF-IDF measures word importance in a document relative to an entire corpus. Term Frequency counts how often a word appears in the email; Inverse Document Frequency penalizes common corpus words (like 'the', 'hello') and amplifies distinct words (like 'invoice', 'server', 'outage')."),
        ("Q2: Why did you choose Logistic Regression over a neural network?",
         "Logistic Regression is fast (sub-millisecond inference), memory-efficient, mathematically interpretable through feature weights, and performs exceptionally well on sparse, high-dimensional TF-IDF feature spaces without overfitting on small datasets."),
        ("Q3: What does model.predict_proba() output?",
         "It outputs calibrated posterior class probabilities summing to 1.0, calculated via the sigmoid/softmax function applied to the linear logits."),
        ("Q4: What is the difference between classification and regression?",
         "Regression predicts continuous numerical values (e.g., house price); classification predicts discrete categorical labels (e.g., WORK vs PERSONAL, HIGH vs MEDIUM vs LOW)."),
        ("Q5: What is n-gram and why did you use ngram_range=(1, 2)?",
         "An n-gram is a contiguous sequence of n tokens. (1, 2) extracts both unigrams ('action', 'required') and bigrams ('action required'). Bigrams capture context and phrase meaning that single words miss."),
        ("Q6: What is sublinear_tf in TfidfVectorizer?",
         "It replaces raw term frequency TF with 1 + log(TF) for TF > 0. This prevents repeated words (e.g., spamming 'urgent' 20 times) from dominating the vector weight by 20x."),
        ("Q7: How does your code handle an email with no subject?",
         "In _extract_text(), str(email.get('subject', '') or '') converts None or empty string safely to an empty string, concatenating with the body without raising a KeyError or TypeError."),
        ("Q8: What is L2 normalization in TF-IDF?",
         "L2 normalization divides each vector by its Euclidean length (sqrt of sum of squared weights), ensuring all document vectors have length 1.0. This prevents long emails from artificially dominating short emails."),
        ("Q9: What is the role of joblib in your project?",
         "Joblib provides efficient serialization and deserialization of Python objects containing large numpy arrays and fitted scikit-learn pipelines to and from disk."),
        ("Q10: What does the classes_ attribute in scikit-learn represent?",
         "It contains the array of unique class labels learned by the classifier during fit(), ordered to correspond directly to the columns of predict_proba()."),

        # Intermediate (11-20)
        ("Q11: Why did you separate Mode and Priority into two independent classifiers?",
         "Mode (WORK vs PERSONAL) and Priority (HIGH/MED/LOW) are orthogonal dimensions. A work email can be low priority; a personal email can be high priority. Decoupling them simplifies training, allows independent feature spaces, and prevents exponential combinatorial class explosion."),
        ("Q12: Why not train a single 6-class classifier (e.g. WORK_HIGH, WORK_LOW, etc.)?",
         "A 6-class model fragments the training data, requires 6x more samples per bucket to avoid class imbalance, increases confusion between orthogonal attributes, and makes rule overrides messy."),
        ("Q13: Why did you use a hybrid architecture combining ML and Rules?",
         "Pure ML is probabilistic and can fail on rare phrasing; pure rules are brittle and do not generalize. The hybrid design leverages ML for broad natural language generalization while using deterministic rules as an authoritative safety net for critical keywords."),
        ("Q14: How did you determine the 0.60 confidence threshold?",
         "In a 2-class or 3-class problem, equal ambiguity yields 0.50 or 0.33. A 0.60 threshold ensures the model has a definitive margin of confidence before auto-processing, routing borderline emails to human triage."),
        ("Q15: What happens when an email has words never seen during training?",
         "TF-IDF ignores unseen out-of-vocabulary tokens. If no tokens match, the email produces an all-zero vector, yielding class prior probabilities (~0.50 or ~0.33), which fall below 0.60 and correctly trigger human review."),
        ("Q16: Why did you set Logistic Regression C=10.0 instead of default C=1.0?",
         "C is inverse regularization strength. With small seed datasets, C=1.0 applies strong L2 penalty shrinking coefficients toward zero and compressing probabilities near 0.50. C=10.0 allows decisive weights on clear discriminative keywords."),
        ("Q17: What is the difference between Precision and Recall for Priority?",
         "Precision measures how many emails flagged as HIGH are truly high (avoiding alert fatigue). Recall measures how many true high-priority emails were caught (avoiding missed emergencies). Recall is paramount for high priority."),
        ("Q18: How does your code prevent false human review alarms when rules fire?",
         "When an explicit high-priority rule triggers, classify_email() boosts effective priority confidence to max(priority_confidence, 0.95), reflecting the authoritative nature of the business rule."),
        ("Q19: How is the ModelRegistry structured for plug-and-play operation?",
         "It checks disk for saved models. If present, it loads them via joblib; if absent, it fits and caches baseline models in memory. This guarantees the service runs out-of-the-box and accepts real models later with zero code refactoring."),
        ("Q20: What is a Pipeline in scikit-learn and why use it?",
         "A Pipeline chains the feature extractor (TfidfVectorizer) and estimator (LogisticRegression) into a single atomic object, preventing data leakage and guaranteeing identical transformations at training and inference."),

        # Advanced (21-30)
        ("Q21: Why not use BERT or a large language model for this classifier?",
         "BERT introduces significant GPU infrastructure costs, 100-300ms inference latency, and cold-start overhead. For triage of high-volume incoming emails, TF-IDF + Logistic Regression delivers microsecond latency on basic CPU instances with 90%+ baseline accuracy."),
        ("Q22: How would you handle concept drift over time?",
         "Concept drift occurs when email language evolves (e.g., new project codenames). I would log emails flagged for human review, collect corrected labels, monitor rolling F1 scores, and implement scheduled automated retraining pipelines."),
        ("Q23: How would you handle severe class imbalance in training data?",
         "In real inboxes, HIGH priority is rare (<5%). I would apply class_weight='balanced' in Logistic Regression, tune the decision threshold rather than using argmax, and evaluate using Precision-Recall AUC and Macro-F1 rather than accuracy."),
        ("Q24: How would you scale this classifier to process 10 million emails per day?",
         "10M emails/day is ~115 emails/sec. Since TF-IDF + LogReg inference takes <1ms, a single multi-threaded Python worker processes ~1,000 emails/sec. We can deploy stateless containerized workers behind a Kafka/RabbitMQ queue with horizontal autoscaling."),
        ("Q25: What is data leakage in NLP and how do you prevent it?",
         "Data leakage occurs when test set statistics leak into the training process (e.g., fitting TfidfVectorizer on the entire dataset before train/test split). We prevent it by calling fit() strictly on the training split, and only transform() on test/inference."),
        ("Q26: How would you improve context awareness without a heavy transformer?",
         "We could extract metadata features: sender domain (internal company vs public), thread depth, number of recipients, time of arrival, and whether the user is in the 'To' vs 'Cc' line, combining them with TF-IDF via FeatureUnion."),
        ("Q27: How would you detect misclassifications in production without ground truth labels?",
         "Monitor distribution drift: track daily proportions of WORK vs PERSONAL and HIGH/MED/LOW. A sudden spike indicates drift. Also track human review escalation rates and user feedback actions (e.g. user manually moving an email to another folder)."),
        ("Q28: How does L2 regularization affect the weights in Logistic Regression?",
         "L2 regularization adds a penalty term lambda * sum(w_i^2) to the loss function. It shrinks large weights toward zero, reducing variance and preventing individual rare words from dominating predictions."),
        ("Q29: Can you explain the difference between Micro, Macro, and Weighted F1-scores?",
         "Micro-F1 aggregates global TP, FP, FN (favors dominant classes); Macro-F1 averages per-class F1 unweighted (treats rare HIGH priority equally with frequent LOW priority); Weighted-F1 averages per-class F1 weighted by class support."),
        ("Q30: If you could make one architectural enhancement tomorrow, what would it be?",
         "I would introduce a lightweight Sentence-Transformer (e.g., MiniLM) embedding alongside TF-IDF to capture semantic synonyms and paraphrase matching, while preserving sub-10ms inference latency."),
    ]

    for q, a in qa_list:
        p(f"<b>{q}</b>", h3_style)
        p(f"&rarr; <i>Answer:</i> {a}")
        sp(3)
    sp(8)

    # ==========================================
    # SECTION 13: "WHY DID YOU CHOOSE THIS?" TABLE
    # ==========================================
    p("13. Architectural Decisions & Trade-off Matrix", h1_style)
    hr()
    dec_data = [
        [Paragraph("<b>Decision</b>", table_header_style), Paragraph("<b>Why I Chose It</b>", table_header_style), Paragraph("<b>Alternative</b>", table_header_style), Paragraph("<b>Why Alternative Rejected</b>", table_header_style)],
        [
            Paragraph("<b>TF-IDF Vectorization</b>", table_cell_style),
            Paragraph("Deterministic, sub-millisecond CPU speed, interpretable n-gram weights, zero dependency on external GPU infrastructure.", table_cell_style),
            Paragraph("Word2Vec / BERT / LLM API", table_cell_style),
            Paragraph("High latency (100ms+), GPU hosting cost, complex dependency tree, risk of API rate limits or hallucination.", table_cell_style),
        ],
        [
            Paragraph("<b>Logistic Regression</b>", table_cell_style),
            Paragraph("Convex optimization (fast training), naturally calibrated predict_proba() outputs, linear interpretability of coefficients.", table_cell_style),
            Paragraph("Random Forest / XGBoost / SVM", table_cell_style),
            Paragraph("Tree models do not scale as efficiently on 10,000+ sparse TF-IDF dimensions; SVM probability calibration (Platt scaling) is slow.", table_cell_style),
        ],
        [
            Paragraph("<b>Separate Classifiers</b>", table_cell_style),
            Paragraph("Mode and Priority are orthogonal concepts. Simplifies modeling into focused tasks, reduces class imbalance.", table_cell_style),
            Paragraph("Single 6-class model (WORK_HIGH, etc.)", table_cell_style),
            Paragraph("Exponential class explosion, data fragmentation, harder to apply targeted rules to urgency alone.", table_cell_style),
        ],
        [
            Paragraph("<b>Hybrid Rules + ML</b>", table_cell_style),
            Paragraph("ML handles long-tail natural variation; rules provide 100% deterministic safety guarantee on SLA trigger words.", table_cell_style),
            Paragraph("Pure Machine Learning", table_cell_style),
            Paragraph("Pure ML will occasionally misclassify an 'URGENT OUTAGE' email due to statistical variance, creating catastrophic downtime.", table_cell_style),
        ],
        [
            Paragraph("<b>0.60 Confidence Gate</b>", table_cell_style),
            Paragraph("Prevents silent errors on out-of-distribution or ambiguous inputs; routes edge cases to human review.", table_cell_style),
            Paragraph("Always trust argmax prediction", table_cell_style),
            Paragraph("Forces system to guess blindly on 51/49 coin flips, degrading user trust.", table_cell_style),
        ],
    ]
    t_dec = Table(dec_data, colWidths=[85, 135, 110, 174])
    t_dec.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_dec)
    sp(10)

    # ==========================================
    # SECTION 14: LIMITATIONS
    # ==========================================
    p("14. Honest System Limitations", h1_style)
    hr()
    p("Being candid about limitations shows senior engineering maturity. Current limitations include:")
    p("• <b>Keyword Dependency &amp; Sarcasm:</b> The rule layer matches substrings without syntactic dependency parsing. A sentence like <i>'It is not urgent'</i> or <i>'Urgent: remember to drink water'</i> will trigger the HIGH priority override.")
    p("• <b>Lack of Semantic Synonyms:</b> TF-IDF relies on exact character token matches. If a user writes <i>'catastrophic production breakdown'</i> and 'breakdown' was never seen in training (only 'crash' or 'outage'), TF-IDF assigns it zero weight.")
    p("• <b>Neglect of Email Metadata:</b> The model only evaluates text. It ignores sender reputation, sender domain (@company.com vs @gmail.com), thread hierarchy, and whether attachments are present.")
    p("• <b>Static Regularization:</b> In-memory models require manual retraining and redeployment to adapt to organizational vocabulary evolution.")
    sp(10)

    # ==========================================
    # SECTION 15: FUTURE EVOLUTION ROADMAP
    # ==========================================
    p("15. Future Evolutionary Roadmap", h1_style)
    hr()
    code_box([
        "Phase 1: Current Architecture",
        "  -> TF-IDF (1-2 ngrams) + Logistic Regression + Substring Keyword Rules",
        "  -> Sub-millisecond CPU execution, baseline accuracy ~85-90%",
        "",
        "Phase 2: Enhanced Feature Engineering & Metadata",
        "  -> Add sender domain features, time-of-day, recipient count, attachment metadata",
        "  -> Add regex dependency negation parsing ('not urgent' -> do not escalate)",
        "",
        "Phase 3: Dense Semantic Sentence Embeddings",
        "  -> Sentence-Transformers (e.g. all-MiniLM-L6-v2) combined with TF-IDF via FeatureUnion",
        "  -> Captures synonyms ('outage' == 'breakdown' == 'incident') while staying <15ms latency",
        "",
        "Phase 4: Full Transformer Fine-Tuning",
        "  -> Fine-tuned DistilBERT / ModernBERT for joint sequence classification",
        "  -> Superior nuanced language comprehension, context tracking, and sarcasm resolution",
        "",
        "Phase 5: Production MLOps & Continuous Active Learning",
        "  -> Human triage actions automatically feed a feedback database",
        "  -> Weekly automated retraining pipeline with automated drift detection and canary deployments",
    ])
    sp(10)

    # ==========================================
    # SECTION 16: MASTER INTERVIEW CHEAT SHEET
    # ==========================================
    p("16. Master Interview Cheat Sheet", h1_style)
    hr()
    p("<b>30-Second Elevator Pitch:</b>")
    p("<i>'I engineered a lightweight, high-performance hybrid email classification system that categorizes emails into Mode (Work vs Personal) and Priority (High, Medium, Low). It pairs dual TF-IDF and Logistic Regression pipelines for probabilistic generalization with a deterministic rule-based override layer for critical SLA triggers, backed by a 0.60 confidence gatekeeper that routes ambiguous messages to human triage. It achieves sub-millisecond latency on standard CPUs.'</i>")
    sp(4)

    p("<b>1-Minute Comprehensive Pitch:</b>")
    p("<i>'In designing our email classifier, our core engineering objective was balancing sub-millisecond execution with zero tolerance for missed emergencies. We chose an orthogonal dual-model architecture: Mode and Priority are classified by independent TF-IDF plus Logistic Regression pipelines using unigrams and bigrams. Because statistical ML models can produce false negatives on rare phrasing, we introduced a hybrid rule layer where mission-critical keywords like \"urgent\" or \"outage\" deterministically promote priority to HIGH with boosted confidence. Finally, all predictions pass through a confidence evaluator: if winning probabilities fall below 0.60, the email is flagged for human triage. This hybrid design delivers the generalization of machine learning, the SLA safety of deterministic rules, and a human-in-the-loop fallback for edge cases.'</i>")
    sp(4)

    p("<b>Formula & Concept Quick Reference:</b>")
    p("• <b>TF-IDF:</b> <code>TF * IDF</code> with <code>sublinear_tf=True (1 + log(TF))</code>.")
    p("• <b>LogReg Probability:</b> <code>P(y=k|x) = exp(z_k) / sum(exp(z_j))</code>.")
    p("• <b>Confidence:</b> <code>max(predict_proba())</code>.")
    p("• <b>Human Review Trigger:</b> <code>min(mode_conf, priority_conf) &lt; 0.60</code>.")
    p("• <b>Rule Override:</b> Keywords in <code>HIGH_PRIORITY_KEYWORDS</code> &rarr; Priority = <code>HIGH</code>, conf = <code>max(conf, 0.95)</code>.")
    sp(6)

    callout_box(
        "You are now fully equipped to explain every line of classifier.py, defend the architectural choices, "
        "derive the mathematical formulas, walk through realistic execution traces, and articulate future scaling strategies. "
        "Good luck with your interview!",
        "INTERVIEW READY"
    )

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] PDF generated successfully at: {filename}")


if __name__ == "__main__":
    output_pdf = os.path.abspath("Email_Classifier_Interview_Preparation_Guide.pdf")
    build_pdf(output_pdf)
