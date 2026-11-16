# -*- coding: utf-8 -*-
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.barcode import qr

# Page dimensions
PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 40
USABLE_WIDTH = PAGE_WIDTH - 2 * MARGIN

# Color Palette matching the reference cookbook design
PRIMARY = colors.HexColor("#0B3954")       # Deep Navy Blue
SECONDARY = colors.HexColor("#087E8B")     # Teal accent
ACCENT = colors.HexColor("#006699")        # Medium Blue
DARK_TEXT = colors.HexColor("#1A202C")     # Charcoal body text
LIGHT_BG = colors.HexColor("#F8FAFC")      # Code/callout background
BORDER_COLOR = colors.HexColor("#CBD5E1")  # Subtle borders
NOTE_BG = colors.HexColor("#F0F9FF")       # Note box background
NOTE_BORDER = colors.HexColor("#0284C7")   # Note border cyan/blue
SUCCESS_COLOR = colors.HexColor("#166534") # Forest Green
TABLE_HEADER_BG = colors.HexColor("#0B3954")
TABLE_ROW_ALT = colors.HexColor("#F1F5F9")
CODE_BG = colors.HexColor("#F1F5F9")

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and render running header & footer.
    """
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
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, total_pages):
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(PRIMARY)
            self.drawString(MARGIN, PAGE_HEIGHT - 26, "Geo-Distributed Active-Active Cache Cluster")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(MARGIN + 215, PAGE_HEIGHT - 26, "•  Architectural Blueprint & Engineering Cookbook")
            
            self.setStrokeColor(BORDER_COLOR)
            self.setLineWidth(0.6)
            self.line(MARGIN, PAGE_HEIGHT - 32, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 32)
            
            # Running Footer
            self.line(MARGIN, 34, PAGE_WIDTH - MARGIN, 34)
            self.drawString(MARGIN, 22, "ACC MiniProject • Multi-Region CRDT Cache (SDG 9)")
            page_text = f"Page {self._pageNumber} of {total_pages}"
            self.drawRightString(PAGE_WIDTH - MARGIN, 22, page_text)
            self.restoreState()

def create_code_block(code_text, styles):
    """Formats code or terminal output inside a styled, bordered box."""
    code_style = ParagraphStyle(
        'CodeText',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.2,
        leading=9.2,
        textColor=colors.HexColor("#0F172A"),
        wordWrap='CJK'
    )
    # Escape xml entities
    formatted = code_text.strip().replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    formatted = formatted.replace('\n', '<br/>').replace(' ', '&nbsp;')
    p = Paragraph(formatted, code_style)
    
    t = Table([[p]], colWidths=[USABLE_WIDTH])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CODE_BG),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    return t

def create_note_box(note_text, styles, title="Note"):
    """Creates a callout box with a prominent left accent border."""
    title_style = ParagraphStyle(
        'NoteTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=PRIMARY
    )
    body_style = ParagraphStyle(
        'NoteBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=DARK_TEXT
    )
    content = [
        Paragraph(f"<b>{title}:</b> {note_text}", body_style)
    ]
    t = Table([[content]], colWidths=[USABLE_WIDTH])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NOTE_BG),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#BAE6FD")),
        ('LINEBEFORE', (0,0), (0,0), 3.5, NOTE_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    return t

def get_qr_drawing(url, size=65):
    """Generates a QR code drawing for links."""
    qr_code = qr.QrCodeWidget(url)
    bounds = qr_code.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    d = Drawing(size, size, transform=[size/width, 0, 0, size/height, 0, 0])
    d.add(qr_code)
    return d

def build_pdf(filename="Geo_Distributed_Cache_Cookbook.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN
    )

    styles = getSampleStyleSheet()

    # Custom styles
    h1_style = ParagraphStyle(
        'CoverH1',
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=PRIMARY,
        spaceAfter=4
    )
    sub_style = ParagraphStyle(
        'CoverSub',
        fontName='Helvetica',
        fontSize=13,
        leading=16,
        textColor=ACCENT,
        spaceAfter=12
    )
    lead_style = ParagraphStyle(
        'CoverLead',
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=DARK_TEXT,
        spaceAfter=14
    )
    sec_title = ParagraphStyle(
        'SectionTitle',
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=PRIMARY,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    subsec_title = ParagraphStyle(
        'SubSectionTitle',
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13.5,
        textColor=ACCENT,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyDark',
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=DARK_TEXT,
        spaceAfter=6
    )
    bullet_style = ParagraphStyle(
        'BulletText',
        fontName='Helvetica',
        fontSize=8.2,
        leading=11,
        textColor=DARK_TEXT,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    story = []

    # =========================================================
    # PAGE 1: COVER & BLUEPRINT SUMMARY
    # =========================================================
    # Top mini header
    top_meta = Paragraph(
        "<font size=8 color='#64748B'><b>VESIT DEPARTMENT OF COMPUTER ENGINEERING • ADVANCED CLOUD COMPUTING (ACC)</b></font>",
        body_style
    )
    story.append(top_meta)
    story.append(Spacer(1, 6))

    story.append(Paragraph("Geo-Distributed Active-Active Cache Cluster", h1_style))
    story.append(Paragraph("Architectural Blueprint & Engineering Cookbook", sub_style))

    story.append(Paragraph(
        "A production-grade implementation guide to building, containerizing, deploying, and operating a high-throughput, "
        "conflict-free geo-distributed cache cluster on AWS EC2 and local Docker. Based on the <b>vedaXD/ACC-Miniproject</b> "
        "repository. Covers Hybrid Logical Clock (HLC) mathematics, CRDT conflict resolution (LWW-Register and PN-Counter), "
        "asynchronous write-behind replication, and multi-region fault tolerance.",
        lead_style
    ))

    # Video link banner with QR code
    qr_draw = get_qr_drawing("https://youtu.be/OwtLWvFsUC4", size=60)
    video_banner_text = Paragraph(
        "<b>🔴 Live Demonstration Video & Verification</b><br/>"
        "<font size=8 color='#0369A1'>Watch the 3-region active-active cluster in action: concurrent LWW writes, PN-counter "
        "increments, and worker outage recovery.</font><br/>"
        "<font size=8><b>YouTube Link:</b> <a href='https://youtu.be/OwtLWvFsUC4' color='#0284C7'><u>https://youtu.be/OwtLWvFsUC4</u></a></font><br/>"
        "<font size=8><b>GitHub Repo:</b> <a href='https://github.com/vedaXD/ACC-Miniproject' color='#0284C7'><u>https://github.com/vedaXD/ACC-Miniproject</u></a></font>",
        body_style
    )
    video_table = Table([[qr_draw, video_banner_text]], colWidths=[70, USABLE_WIDTH - 70])
    video_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NOTE_BG),
        ('BOX', (0,0), (-1,-1), 0.75, NOTE_BORDER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(video_table)
    story.append(Spacer(1, 10))

    # Stack Table (Matching Reference Page 1)
    stack_data = [
        [Paragraph("<b>Stack Component</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Technology / Implementation</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Architectural Role in Cluster</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white))],
        [Paragraph("In-Memory Cache", body_style), Paragraph("Redis 7 (Alpine)", body_style), Paragraph("Local sub-millisecond in-memory data store for keys & counters", body_style)],
        [Paragraph("Replication Gateway", body_style), Paragraph("Python 3.11 + Flask", body_style), Paragraph("Client API (/set, /get, /incr, /counter) and HTTP /sync engine", body_style)],
        [Paragraph("Causal Clock", body_style), Paragraph("Hybrid Logical Clock (HLC)", body_style), Paragraph("Generates monotonic timestamps (physical_ms, counter, node_id)", body_style)],
        [Paragraph("Key-Value CRDT", body_style), Paragraph("LWW-Register", body_style), Paragraph("Last-Write-Wins deterministic merge with node-ID tie breaker", body_style)],
        [Paragraph("Counter CRDT", body_style), Paragraph("State-Based PN-Counter", body_style), Paragraph("Positive-Negative counters with idempotent per-node maxima merging", body_style)],
        [Paragraph("Replication Engine", body_style), Paragraph("Asynchronous Write-Behind", body_style), Paragraph("Immediate local writes; background 500ms push (capped at 5,000)", body_style)],
        [Paragraph("Cloud Infrastructure", body_style), Paragraph("AWS EC2 (3 Regions)", body_style), Paragraph("Multi-master deployment across US, Europe, and Asia regions", body_style)],
        [Paragraph("Local Orchestration", body_style), Paragraph("Docker Compose", body_style), Paragraph("Zero-config multi-container cluster setup (ports 5001-5003)", body_style)],
    ]
    stack_table = Table(stack_data, colWidths=[120, 140, USABLE_WIDTH - 260])
    stack_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TABLE_HEADER_BG),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, TABLE_ROW_ALT]),
    ]))
    story.append(stack_table)
    story.append(Spacer(1, 10))

    # Authors & Academic Details Box
    meta_data = [
        [Paragraph("<b>Project Details:</b> Advanced Cloud Computing (ACC) • Course Code: Sem 7, 2026 • Group No: 6<br/>"
                   "<b>Institute:</b> Vivekanand Education Society's Institute of Technology (VESIT), Mumbai<br/>"
                   "<b>Project Mentor:</b> Prof. Richard Joseph • <b>UN SDG Alignment:</b> SDG 9 (Industry, Innovation & Infrastructure)<br/>"
                   "<b>Team Members:</b> Veda Patki (Roll 43), Akul Patre (Roll 44), Isha Palkar (Roll 37), Soham Patil (Roll 40)",
                   ParagraphStyle('MetaStyle', fontName='Helvetica', fontSize=7.5, leading=10, textColor=colors.HexColor("#334155")))]
    ]
    meta_table = Table(meta_data, colWidths=[USABLE_WIDTH])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)

    story.append(PageBreak())

    # =========================================================
    # PAGE 2: TABLE OF CONTENTS
    # =========================================================
    story.append(Paragraph("Table of Contents", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    toc_items = [
        ("1. Architecture & System Design Philosophy", "3"),
        ("2. Data Flow & Component Interactions", "4"),
        ("3. Required Tools & Environment Prerequisites", "5"),
        ("Recipe 1: Local Multi-Container Development & Cluster Setup", "6"),
        ("Recipe 2: Multi-Region Cloud Deployment on AWS EC2", "7"),
        ("Recipe 3: Hybrid Logical Clocks (HLC) Mathematical Design", "8"),
        ("Recipe 4: LWW-Register CRDT for Key-Value Data", "9"),
        ("Recipe 5: State-Based PN-Counter CRDT for Distributed Counters", "10"),
        ("Recipe 6: Asynchronous Write-Behind Replication Engine & Buffer Capping", "11"),
        ("Recipe 7: Concurrent Conflicting Writes Verification (01-lww-demo.ps1)", "12"),
        ("Recipe 8: Concurrent Counter Increments Verification (02-pn-counter-demo.ps1)", "13"),
        ("Recipe 9: Fault Tolerance & Outage Recovery (03-worker-outage-recovery.ps1)", "14"),
        ("Recipe 10: Multi-Region Latency & Convergence Benchmarking", "15"),
        ("Quick Reference Cheat Sheet: REST APIs & Configuration", "16"),
    ]

    toc_data = []
    for title, page in toc_items:
        toc_data.append([
            Paragraph(f"<b>{title}</b>", body_style),
            Paragraph(f"<b>{page}</b>", ParagraphStyle('PageNum', parent=body_style, alignment=2))
        ])

    toc_table = Table(toc_data, colWidths=[USABLE_WIDTH - 40, 40])
    toc_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(toc_table)

    story.append(Spacer(1, 15))
    story.append(Paragraph("System Specification Highlights", subsec_title))
    story.append(Paragraph("• <b>Multi-Master Active-Active:</b> Every region accepts both reads and writes locally with zero cross-continent latency on client write.", bullet_style))
    story.append(Paragraph("• <b>Coordination-Free Convergence:</b> State-based CRDTs guarantee that replicas independently reach identical states without Paxos, Raft, or distributed locks.", bullet_style))
    story.append(Paragraph("• <b>Clock-Skew Resilient:</b> Hybrid Logical Clocks (HLC) provide monotonic, causality-preserving total order without requiring specialized atomic clocks.", bullet_style))
    story.append(Paragraph("• <b>Partition Tolerant (AP):</b> Isolated nodes continue serving local reads and writes; updates queue up and reconcile seamlessly upon network healing.", bullet_style))
    story.append(Paragraph("• <b>Memory Safety:</b> In-memory write-behind buffers are strictly bounded to 5,000 deltas to avoid Out-Of-Memory (OOM) failures under long partitions.", bullet_style))

    story.append(PageBreak())

    # =========================================================
    # PAGE 3: SECTION 1 - ARCHITECTURE & DESIGN PHILOSOPHY
    # =========================================================
    story.append(Paragraph("1. Architecture & System Design Philosophy", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph("The Core Problem: Single-Region Latency vs. Multi-Master Replication", subsec_title))
    story.append(Paragraph(
        "Modern internet applications serve globally distributed users across continents. However, conventional caching "
        "layers rely on a single primary instance hosted in one cloud region (e.g., US). A user in India or Europe accessing "
        "a primary in North America incurs a mandatory <b>400ms – 550ms round-trip latency penalty</b> on every request. "
        "Furthermore, if the central region or the transatlantic fiber link fails, global clients lose write availability completely.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Active-Active (Multi-Master) Geo-Replication</b> solves this latency barrier by hosting fully functional replicas "
        "in every geographic region. Clients read and write to their closest geographic node with sub-millisecond local latency. "
        "However, multi-master systems introduce a fundamental concurrency challenge: concurrent, conflicting writes to the "
        "same key at different nodes must be resolved deterministically without a central coordinator.",
        body_style
    ))

    story.append(Paragraph("Architectural Invariants of this System", subsec_title))
    story.append(Paragraph(
        "<b>1. Local-First Write Latency:</b> Client writes are committed to the local Redis instance immediately and acknowledged "
        "to the caller with HTTP 200. Replicating updates across continents never blocks local request execution.",
        bullet_style
    ))
    story.append(Paragraph(
        "<b>2. AP Availability under CAP Theorem:</b> In accordance with Brewer's Conjecture, during network partitions the system "
        "prioritizes <i>Availability</i> and <i>Partition Tolerance</i>. Isolated nodes accept writes locally; eventual consistency "
        "is restored automatically once communication is re-established.",
        bullet_style
    ))
    story.append(Paragraph(
        "<b>3. Hybrid Logical Clock (HLC) Total Ordering:</b> Wall-clock time alone cannot order distributed events due to NTP "
        "drifts, leap seconds, and virtual machine clock jitter. The system attaches a tuple <i>(physical_ms, logical_counter, node_id)</i> "
        "to every write, creating a strict monotonic total order.",
        bullet_style
    ))
    story.append(Paragraph(
        "<b>4. Conflict-Free Replicated Data Types (CRDTs):</b> State merges rely on mathematical semilattices satisfying "
        "commutativity ($A \\vee B = B \\vee A$), associativity ($(A \\vee B) \\vee C = A \\vee (B \\vee C)$), and idempotency ($A \\vee A = A$). "
        "LWW-Register resolves key-value conflicts; PN-Counter merges distributed increments without losing counts.",
        bullet_style
    ))
    story.append(Paragraph(
        "<b>5. Asynchronous Write-Behind with Delta Capping:</b> Changes are accumulated in an in-memory queue and dispatched "
        "every 500 ms via HTTP POST /sync. To prevent unbounded memory expansion during protracted partitions, buffers are capped at 5,000 deltas.",
        bullet_style
    ))

    story.append(Spacer(1, 6))
    story.append(create_note_box(
        "<b>Key Takeaway for System Evaluators:</b> The cache cluster trades immediate linearizability for sub-millisecond local write latency and 100% partition availability. Causality is strictly preserved via HLC, and eventual convergence is mathematically guaranteed via CRDT semilattices.",
        styles, title="Architectural Tradeoff"
    ))

    story.append(PageBreak())

    # =========================================================
    # PAGE 4: SECTION 2 - DATA FLOW & COMPONENT INTERACTIONS
    # =========================================================
    story.append(Paragraph("2. Data Flow & Component Interactions", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph("End-to-End Replication Architecture", subsec_title))
    
    ascii_diagram = """
    +---------------------------------------------------------------------------------------------------------+
    |                                   GEO-DISTRIBUTED ACTIVE-ACTIVE REPLICATION PIPELINE                    |
    +---------------------------------------------------------------------------------------------------------+
    
      [Local Client in US]                 [Local Client in EU]               [Local Client in Asia]
             | (HTTP POST /set)                   | (HTTP POST /set)                 | (HTTP POST /incr)
             v                                    v                                  v
    +-----------------------+            +-----------------------+          +-----------------------+
    | AWS US: us-east-1     |            | AWS Europe: eu-west-1 |          | AWS Asia: ap-se-1     |
    | EC2: 54.242.141.54    |            | EC2: 34.241.36.71     |          | EC2: 52.77.218.56     |
    |                       |            |                       |          |                       |
    |  +-----------------+  |            |  +-----------------+  |          |  +-----------------+  |
    |  |  Flask Worker   |  |            |  |  Flask Worker   |  |          |  |  Flask Worker   |  |
    |  |  (app.py :5000) |  |            |  |  (app.py :5000) |  |          |  |  (app.py :5000) |  |
    |  +--------+--------+  |            +--------+--------+  |          +--------+--------+  |
    |           |           |                     |           |                   |           |
    |    (1) Tick HLC       |              (1) Tick HLC       |            (1) Tick HLC       |
    |    (2) Local Redis SET|              (2) Local Redis SET|            (2) Local Redis SET|
    |    (3) Buffer Delta   |              (3) Buffer Delta   |            (3) Buffer Delta   |
    |           |           |                     |           |                   |           |
    |  +--------v--------+  |            |  +--------v--------+  |          |  +--------v--------+  |
    |  | Redis 7 Storage |  |            |  | Redis 7 Storage |  |          |  | Redis 7 Storage |  |
    |  | (redis:7-alpine)|  |            |  | (redis:7-alpine)|  |          |  | (redis:7-alpine)|  |
    |  +-----------------+  |            |  +-----------------+  |          |  +-----------------+  |
    |           |           |                     |           |                   |           |
    |   [Write-Behind Buf]  |            |   [Write-Behind Buf]  |          |   [Write-Behind Buf]  |
    |   (max 5000 deltas)   |            |   (max 5000 deltas)   |          |   (max 5000 deltas)   |
    +-----------+-----------+            +-----------+-----------+          +-----------+-----------+
                |                                    |                                  |
                |====== HTTP POST /sync (500ms) =====+====== HTTP POST /sync (500ms) ===|
                |                                    |                                  |
                +------------------------------------+----------------------------------+
                                        Inter-Region Mesh Network
    """
    story.append(create_code_block(ascii_diagram, styles))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Step-by-Step Processing Lifecycle", subsec_title))
    story.append(Paragraph("<b>Phase 1: Ingest & Local Commit</b> — The client issues an HTTP POST (/set or /incr). The worker invokes clock.tick() to acquire an HLC timestamp (physical_ms, logical_counter, node_id). It merges the update with local Redis state and returns HTTP 200 immediately.", bullet_style))
    story.append(Paragraph("<b>Phase 2: Write-Behind Buffering</b> — The committed delta is appended to an in-memory buffer pending_deltas under a thread-safe mutex lock. If the buffer exceeds 5,000 items (e.g. during a prolonged network partition), the oldest overflow items are discarded.", bullet_style))
    story.append(Paragraph("<b>Phase 3: Periodic Anti-Entropy Push</b> — Every 500 ms, a background daemon replication_loop drains pending_deltas and dispatches the batch to all peer nodes via POST /sync.", bullet_style))
    story.append(Paragraph("<b>Phase 4: Remote Merging</b> — The peer worker receives the delta batch, calls clock.update(remote_ts) to advance its logical clock, applies CRDT resolution (LWWRegister.merge or PNCounter.merge), and updates its local Redis instance.", bullet_style))

    story.append(PageBreak())

    # =========================================================
    # PAGE 5: SECTION 3 - REQUIRED TOOLS & PREREQUISITES
    # =========================================================
    story.append(Paragraph("3. Required Tools & Environment Prerequisites", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph(
        "Before launching or testing the cluster, verify that the following utilities are installed on your host machine. "
        "The project is 100% cross-platform and runs natively on Windows 11/10 (PowerShell), macOS, and Ubuntu Linux.",
        body_style
    ))

    tools_data = [
        [Paragraph("<b>Tool</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Command</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Minimum Version</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Purpose in this Project</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white))],
        [Paragraph("Docker Engine", body_style), Paragraph("docker --version", body_style), Paragraph("24.0+", body_style), Paragraph("Runs Redis 7 and Python Flask worker containers", body_style)],
        [Paragraph("Docker Compose", body_style), Paragraph("docker compose version", body_style), Paragraph("v2.20+", body_style), Paragraph("Orchestrates 6-container local mesh and 2-container AWS nodes", body_style)],
        [Paragraph("Python Runtime", body_style), Paragraph("python --version", body_style), Paragraph("3.11+", body_style), Paragraph("Executes worker backend, HLC, and CRDT test scripts", body_style)],
        [Paragraph("PowerShell", body_style), Paragraph("$PSVersionTable.PSVersion", body_style), Paragraph("5.1 or 7+", body_style), Paragraph("Runs automated multi-region verification harnesses (.ps1)", body_style)],
        [Paragraph("cURL / Invoke-RestMethod", body_style), Paragraph("curl --version", body_style), Paragraph("7.68+", body_style), Paragraph("Issues synthetic HTTP writes and reads against cluster nodes", body_style)],
        [Paragraph("OpenSSH Client", body_style), Paragraph("ssh -V", body_style), Paragraph("OpenSSH 8.0+", body_style), Paragraph("Remote management of AWS EC2 instances via .pem key pairs", body_style)],
    ]
    tools_table = Table(tools_data, colWidths=[90, 110, 80, USABLE_WIDTH - 280])
    tools_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TABLE_HEADER_BG),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, TABLE_ROW_ALT]),
    ]))
    story.append(tools_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Host Environment Verification Script", subsec_title))
    verify_cmd = """# Run in PowerShell to verify all dependencies simultaneously
docker --version
docker compose version
python --version
curl.exe --version
Get-Command ssh | Select-Object Name, Source"""
    story.append(create_code_block(verify_cmd, styles))
    story.append(Spacer(1, 8))

    story.append(create_note_box(
        "<b>Windows Execution Policy:</b> If running the .ps1 test scripts displays a script execution restriction error, run: "
        "Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass in your PowerShell terminal.",
        styles, title="PowerShell Tip"
    ))

    story.append(PageBreak())

    # =========================================================
    # PAGE 6: RECIPE 1 - LOCAL DEVELOPMENT SETUP
    # =========================================================
    story.append(Paragraph("Recipe 1: Local Development & Multi-Container Cluster Setup", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph(
        "To enable offline development and deterministic local testing, the project provides a 6-container Docker Compose "
        "definition simulating three distinct regions (us-central1, europe-west1, and asia-southeast1) connected via a shared bridge network.",
        body_style
    ))

    story.append(Paragraph("Local Cluster Port Mapping", subsec_title))
    port_data = [
        [Paragraph("<b>Region</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Container Name</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Host HTTP Port</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Configured Peer Addresses</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white))],
        [Paragraph("US", body_style), Paragraph("us-central1-worker", body_style), Paragraph("http://localhost:5001", body_style), Paragraph("europe-west1-worker:5000, asia-southeast1-worker:5000", body_style)],
        [Paragraph("Europe", body_style), Paragraph("europe-west1-worker", body_style), Paragraph("http://localhost:5002", body_style), Paragraph("us-central1-worker:5000, asia-southeast1-worker:5000", body_style)],
        [Paragraph("Asia", body_style), Paragraph("asia-southeast1-worker", body_style), Paragraph("http://localhost:5003", body_style), Paragraph("us-central1-worker:5000, europe-west1-worker:5000", body_style)],
    ]
    port_table = Table(port_data, colWidths=[60, 130, 110, USABLE_WIDTH - 300])
    port_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TABLE_HEADER_BG),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, TABLE_ROW_ALT]),
    ]))
    story.append(port_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Step-by-Step Local Deployment Commands", subsec_title))
    local_cmds = """# Step 1: Navigate to the geo-cache directory
cd "c:\\Users\\HP\\Desktop\\ACC\\ACC Miniproject\\geo-cache"

# Step 2: Build images and start all 6 containers in detached mode
docker compose up --build -d

# Step 3: Verify all 6 containers are running
docker compose ps

# Step 4: Verify the health endpoint of each region
curl.exe http://localhost:5001/health
curl.exe http://localhost:5002/health
curl.exe http://localhost:5003/health"""
    story.append(create_code_block(local_cmds, styles))
    story.append(Spacer(1, 8))

    # Add evidence screenshot if available
    img_path = os.path.join("cookbook_assets", "image4.png")
    if os.path.exists(img_path):
        story.append(Paragraph("<b>Docker Desktop Verification:</b>", subsec_title))
        story.append(Image(img_path, width=USABLE_WIDTH, height=95))
        story.append(Spacer(1, 4))
        story.append(Paragraph("<font size=7 color='#64748B'>Figure R1: All 3 Redis and 3 worker containers running in Docker Desktop.</font>", body_style))

    story.append(PageBreak())

    # =========================================================
    # PAGE 7: RECIPE 2 - MULTI-REGION AWS CLOUD DEPLOYMENT
    # =========================================================
    story.append(Paragraph("Recipe 2: Multi-Region Cloud Deployment on AWS EC2", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph(
        "For authentic cross-continent testing, the cluster is deployed on three Amazon EC2 instances located in three "
        "geographically distinct AWS regions. Each node runs an identical container stack via docker-compose.aws.yml.",
        body_style
    ))

    story.append(Paragraph("AWS Multi-Region Topology", subsec_title))
    aws_node_data = [
        [Paragraph("<b>Region Name</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>AWS Identifier</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Physical Location</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Public Elastic IP</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Instance Type</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white))],
        [Paragraph("US Node", body_style), Paragraph("us-east-1", body_style), Paragraph("N. Virginia, USA", body_style), Paragraph("54.242.141.54", body_style), Paragraph("t3.small (2GB)", body_style)],
        [Paragraph("Europe Node", body_style), Paragraph("eu-west-1", body_style), Paragraph("Dublin, Ireland", body_style), Paragraph("34.241.36.71", body_style), Paragraph("t3.small (2GB)", body_style)],
        [Paragraph("Asia Node", body_style), Paragraph("ap-southeast-1", body_style), Paragraph("Singapore, Asia", body_style), Paragraph("52.77.218.56", body_style), Paragraph("t3.small (2GB)", body_style)],
    ]
    aws_node_table = Table(aws_node_data, colWidths=[70, 80, 110, 100, USABLE_WIDTH - 360])
    aws_node_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TABLE_HEADER_BG),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, TABLE_ROW_ALT]),
    ]))
    story.append(aws_node_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Security Group Configuration Invariants", subsec_title))
    story.append(Paragraph("• <b>SSH (Port 22):</b> Restricted exclusively to administrator testing IP.", bullet_style))
    story.append(Paragraph("• <b>Cluster Sync (Port 5000):</b> Restricted to peer Elastic IPs and admin IP. Never open to 0.0.0.0/0.", bullet_style))

    story.append(Paragraph("One-Line Deployment Script per AWS Node", subsec_title))
    aws_deploy_cmds = """# Connect to node via SSH
ssh -i geo-key.pem ubuntu@<INSTANCE_PUBLIC_IP>

# 1. Install Docker Engine
curl -fsSL https://get.docker.com | sudo sh

# 2. Deploy project files and launch containers
git clone https://github.com/vedaXD/ACC-Miniproject.git
cd ACC-Miniproject/geo-cache

# 3. Apply region-specific configuration (example for US node)
cp .env.us .env

# 4. Start Redis and Flask worker with persistent restart
sudo docker compose -f docker-compose.aws.yml up --build -d

# 5. Verify local health
curl -s http://localhost:5000/health"""
    story.append(create_code_block(aws_deploy_cmds, styles))
    story.append(Spacer(1, 6))

    img_sg = os.path.join("aws_assets", "image1.png")
    if os.path.exists(img_sg):
        story.append(Paragraph("<b>AWS Security Group Verification:</b>", subsec_title))
        story.append(Image(img_sg, width=USABLE_WIDTH, height=95))
        story.append(Spacer(1, 4))
        story.append(Paragraph("<font size=7 color='#64748B'>Figure R2: Inbound rules restricting TCP 5000 strictly to peer Elastic IPs.</font>", body_style))

    story.append(PageBreak())

    # =========================================================
    # PAGE 8: RECIPE 3 - HYBRID LOGICAL CLOCKS (HLC)
    # =========================================================
    story.append(Paragraph("Recipe 3: Hybrid Logical Clock (HLC) Algorithmic Design", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph(
        "Standard wall clocks (NTP) suffer from non-monotonic adjustments and network skew, while pure Lamport clocks lose "
        "all correlation with physical wall-clock time. The Hybrid Logical Clock (HLC) combines physical time with a logical "
        "counter to guarantee causality while bounding drift.",
        body_style
    ))

    story.append(Paragraph("Mathematical Timestamp Definition", subsec_title))
    story.append(Paragraph(
        "Each HLC timestamp is a 3-tuple: <b><i>T = (l, c, node_id)</i></b><br/>"
        "• <b><i>l (physical_time_ms):</i></b> Maximum physical wall-clock millisecond observed so far.<br/>"
        "• <b><i>c (logical_counter):</i></b> Monotonically increments when multiple events occur within the same millisecond.<br/>"
        "• <b><i>node_id:</i></b> Unique region identifier (e.g., 'us-east-1') used as a deterministic tie-breaker.",
        body_style
    ))

    story.append(Paragraph("Core HLC Implementation (worker/hlc.py)", subsec_title))
    hlc_code = """class HLC:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self._lock = threading.Lock()
        self._last_physical = 0
        self._counter = 0

    def tick(self):
        \"\"\"Local write event: advances clock monotonically.\"\"\"
        with self._lock:
            now = int(time.time() * 1000)
            if now > self._last_physical:
                self._last_physical = now
                self._counter = 0
            else:
                self._counter += 1
            return (self._last_physical, self._counter, self.node_id)

    def update(self, remote_ts):
        \"\"\"Remote message received: folds remote timestamp into local clock.\"\"\"
        remote_physical, remote_counter, _ = remote_ts
        with self._lock:
            now = int(time.time() * 1000)
            new_physical = max(self._last_physical, remote_physical, now)
            if new_physical == self._last_physical == remote_physical:
                self._counter = max(self._counter, remote_counter) + 1
            elif new_physical == self._last_physical:
                self._counter += 1
            elif new_physical == remote_physical:
                self._counter = remote_counter + 1
            else:
                self._counter = 0
            self._last_physical = new_physical
            return (self._last_physical, self._counter, self.node_id)"""
    story.append(create_code_block(hlc_code, styles))
    story.append(Spacer(1, 8))

    story.append(create_note_box(
        "<b>Deterministic Total Ordering:</b> Two timestamps T1 and T2 are compared by checking: (1) physical time l, then (2) logical counter c, then (3) node_id alphabetically. This ensures every node in the cluster orders any two events identically without network consensus.",
        styles, title="Ordering Invariant"
    ))

    story.append(PageBreak())

    # =========================================================
    # PAGE 9: RECIPE 4 - LWW-REGISTER CRDT
    # =========================================================
    story.append(Paragraph("Recipe 4: LWW-Register CRDT for Key-Value Data", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph(
        "The Last-Write-Wins Register (LWW-Register) is a state-based CRDT used for general string key-value storage. "
        "Every write attaches the winning value and its HLC timestamp. When concurrent writes collide, the entry with the "
        "highest HLC timestamp wins deterministically across all nodes.",
        body_style
    ))

    story.append(Paragraph("LWW-Register Specification & Merge Logic (worker/crdt.py)", subsec_title))
    lww_code = """from hlc import compare as hlc_compare

class LWWRegister:
    \"\"\"
    State shape per key in Redis:
    {"value": <val>, "ts": [physical_ms, logical_counter, node_id]}
    \"\"\"

    @staticmethod
    def merge(local_entry, remote_entry):
        \"\"\"
        Commutative and idempotent merge.
        Returns whichever entry has the higher HLC timestamp.
        \"\"\"
        if local_entry is None:
            return remote_entry
        if remote_entry is None:
            return local_entry

        # Strict deterministic comparison:
        # 1. Compare physical millisecond
        # 2. Compare logical counter
        # 3. Compare node_id lexicographically
        if hlc_compare(remote_entry["ts"], local_entry["ts"]) > 0:
            return remote_entry
        return local_entry"""
    story.append(create_code_block(lww_code, styles))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Conflict Resolution Walkthrough", subsec_title))
    story.append(Paragraph("1. Client A sends POST /set (user:100 = 'active') to <b>US</b> at physical time 1790925567663.", bullet_style))
    story.append(Paragraph("2. Client B sends POST /set (user:100 = 'inactive') to <b>Europe</b> at physical time 1790925567744.", bullet_style))
    story.append(Paragraph("3. When US replicates to Europe, Europe checks timestamps: 1790925567744 > 1790925567663. Europe keeps 'inactive'.", bullet_style))
    story.append(Paragraph("4. When Europe replicates to US, US performs the exact same check. US overwrites 'active' with 'inactive'.", bullet_style))
    story.append(Paragraph("5. Replicas converge on the identical value without central coordination.", bullet_style))

    story.append(Spacer(1, 6))
    story.append(create_note_box(
        "<b>Mathematical Guarantee:</b> Because the merge function is idempotent (merge(A,A) = A), commutative (merge(A,B) = merge(B,A)), and associative (merge(merge(A,B),C) = merge(A,merge(B,C))), packet reordering, network retries, and duplicate delivery cannot corrupt the state.",
        styles, title="CRDT Mathematical Property"
    ))

    story.append(PageBreak())

    # =========================================================
    # PAGE 10: RECIPE 5 - STATE-BASED PN-COUNTER CRDT
    # =========================================================
    story.append(Paragraph("Recipe 5: State-Based PN-Counter CRDT for Distributed Counters", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph(
        "Standard Redis INCR operations are unsafe in active-active topologies: concurrent increments issued to different "
        "replicas overwrite each other if replicated as raw numbers. The Positive-Negative Counter (PN-Counter) solves this by "
        "tracking per-node increment vectors.",
        body_style
    ))

    story.append(Paragraph("PN-Counter State & Merge Algorithm (worker/crdt.py)", subsec_title))
    pn_code = """class PNCounter:
    \"\"\"
    State shape per key:
    {
      "P": {"us-east-1": 5, "eu-west-1": 3, "ap-southeast-1": 2},
      "N": {"us-east-1": 0, "eu-west-1": 1, "ap-southeast-1": 0}
    }
    \"\"\"

    @staticmethod
    def new_state():
        return {"P": {}, "N": {}}

    @staticmethod
    def increment(state, node_id, amount=1):
        if amount >= 0:
            state["P"][node_id] = state["P"].get(node_id, 0) + amount
        else:
            state["N"][node_id] = state["N"].get(node_id, 0) + abs(amount)
        return state

    @staticmethod
    def value(state):
        \"\"\"Net counter value is sum of all positives minus sum of all negatives.\"\"\"
        total_p = sum(state.get("P", {}).values())
        total_n = sum(state.get("N", {}).values())
        return total_p - total_n

    @staticmethod
    def merge(local_state, remote_state):
        \"\"\"Merge takes per-node maxima: idempotent and commutative.\"\"\"
        if not local_state:
            return remote_state
        if not remote_state:
            return local_state

        merged_p = {}
        all_nodes_p = set(local_state.get("P", {})).union(remote_state.get("P", {}))
        for n in all_nodes_p:
            merged_p[n] = max(local_state.get("P", {}).get(n, 0), remote_state.get("P", {}).get(n, 0))

        merged_n = {}
        all_nodes_n = set(local_state.get("N", {})).union(remote_state.get("N", {}))
        for n in all_nodes_n:
            merged_n[n] = max(local_state.get("N", {}).get(n, 0), remote_state.get("N", {}).get(n, 0))

        return {"P": merged_p, "N": merged_n}"""
    story.append(create_code_block(pn_code, styles))
    story.append(Spacer(1, 8))

    story.append(create_note_box(
        "<b>No Increments Lost:</b> Because each node only increments its own slot in P, and merging computes max(P_local[k], P_remote[k]), increments from any region are strictly additive and will never overwrite concurrent increments from other regions.",
        styles, title="Additive Invariant"
    ))

    story.append(PageBreak())

    # =========================================================
    # PAGE 11: RECIPE 6 - WRITE-BEHIND REPLICATION & MEMORY FIX
    # =========================================================
    story.append(Paragraph("Recipe 6: Asynchronous Write-Behind Replication Engine & Buffer Capping", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph(
        "The Flask worker maintains an in-memory delta queue flushed every 500ms to peer nodes. During testing, an unbounded "
        "memory leak was discovered under prolonged network partitions. Below is the production-hardened implementation.",
        body_style
    ))

    story.append(Paragraph("Replication Loop with Buffer Capping (worker/app.py)", subsec_title))
    rep_code = """buffer_lock = threading.Lock()
pending_deltas = []  # list of {"type": "lww"|"counter", "key": ..., "entry"/"state": ...}
MAX_BUFFER_SIZE = 5000  # Hard cap prevents unbounded growth during partitions

def replication_loop():
    \"\"\"Flushes pending deltas to all peers every SYNC_INTERVAL_MS.\"\"\"
    while True:
        time.sleep(SYNC_INTERVAL_MS / 1000)
        with buffer_lock:
            if not pending_deltas:
                continue
            batch = pending_deltas[:]
            pending_deltas.clear()

        # Asynchronously send deltas to all configured peer nodes
        for peer in PEERS:
            try:
                requests.post(f"http://{peer}/sync", json={"deltas": batch}, timeout=2)
            except requests.RequestException as e:
                # Peer unreachable: Re-buffer failed batch but enforce strict upper cap
                with buffer_lock:
                    pending_deltas.extend(batch)
                    if len(pending_deltas) > MAX_BUFFER_SIZE:
                        overflow = len(pending_deltas) - MAX_BUFFER_SIZE
                        del pending_deltas[:overflow]  # Drop oldest deltas
                        print(f"[{REGION_ID}] Buffer capped, dropped {overflow} oldest deltas")
                print(f"[{REGION_ID}] Sync to {peer} failed: {e}")"""
    story.append(create_code_block(rep_code, styles))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Engineering Finding: Resolving the OOM Defect", subsec_title))
    story.append(Paragraph(
        "During initial partition testing on 1 GB EC2 instances, isolating a node for 15 minutes caused pending_deltas to "
        "accumulate over 45,000 objects. Each failed retry cycle re-extended the queue, resulting in an exponential memory leak "
        "that triggered the Linux kernel Out-Of-Memory (OOM) killer. Capping the buffer to 5,000 entries and upgrading to 2 GB RAM "
        "(t3.small) completely eliminated crashes.",
        body_style
    ))
    story.append(Spacer(1, 4))

    img_oom = os.path.join("cookbook_assets", "image10.png")
    if os.path.exists(img_oom):
        story.append(Image(img_oom, width=USABLE_WIDTH, height=55))
        story.append(Paragraph("<font size=7 color='#64748B'>Figure R6: Root-cause diagnosis of unbounded memory growth in the retry queue.</font>", body_style))

    story.append(PageBreak())

    # =========================================================
    # PAGE 12: RECIPE 7 - LWW CONFLICT DEMONSTRATION
    # =========================================================
    story.append(Paragraph("Recipe 7: Concurrent Conflicting Writes Verification (01-lww-demo.ps1)", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph(
        "This test verifies that when conflicting values are written simultaneously to the exact same key across two "
        "different continents, the cluster reaches 100% deterministic convergence.",
        body_style
    ))

    story.append(Paragraph("Automated Verification Script (01-lww-demo.ps1)", subsec_title))
    lww_script = """# Firing simultaneous conflicting writes to US and Europe
$key = "demo-lww-" + (Get-Date -Format "yyyyMMdd-HHmmss-fff")

$jUS = Start-Job -ScriptBlock {
    param($url,$key)
    Invoke-RestMethod "$url/set" -Method Post -ContentType "application/json" -Body (@{key=$key; value="active"}|ConvertTo-Json)
} -ArgumentList "http://54.242.141.54:5000",$key

$jEU = Start-Job -ScriptBlock {
    param($url,$key)
    Invoke-RestMethod "$url/set" -Method Post -ContentType "application/json" -Body (@{key=$key; value="inactive"}|ConvertTo-Json)
} -ArgumentList "http://34.241.36.71:5000",$key

Wait-Job $jUS,$jEU | Out-Null
Receive-Job $jUS; Receive-Job $jEU

# Wait 3 seconds for cross-continental sync
Start-Sleep -Seconds 3

# Query final state on all three global nodes
$nodes = @("http://54.242.141.54:5000", "http://34.241.36.71:5000", "http://52.77.218.56:5000")
foreach ($n in $nodes) { (Invoke-RestMethod "$n/get/$key") }"""
    story.append(create_code_block(lww_script, styles))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Observed Execution Evidence", subsec_title))
    img_lww = os.path.join("cookbook_assets", "image16.png")
    if os.path.exists(img_lww):
        story.append(Image(img_lww, width=USABLE_WIDTH, height=85))
        story.append(Spacer(1, 4))
        story.append(Paragraph("<font size=7 color='#64748B'>Figure R7: Test execution confirming all 3 regions converged to identical winning value.</font>", body_style))

    story.append(Spacer(1, 6))
    story.append(create_note_box(
        "<b>Verification Success:</b> US wrote 'active' and Europe wrote 'inactive'. Within 1.5 seconds, all three nodes (US, Europe, Asia) returned the identical value and HLC timestamp, proving coordination-free convergence.",
        styles, title="Observed Result"
    ))

    story.append(PageBreak())

    # =========================================================
    # PAGE 13: RECIPE 8 - PN-COUNTER DEMONSTRATION
    # =========================================================
    story.append(Paragraph("Recipe 8: Concurrent Counter Increments Verification (02-pn-counter-demo.ps1)", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph(
        "This test fires concurrent increment operations across all three regions simultaneously on a single shared counter key: "
        "US increments by +5, Europe by +3, and Asia by +2. The expected total sum is exactly 10 across all replicas.",
        body_style
    ))

    story.append(Paragraph("Automated Increments Script (02-pn-counter-demo.ps1)", subsec_title))
    pn_script = """# Concurrently incrementing post:101:likes from 3 continents
$key = "demo-pn-" + (Get-Date -Format "yyyyMMdd-HHmmss-fff")

$jobs = @()
$jobs += Start-Job -ScriptBlock { param($u,$k) Invoke-RestMethod "$u/incr" -Method Post -ContentType "application/json" -Body (@{key=$k; amount=5}|ConvertTo-Json) } -ArgumentList "http://54.242.141.54:5000",$key
$jobs += Start-Job -ScriptBlock { param($u,$k) Invoke-RestMethod "$u/incr" -Method Post -ContentType "application/json" -Body (@{key=$k; amount=3}|ConvertTo-Json) } -ArgumentList "http://34.241.36.71:5000",$key
$jobs += Start-Job -ScriptBlock { param($u,$k) Invoke-RestMethod "$u/incr" -Method Post -ContentType "application/json" -Body (@{key=$k; amount=2}|ConvertTo-Json) } -ArgumentList "http://52.77.218.56:5000",$key

Wait-Job $jobs | Out-Null

# Poll until convergence across all three nodes
$deadline = (Get-Date).AddSeconds(15)
do {
    Start-Sleep -Milliseconds 500
    $vUS   = (Invoke-RestMethod "http://54.242.141.54:5000/counter/$key").value
    $vEU   = (Invoke-RestMethod "http://34.241.36.71:5000/counter/$key").value
    $vAsia = (Invoke-RestMethod "http://52.77.218.56:5000/counter/$key").value
    if ($vUS -eq 10 -and $vEU -eq 10 -and $vAsia -eq 10) { break }
} while ((Get-Date) -lt $deadline)

Write-Host "US -> $vUS | Europe -> $vEU | Asia -> $vAsia (Expected: 10 everywhere)" """
    story.append(create_code_block(pn_script, styles))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Observed Execution Evidence", subsec_title))
    img_pn = os.path.join("cookbook_assets", "image8.png")
    if os.path.exists(img_pn):
        story.append(Image(img_pn, width=USABLE_WIDTH, height=75))
        story.append(Spacer(1, 4))
        story.append(Paragraph("<font size=7 color='#64748B'>Figure R8: Terminal output showing counter value 10 converging across all 3 regions.</font>", body_style))

    story.append(Spacer(1, 6))
    story.append(create_note_box(
        "<b>Verification Success:</b> Zero lost updates. Despite network propagation delays across oceans, the additive semilattice merged all three regional positive components (+5, +3, +2) into a consistent global total of 10.",
        styles, title="Observed Result"
    ))

    story.append(PageBreak())

    # =========================================================
    # PAGE 14: RECIPE 9 - FAULT TOLERANCE & OUTAGE RECOVERY
    # =========================================================
    story.append(Paragraph("Recipe 9: Fault Tolerance & Outage Recovery (03-worker-outage-recovery.ps1)", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph(
        "This test proves high availability during a regional outage. A single worker container is forcefully stopped. "
        "Surviving nodes continue accepting live traffic. Upon container restart, all queued deltas replicate automatically.",
        body_style
    ))

    story.append(Paragraph("Outage & Automatic Reconciliation Lifecycle", subsec_title))
    outage_script = """# 1. Stop the Asia Flask worker over SSH (EC2 and Redis remain running)
ssh.exe -i geo-cache-asia-key.pem ubuntu@52.77.218.56 "sudo docker compose -f ~/docker-compose.aws.yml stop worker"

# 2. Write updates to surviving nodes (US +4, Europe +6)
$key = "demo-outage-" + (Get-Date -Format "yyyyMMdd-HHmmss-fff")
Invoke-RestMethod "http://54.242.141.54:5000/incr" -Method Post -ContentType "application/json" -Body (@{key=$key; amount=4}|ConvertTo-Json)
Invoke-RestMethod "http://34.241.36.71:5000/incr" -Method Post -ContentType "application/json" -Body (@{key=$key; amount=6}|ConvertTo-Json)

# 3. Confirm Asia is unreachable while US and Europe report 10
# 4. Restart the Asia worker
ssh.exe -i geo-cache-asia-key.pem ubuntu@52.77.218.56 "sudo docker compose -f ~/docker-compose.aws.yml start worker"

# 5. Within 2 seconds, US and Europe flush their buffered deltas to Asia
Start-Sleep -Seconds 2
Invoke-RestMethod "http://52.77.218.56:5000/counter/$key"  # Returns 10!"""
    story.append(create_code_block(outage_script, styles))
    story.append(Spacer(1, 8))

    img_outage = os.path.join("aws_assets", "image18.png")
    if not os.path.exists(img_outage):
        img_outage = os.path.join("cookbook_assets", "image1.png")
    if os.path.exists(img_outage):
        story.append(Paragraph("<b>Partition Recovery Verification:</b>", subsec_title))
        story.append(Image(img_outage, width=USABLE_WIDTH, height=90))
        story.append(Spacer(1, 4))
        story.append(Paragraph("<font size=7 color='#64748B'>Figure R9: Asia node catching up and returning counter value 10 after container restart.</font>", body_style))

    story.append(PageBreak())

    # =========================================================
    # PAGE 15: RECIPE 10 - LATENCY & CONVERGENCE BENCHMARKING
    # =========================================================
    story.append(Paragraph("Recipe 10: Multi-Region Latency & Convergence Benchmarking", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph(
        "Empirical benchmarks were conducted to quantify both inter-continental convergence duration and the end-user latency "
        "reduction achieved by serving clients from their nearest geographic region.",
        body_style
    ))

    story.append(Paragraph("Empirical Benchmark Results", subsec_title))
    bench_data = [
        [Paragraph("<b>Benchmark Metric</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Measurement Route / Scenario</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Observed Result</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Performance Interpretation</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white))],
        [Paragraph("Client Latency (Nearest)", body_style), Paragraph("India Client -> Singapore (Asia)", body_style), Paragraph("<b>166 ms</b>", body_style), Paragraph("Lowest latency path for South Asian traffic", body_style)],
        [Paragraph("Client Latency (Distant)", body_style), Paragraph("India Client -> N. Virginia (US)", body_style), Paragraph("<b>504 ms</b>", body_style), Paragraph("3.0x slower without active-active replication", body_style)],
        [Paragraph("Client Latency (Distant)", body_style), Paragraph("India Client -> Ireland (Europe)", body_style), Paragraph("<b>522 ms</b>", body_style), Paragraph("3.1x slower without active-active replication", body_style)],
        [Paragraph("Replication Convergence", body_style), Paragraph("US write -> Asia readable (10 runs)", body_style), Paragraph("<b>924 ms – 1413 ms</b><br/>(Avg: 1120 ms)", body_style), Paragraph("Floor is 500ms sync interval + transatlantic RTT", body_style)],
        [Paragraph("Replication Accuracy", body_style), Paragraph("100 concurrent LWW & PN operations", body_style), Paragraph("<b>100% Convergence</b>", body_style), Paragraph("Zero lost updates across all AWS replicas", body_style)],
    ]
    bench_table = Table(bench_data, colWidths=[110, 140, 95, USABLE_WIDTH - 345])
    bench_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TABLE_HEADER_BG),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, TABLE_ROW_ALT]),
    ]))
    story.append(bench_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Client Latency Measurement Command", subsec_title))
    lat_cmd = """# Measure total HTTP round-trip latency to each region from local machine
curl.exe -s -o NUL -w "Asia (Singapore) : %{time_total}s\\n" http://52.77.218.56:5000/health
curl.exe -s -o NUL -w "US (N. Virginia)  : %{time_total}s\\n" http://54.242.141.54:5000/health
curl.exe -s -o NUL -w "Europe (Ireland)  : %{time_total}s\\n" http://34.241.36.71:5000/health"""
    story.append(create_code_block(lat_cmd, styles))
    story.append(Spacer(1, 6))

    story.append(create_note_box(
        "<b>Architectural Impact:</b> Serving users from their nearest geographic cache node slashes client latency from ~510 ms down to 166 ms — an immediate <b>67% response-time reduction</b>, fulfilling the core objective of the Advanced Cloud Computing project.",
        styles, title="Key Finding"
    ))

    story.append(PageBreak())

    # =========================================================
    # PAGE 16: QUICK REFERENCE CHEAT SHEET
    # =========================================================
    story.append(Paragraph("Quick Reference Cheat Sheet", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph("Cluster REST API Endpoints", subsec_title))
    api_data = [
        [Paragraph("<b>Endpoint</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Method</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Payload / Params</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Purpose & Architectural Behavior</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white))],
        [Paragraph("/set", body_style), Paragraph("POST", body_style), Paragraph('{"key":"k", "value":"v"}', body_style), Paragraph("Writes LWW-Register key; ticks HLC; buffers delta", body_style)],
        [Paragraph("/get/&lt;key&gt;", body_style), Paragraph("GET", body_style), Paragraph("None", body_style), Paragraph("Returns current value, HLC timestamp tuple, and region", body_style)],
        [Paragraph("/incr", body_style), Paragraph("POST", body_style), Paragraph('{"key":"k", "amount":1}', body_style), Paragraph("Increments PN-Counter local vector; buffers delta", body_style)],
        [Paragraph("/counter/&lt;key&gt;", body_style), Paragraph("GET", body_style), Paragraph("None", body_style), Paragraph("Calculates sum(P) - sum(N) across all known regions", body_style)],
        [Paragraph("/sync", body_style), Paragraph("POST", body_style), Paragraph('{"deltas": [...]}', body_style), Paragraph("Receives delta batch from peer; folds HLC; merges CRDT", body_style)],
        [Paragraph("/health", body_style), Paragraph("GET", body_style), Paragraph("None", body_style), Paragraph("Reports node health, assigned REGION_ID, and peer list", body_style)],
    ]
    api_table = Table(api_data, colWidths=[90, 45, 130, USABLE_WIDTH - 265])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TABLE_HEADER_BG),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, TABLE_ROW_ALT]),
    ]))
    story.append(api_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Environment Variables Reference", subsec_title))
    env_data = [
        [Paragraph("<b>Variable</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Default / Example</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Description</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white))],
        [Paragraph("REGION_ID", body_style), Paragraph("us-east-1", body_style), Paragraph("Unique node name used for HLC tie-breaking and PN-Counter tracking", body_style)],
        [Paragraph("REDIS_HOST", body_style), Paragraph("redis", body_style), Paragraph("Hostname or IP of the region-local Redis container instance", body_style)],
        [Paragraph("PEERS", body_style), Paragraph("34.241.36.71:5000,52.77.218.56:5000", body_style), Paragraph("Comma-separated list of peer worker host:port endpoints", body_style)],
        [Paragraph("SYNC_INTERVAL_MS", body_style), Paragraph("500", body_style), Paragraph("Replication heartbeat interval for flushing the write-behind buffer", body_style)],
        [Paragraph("SIMULATED_LATENCY_MS", body_style), Paragraph("0", body_style), Paragraph("Optional artificial delay injected into sync calls for local testing", body_style)],
    ]
    env_table = Table(env_data, colWidths=[120, 160, USABLE_WIDTH - 280])
    env_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TABLE_HEADER_BG),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, TABLE_ROW_ALT]),
    ]))
    story.append(env_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Copy-Paste Verification Runbook", subsec_title))
    runbook_cmd = """# Run the 3 automated test suites from project root
cd "c:\\Users\\HP\\Desktop\\ACC\\ACC Miniproject\\geo-cache"
.\\01-lww-demo.ps1                 # Test concurrent conflicting writes
.\\02-pn-counter-demo.ps1          # Test multi-region counter increments
.\\03-worker-outage-recovery.ps1   # Test worker crash and recovery"""
    story.append(create_code_block(runbook_cmd, styles))

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Cookbook PDF successfully compiled to: {filename}")

if __name__ == "__main__":
    build_pdf()
