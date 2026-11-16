# -*- coding: utf-8 -*-
"""
Engineering Cookbook PDF Generator for Geo-Distributed Active-Active Cache Cluster.
100% developer-focused: architecture, setup recipes, code walkthroughs, test execution, and API cheat sheets.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode import qr

PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 42
USABLE_WIDTH = PAGE_WIDTH - 2 * MARGIN

# Visual Identity matching the reference engineering cookbook
PRIMARY = colors.HexColor("#0B3954")       # Deep Navy Blue
ACCENT = colors.HexColor("#0284C7")        # Cyan / Blue
DARK_TEXT = colors.HexColor("#0F172A")     # Slate dark body text
MUTED_TEXT = colors.HexColor("#475569")    # Subtitle / secondary
BORDER_COLOR = colors.HexColor("#CBD5E1")  # Clean grey border
NOTE_BG = colors.HexColor("#F0F9FF")       # Info box background
NOTE_BORDER = colors.HexColor("#0284C7")   # Info box accent border
TABLE_HEADER_BG = colors.HexColor("#0B3954")
TABLE_ROW_ALT = colors.HexColor("#F8FAFC")
CODE_BG = colors.HexColor("#F1F5F9")

class NumberedCanvas(canvas.Canvas):
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
            self.setFillColor(MUTED_TEXT)
            self.drawString(MARGIN + 215, PAGE_HEIGHT - 26, "•  Architectural Blueprint & Engineering Cookbook")
            
            self.setStrokeColor(BORDER_COLOR)
            self.setLineWidth(0.5)
            self.line(MARGIN, PAGE_HEIGHT - 31, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 31)
            
            self.line(MARGIN, 34, PAGE_WIDTH - MARGIN, 34)
            self.drawString(MARGIN, 22, "vedaXD/ACC-Miniproject • Developer Cookbook")
            page_text = f"Page {self._pageNumber} of {total_pages}"
            self.drawRightString(PAGE_WIDTH - MARGIN, 22, page_text)
            self.restoreState()

def create_code_block(code_text, styles):
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.2,
        leading=9.2,
        textColor=colors.HexColor("#0F172A")
    )
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

def create_note_box(note_text, styles, title="Developer Note"):
    body_style = ParagraphStyle(
        'NoteBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=DARK_TEXT
    )
    content = [Paragraph(f"<b>{title}:</b> {note_text}", body_style)]
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

def get_qr_drawing(url, size=58):
    qr_code = qr.QrCodeWidget(url)
    bounds = qr_code.getBounds()
    w = bounds[2] - bounds[0]
    h = bounds[3] - bounds[1]
    d = Drawing(size, size, transform=[size/w, 0, 0, size/h, 0, 0])
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

    h1_style = ParagraphStyle(
        'CoverH1',
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=30,
        textColor=PRIMARY,
        spaceAfter=4
    )
    sub_style = ParagraphStyle(
        'CoverSub',
        fontName='Helvetica',
        fontSize=14,
        leading=17,
        textColor=ACCENT,
        spaceAfter=14
    )
    lead_style = ParagraphStyle(
        'CoverLead',
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
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
    # PAGE 1: COVER PAGE (PURE ENGINEERING COOKBOOK)
    # =========================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("Geo-Distributed Active-Active Cache Cluster", h1_style))
    story.append(Paragraph("Architectural Blueprint & Engineering Cookbook", sub_style))

    story.append(Paragraph(
        "A production-grade developer guide to building, containerizing, deploying, and operating high-throughput, "
        "conflict-free geo-distributed cache clusters on Microsoft Windows, Linux, Docker, and Amazon Web Services (AWS EC2). "
        "Based on the <b>ACC-MiniProject</b> repository (<b>vedaXD/ACC-Miniproject</b>). Covers multi-master replication architecture, "
        "Hybrid Logical Clock (HLC) mathematics, state-based CRDT conflict resolution (LWW-Register and PN-Counter), "
        "asynchronous write-behind buffering, and ten practical implementation recipes.",
        lead_style
    ))

    # Interactive links banner
    qr_draw = get_qr_drawing("https://youtu.be/OwtLWvFsUC4", size=55)
    video_banner_text = Paragraph(
        "<b>Project Repositories & Demonstration Video</b><br/>"
        "<font size=8 color='#0369A1'>If you are running this project for the first time, review the live walkthrough and codebase:</font><br/>"
        "<font size=8>• <b>Live Video Walkthrough:</b> <a href='https://youtu.be/OwtLWvFsUC4' color='#0284C7'><u>https://youtu.be/OwtLWvFsUC4</u></a></font><br/>"
        "<font size=8>• <b>GitHub Repository:</b> <a href='https://github.com/vedaXD/ACC-Miniproject' color='#0284C7'><u>https://github.com/vedaXD/ACC-Miniproject</u></a></font><br/>"
        "<font size=8>• <b>Cluster Topology:</b> 3 AWS Regions: US (us-east-1), Europe (eu-west-1), Asia (ap-southeast-1)</font>",
        body_style
    )
    banner_table = Table([[qr_draw, video_banner_text]], colWidths=[65, USABLE_WIDTH - 65])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NOTE_BG),
        ('BOX', (0,0), (-1,-1), 0.75, NOTE_BORDER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 14))

    # Stack Table (Matching Reference Page 1 layout)
    stack_data = [
        [Paragraph("<b>Stack Component</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Technology / Implementation</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Architectural Role in System</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white))],
        [Paragraph("In-Memory Storage", body_style), Paragraph("Redis 7 (Alpine)", body_style), Paragraph("Sub-millisecond local in-memory storage for raw keys and counter states", body_style)],
        [Paragraph("Regional Gateway Worker", body_style), Paragraph("Python 3.11 + Flask", body_style), Paragraph("Exposes HTTP API (/set, /get, /incr, /counter) and coordinates /sync replication", body_style)],
        [Paragraph("Causal Timestamping", body_style), Paragraph("Hybrid Logical Clock (HLC)", body_style), Paragraph("Generates monotonic (physical_ms, logical_counter, node_id) timestamps", body_style)],
        [Paragraph("Key-Value Resolution", body_style), Paragraph("LWW-Register CRDT", body_style), Paragraph("Last-Write-Wins deterministic merge with node_id tie breaking", body_style)],
        [Paragraph("Distributed Counters", body_style), Paragraph("State-Based PN-Counter", body_style), Paragraph("Positive-Negative counters with idempotent per-node maxima vector merging", body_style)],
        [Paragraph("Replication Buffer", body_style), Paragraph("Asynchronous Write-Behind", body_style), Paragraph("Immediate local writes; 500ms batched HTTP push (capped at 5,000 deltas)", body_style)],
        [Paragraph("Cloud Infrastructure", body_style), Paragraph("AWS EC2 Multi-Region", body_style), Paragraph("Three t3.small instances across US, Europe, and Asia regions with Elastic IPs", body_style)],
        [Paragraph("Local Orchestration", body_style), Paragraph("Docker Compose v2", body_style), Paragraph("One-command 6-container development mesh mapped to ports 5001-5003", body_style)],
    ]
    stack_table = Table(stack_data, colWidths=[120, 135, USABLE_WIDTH - 255])
    stack_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TABLE_HEADER_BG),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, TABLE_ROW_ALT]),
    ]))
    story.append(stack_table)

    story.append(PageBreak())

    # =========================================================
    # PAGE 2: TABLE OF CONTENTS
    # =========================================================
    story.append(Paragraph("Table of Contents", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    toc_items = [
        ("1. Architecture & System Design Philosophy", "3"),
        ("2. Data Flow & Replication Topology", "4"),
        ("3. Required Tools & Prerequisites", "5"),
        ("Recipe 1: Local Development & Multi-Container Cluster Setup", "6"),
        ("Recipe 2: Multi-Region AWS Cloud Provisioning & Deployment", "7"),
        ("Recipe 3: Hybrid Logical Clock (HLC) Implementation", "8"),
        ("Recipe 4: LWW-Register CRDT Conflict Resolution", "9"),
        ("Recipe 5: State-Based PN-Counter CRDT", "10"),
        ("Recipe 6: Asynchronous Write-Behind Replication Engine & Buffer Capping", "11"),
        ("Recipe 7: Verification — Concurrent Conflicting Writes (01-lww-demo.ps1)", "12"),
        ("Recipe 8: Verification — Concurrent Counter Increments (02-pn-counter-demo.ps1)", "13"),
        ("Recipe 9: Verification — Fault Tolerance & Regional Outage Recovery (03-worker-outage-recovery.ps1)", "14"),
        ("Recipe 10: Performance Benchmarking & Latency Analysis", "15"),
        ("Quick Reference Cheat Sheet: REST APIs & Environment Variables", "16"),
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

    story.append(Spacer(1, 16))
    story.append(Paragraph("How to Use This Cookbook", subsec_title))
    story.append(Paragraph("• <b>If you are running the project locally:</b> Go straight to <b>Recipe 1</b> (Page 6). Run docker compose up --build -d and execute the test scripts.", bullet_style))
    story.append(Paragraph("• <b>If you are deploying across AWS cloud regions:</b> Follow <b>Recipe 2</b> (Page 7) to launch EC2 instances and set security groups.", bullet_style))
    story.append(Paragraph("• <b>If you want to understand the conflict resolution algorithms:</b> Review <b>Recipes 3, 4, 5, and 6</b> for HLC, LWW, PN-Counter, and write-behind buffering code.", bullet_style))
    story.append(Paragraph("• <b>If you want to run the automated verification suite:</b> Follow <b>Recipes 7, 8, and 9</b> for copy-paste test runs.", bullet_style))

    story.append(PageBreak())

    # =========================================================
    # PAGE 3: SECTION 1 - ARCHITECTURE & DESIGN PHILOSOPHY
    # =========================================================
    story.append(Paragraph("1. Architecture & System Design Philosophy", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph("The Core Problem: Single-Region Cache Latency vs. Active-Active Replication", subsec_title))
    story.append(Paragraph(
        "Traditional cloud architectures place the primary caching layer in a single central region (e.g., US East). "
        "When an end-user in Asia or Europe issues an update, that request traverses multiple undersea fiber cables, "
        "incurring a mandatory <b>400ms – 550ms round-trip latency penalty</b> on every read and write. Even worse, if the "
        "central region suffers a network partition or hardware outage, write availability across the entire globe drops to zero.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Active-Active (Multi-Master) Geo-Replication</b> resolves this bottleneck by placing fully writable cache nodes in "
        "each geographic region. Local clients read and write with sub-millisecond local latency. However, multi-master writes "
        "introduce concurrent conflicting updates that must converge deterministically across all replicas without requiring "
        "a centralized coordinator.",
        body_style
    ))

    story.append(Paragraph("Architectural Invariants of this System", subsec_title))
    story.append(Paragraph("<b>1. Sub-Millisecond Local Write Latency:</b> Writes (/set, /incr) are committed immediately to the local Redis instance and acknowledged to the client with HTTP 200. Replicating updates across continents never blocks local user execution.", bullet_style))
    story.append(Paragraph("<b>2. AP Availability under CAP Theorem:</b> When transatlantic connections degrade or fail, each node continues accepting local reads and writes (100% availability). Eventual consistency is restored automatically upon reconnection.", bullet_style))
    story.append(Paragraph("<b>3. Hybrid Logical Clock (HLC) Causal Total Ordering:</b> Wall-clock time alone cannot order distributed events due to NTP clock drift and virtualization jitter. HLC stamps each write with (physical_ms, logical_counter, node_id) to guarantee a strict monotonic order across machines.", bullet_style))
    story.append(Paragraph("<b>4. Conflict-Free Replicated Data Types (CRDTs):</b> All state reconciliations rely on mathematical semilattices satisfying commutativity (A ∨ B = B ∨ A), associativity ((A ∨ B) ∨ C = A ∨ (B ∨ C)), and idempotency (A ∨ A = A).", bullet_style))
    story.append(Paragraph("<b>5. Asynchronous Write-Behind with Delta Capping:</b> Changes are accumulated in memory and flushed every 500 ms via HTTP POST /sync. To protect worker processes from memory exhaustion during extended outages, the retry queue is capped at 5,000 deltas.", bullet_style))

    story.append(Spacer(1, 8))
    story.append(create_note_box(
        "<b>Architectural Tradeoff:</b> This cluster is an AP system under CAP theorem. It chooses immediate availability and sub-millisecond local latency over linearizable immediate consistency. Replicas converge within ~1 second under normal transatlantic network conditions.",
        styles, title="CAP Theorem Classification"
    ))

    story.append(PageBreak())

    # =========================================================
    # PAGE 4: SECTION 2 - DATA FLOW & REPLICATION TOPOLOGY
    # =========================================================
    story.append(Paragraph("2. Data Flow & Replication Topology", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph("Replication Architecture", subsec_title))
    ascii_flow = """
  [Local Client in US]                 [Local Client in EU]               [Local Client in Asia]
         | (POST /set)                        | (POST /set)                      | (POST /incr)
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
|  +-----------------+  |            |  +-----------------+  |          |  +-----------------+  |
|           |           |                     |           |                   |           |
|   [Write-Behind Buf]  |            |   [Write-Behind Buf]  |          |   [Write-Behind Buf]  |
|   (max 5000 deltas)   |            |   (max 5000 deltas)   |          |   (max 5000 deltas)   |
+-----------+-----------+            +-----------+-----------+          +-----------+-----------+
            |                                    |                                  |
            |====== HTTP POST /sync (500ms) =====+====== HTTP POST /sync (500ms) ===|
            +------------------------------------+----------------------------------+
                                    Inter-Region Network Mesh
    """
    story.append(create_code_block(ascii_flow, styles))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Lifecycle of a Write Operation", subsec_title))
    story.append(Paragraph("<b>1. Ingestion:</b> Client sends POST /set or POST /incr to closest regional worker. Worker executes clock.tick() to assign a monotonic HLC timestamp.", bullet_style))
    story.append(Paragraph("<b>2. Local Persistence:</b> The worker writes the update directly to local Redis and responds with HTTP 200 OK (< 2ms response time).", bullet_style))
    story.append(Paragraph("<b>3. Write-Behind Queue:</b> The committed delta is appended to pending_deltas under a thread-safe mutex lock.", bullet_style))
    story.append(Paragraph("<b>4. Asynchronous Push:</b> Every 500ms, a background thread drains the buffer and sends deltas to all peer nodes via POST /sync.", bullet_style))
    story.append(Paragraph("<b>5. Remote CRDT Merge:</b> The receiving worker folds the incoming timestamp into its HLC and merges state deterministically into its local Redis instance.", bullet_style))

    story.append(PageBreak())

    # =========================================================
    # PAGE 5: SECTION 3 - REQUIRED TOOLS & PREREQUISITES
    # =========================================================
    story.append(Paragraph("3. Required Tools & Prerequisites", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph(
        "All commands in this cookbook run natively on Windows 11/10 (PowerShell), macOS, or Ubuntu Linux. "
        "Verify your local development environment before executing the recipes.",
        body_style
    ))

    tools_data = [
        [Paragraph("<b>Tool</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Command to Verify</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Minimum Version</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Role in this Cookbook</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white))],
        [Paragraph("Docker Engine", body_style), Paragraph("docker --version", body_style), Paragraph("24.0+", body_style), Paragraph("Runs containerized Redis 7 and Flask worker services", body_style)],
        [Paragraph("Docker Compose", body_style), Paragraph("docker compose version", body_style), Paragraph("v2.20+", body_style), Paragraph("Orchestrates local 6-container cluster and AWS cloud nodes", body_style)],
        [Paragraph("Python Runtime", body_style), Paragraph("python --version", body_style), Paragraph("3.11+", body_style), Paragraph("Runs worker backend, HLC, and CRDT test scripts", body_style)],
        [Paragraph("PowerShell", body_style), Paragraph("$PSVersionTable.PSVersion", body_style), Paragraph("5.1 or 7+", body_style), Paragraph("Executes automated multi-region test suites (.ps1)", body_style)],
        [Paragraph("cURL", body_style), Paragraph("curl.exe --version", body_style), Paragraph("7.68+", body_style), Paragraph("Issues synthetic reads, writes, and health checks", body_style)],
        [Paragraph("OpenSSH", body_style), Paragraph("ssh -V", body_style), Paragraph("8.0+", body_style), Paragraph("Connects to remote AWS EC2 cloud instances using .pem keys", body_style)],
    ]
    tools_table = Table(tools_data, colWidths=[90, 115, 80, USABLE_WIDTH - 285])
    tools_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TABLE_HEADER_BG),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, TABLE_ROW_ALT]),
    ]))
    story.append(tools_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Fast Pre-Flight Verification Script", subsec_title))
    preflight = """# Copy and paste into PowerShell to check all dependencies:
docker --version
docker compose version
python --version
curl.exe --version
Get-Command ssh | Select-Object Name, Source"""
    story.append(create_code_block(preflight, styles))
    story.append(Spacer(1, 8))

    story.append(create_note_box(
        "<b>PowerShell Script Execution:</b> If running .ps1 scripts produces an execution policy restriction error, run: "
        "Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass in your PowerShell terminal.",
        styles, title="Setup Note"
    ))

    story.append(PageBreak())

    # =========================================================
    # PAGE 6: RECIPE 1 - LOCAL DEVELOPMENT SETUP
    # =========================================================
    story.append(Paragraph("Recipe 1: Local Multi-Container Development Setup", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph(
        "The project includes a 6-container Docker Compose file (docker-compose.yml) simulating three distinct regions "
        "(us-central1, europe-west1, and asia-southeast1) connected via a private Docker bridge network.",
        body_style
    ))

    story.append(Paragraph("Local Cluster Port Mapping", subsec_title))
    local_ports = [
        [Paragraph("<b>Region</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Worker Container</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Local Port</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Configured Peer Addresses</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white))],
        [Paragraph("US", body_style), Paragraph("us-central1-worker", body_style), Paragraph("http://localhost:5001", body_style), Paragraph("europe-west1-worker:5000, asia-southeast1-worker:5000", body_style)],
        [Paragraph("Europe", body_style), Paragraph("europe-west1-worker", body_style), Paragraph("http://localhost:5002", body_style), Paragraph("us-central1-worker:5000, asia-southeast1-worker:5000", body_style)],
        [Paragraph("Asia", body_style), Paragraph("asia-southeast1-worker", body_style), Paragraph("http://localhost:5003", body_style), Paragraph("us-central1-worker:5000, europe-west1-worker:5000", body_style)],
    ]
    t_ports = Table(local_ports, colWidths=[60, 130, 110, USABLE_WIDTH - 300])
    t_ports.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TABLE_HEADER_BG),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, TABLE_ROW_ALT]),
    ]))
    story.append(t_ports)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Copy-Paste Local Launch Commands", subsec_title))
    local_run = """# 1. Switch to project directory
cd "c:\\Users\\HP\\Desktop\\ACC\\ACC Miniproject\\geo-cache"

# 2. Build and launch all 6 containers in background
docker compose up --build -d

# 3. Check container status (All 6 should report 'Up')
docker compose ps

# 4. Confirm health across all 3 local regions
curl.exe http://localhost:5001/health
curl.exe http://localhost:5002/health
curl.exe http://localhost:5003/health"""
    story.append(create_code_block(local_run, styles))
    story.append(Spacer(1, 8))

    img_dps = os.path.join("cookbook_assets", "image4.png")
    if os.path.exists(img_dps):
        story.append(Paragraph("<b>Docker Desktop Verification:</b>", subsec_title))
        story.append(Image(img_dps, width=USABLE_WIDTH, height=92))
        story.append(Spacer(1, 4))
        story.append(Paragraph("<font size=7 color='#64748B'>Figure R1: Three Redis and three worker containers running in Docker Desktop.</font>", body_style))

    story.append(PageBreak())

    # =========================================================
    # PAGE 7: RECIPE 2 - AWS MULTI-REGION DEPLOYMENT
    # =========================================================
    story.append(Paragraph("Recipe 2: Multi-Region AWS Cloud Provisioning & Deployment", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph(
        "To test real transatlantic and cross-Pacific latency, the cluster is deployed on three Amazon EC2 instances "
        "in three different AWS regions using docker-compose.aws.yml.",
        body_style
    ))

    story.append(Paragraph("AWS Cloud Infrastructure Topology", subsec_title))
    aws_data = [
        [Paragraph("<b>Node</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>AWS Region</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Location</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Public Elastic IP</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Instance Type</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white))],
        [Paragraph("US Node", body_style), Paragraph("us-east-1", body_style), Paragraph("N. Virginia, USA", body_style), Paragraph("54.242.141.54", body_style), Paragraph("t3.small (2GB RAM)", body_style)],
        [Paragraph("Europe Node", body_style), Paragraph("eu-west-1", body_style), Paragraph("Dublin, Ireland", body_style), Paragraph("34.241.36.71", body_style), Paragraph("t3.small (2GB RAM)", body_style)],
        [Paragraph("Asia Node", body_style), Paragraph("ap-southeast-1", body_style), Paragraph("Singapore, Asia", body_style), Paragraph("52.77.218.56", body_style), Paragraph("t3.small (2GB RAM)", body_style)],
    ]
    t_aws = Table(aws_data, colWidths=[70, 80, 110, 100, USABLE_WIDTH - 360])
    t_aws.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TABLE_HEADER_BG),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, TABLE_ROW_ALT]),
    ]))
    story.append(t_aws)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Security Group Rules", subsec_title))
    story.append(Paragraph("• <b>SSH (Port 22):</b> Authorized exclusively for the administrator IP (/32).", bullet_style))
    story.append(Paragraph("• <b>Cluster Sync (Port 5000):</b> Restricted to peer Elastic IPs and admin IP. Never open to 0.0.0.0/0.", bullet_style))

    story.append(Paragraph("Standardized Node Provisioning Commands", subsec_title))
    ec2_cmds = """# Connect to EC2 instance via SSH
ssh -i geo-key.pem ubuntu@<NODE_PUBLIC_IP>

# 1. Install Docker Engine
curl -fsSL https://get.docker.com | sudo sh

# 2. Clone repository & enter directory
git clone https://github.com/vedaXD/ACC-Miniproject.git
cd ACC-Miniproject/geo-cache

# 3. Apply the environment file for this specific region:
# (Use .env.us on US node, .env.eu on Europe node, .env.asia on Asia node)
cp .env.us .env

# 4. Start Redis and Flask worker
sudo docker compose -f docker-compose.aws.yml up --build -d

# 5. Check local node health
curl http://localhost:5000/health"""
    story.append(create_code_block(ec2_cmds, styles))
    story.append(Spacer(1, 6))

    img_sg = os.path.join("aws_assets", "image1.png")
    if os.path.exists(img_sg):
        story.append(Paragraph("<b>AWS Security Group Verification:</b>", subsec_title))
        story.append(Image(img_sg, width=USABLE_WIDTH, height=90))
        story.append(Spacer(1, 4))
        story.append(Paragraph("<font size=7 color='#64748B'>Figure R2: Port 5000 restricted to peer Elastic IPs.</font>", body_style))

    story.append(PageBreak())

    # =========================================================
    # PAGE 8: RECIPE 3 - HYBRID LOGICAL CLOCKS (HLC)
    # =========================================================
    story.append(Paragraph("Recipe 3: Hybrid Logical Clock (HLC) Implementation", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph(
        "NTP wall clocks are vulnerable to clock drift, while pure Lamport clocks decouple timestamps from physical time. "
        "The Hybrid Logical Clock (HLC) combines physical wall-clock time with a logical counter to guarantee strict monotonicity "
        "and causal ordering across distributed nodes.",
        body_style
    ))

    story.append(Paragraph("Timestamp Structure & Algorithm", subsec_title))
    story.append(Paragraph(
        "Every write is tagged with a 3-tuple: <b><i>T = (physical_ms, logical_counter, node_id)</i></b><br/>"
        "• <b><i>physical_ms:</i></b> Maximum physical wall-clock millisecond observed locally or received from peers.<br/>"
        "• <b><i>logical_counter:</i></b> Increments monotonically if multiple events occur within the same millisecond.<br/>"
        "• <b><i>node_id:</i></b> Unique region identifier (e.g., 'us-east-1') that acts as a deterministic tie-breaker.",
        body_style
    ))

    story.append(Paragraph("HLC Engine Source Code (worker/hlc.py)", subsec_title))
    hlc_code = """class HLC:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self._lock = threading.Lock()
        self._last_physical = 0
        self._counter = 0

    def tick(self):
        \"\"\"Advances clock locally upon a write event.\"\"\"
        with self._lock:
            now = int(time.time() * 1000)
            if now > self._last_physical:
                self._last_physical = now
                self._counter = 0
            else:
                self._counter += 1
            return (self._last_physical, self._counter, self.node_id)

    def update(self, remote_ts):
        \"\"\"Folds remote timestamp into local clock upon receiving a delta.\"\"\"
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
        "<b>Deterministic Comparison Rule:</b> Two timestamps T1 and T2 are compared by checking: (1) physical_ms, then (2) logical_counter, then (3) node_id alphabetically. Every node in the cluster reaches the identical comparison result without consensus rounds.",
        styles, title="Total Order Rule"
    ))

    story.append(PageBreak())

    # =========================================================
    # PAGE 9: RECIPE 4 - LWW-REGISTER CRDT
    # =========================================================
    story.append(Paragraph("Recipe 4: LWW-Register CRDT Conflict Resolution", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph(
        "The Last-Write-Wins Register (LWW-Register) is a state-based CRDT used for general string key-value storage. "
        "When conflicting writes occur concurrently in different regions, the update with the highest HLC timestamp deterministically wins.",
        body_style
    ))

    story.append(Paragraph("LWW-Register Implementation (worker/crdt.py)", subsec_title))
    lww_code = """from hlc import compare as hlc_compare

class LWWRegister:
    \"\"\"
    Stored representation in Redis per key:
    {"value": "<string_value>", "ts": [physical_ms, logical_counter, node_id]}
    \"\"\"

    @staticmethod
    def merge(local_entry, remote_entry):
        \"\"\"
        Idempotent and commutative merge function.
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
    story.append(Paragraph("1. Client A sends POST /set (key=user:100, value='active') to <b>US</b> (ts: [1790925567663, 0, 'us-east-1']).", bullet_style))
    story.append(Paragraph("2. Client B sends POST /set (key=user:100, value='inactive') to <b>Europe</b> (ts: [1790925567744, 0, 'eu-west-1']).", bullet_style))
    story.append(Paragraph("3. When US replicates to Europe: Europe compares 1790925567744 > 1790925567663 and keeps 'inactive'.", bullet_style))
    story.append(Paragraph("4. When Europe replicates to US: US compares 1790925567744 > 1790925567663 and overwrites with 'inactive'.", bullet_style))
    story.append(Paragraph("5. Both nodes converge to identical winning state without distributed locks or coordination.", bullet_style))

    story.append(Spacer(1, 6))
    story.append(create_note_box(
        "<b>Mathematical Invariant:</b> The merge operation is commutative (merge(A,B) = merge(B,A)) and idempotent (merge(A,A) = A). Network retries, duplicate deliveries, and out-of-order packets cannot corrupt the database state.",
        styles, title="CRDT Mathematical Property"
    ))

    story.append(PageBreak())

    # =========================================================
    # PAGE 10: RECIPE 5 - STATE-BASED PN-COUNTER CRDT
    # =========================================================
    story.append(Paragraph("Recipe 5: State-Based PN-Counter CRDT", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph(
        "In a multi-master cache, using raw Redis INCR commands causes lost updates when concurrent increments occur across regions. "
        "The Positive-Negative Counter (PN-Counter) avoids lost updates by maintaining per-node increment and decrement vectors.",
        body_style
    ))

    story.append(Paragraph("PN-Counter Implementation (worker/crdt.py)", subsec_title))
    pn_code = """class PNCounter:
    \"\"\"
    State representation in Redis:
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
        \"\"\"Net counter value = sum(P) - sum(N)\"\"\"
        total_p = sum(state.get("P", {}).values())
        total_n = sum(state.get("N", {}).values())
        return total_p - total_n

    @staticmethod
    def merge(local_state, remote_state):
        \"\"\"Merges states by computing per-node maxima.\"\"\"
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
        "<b>Zero Lost Updates:</b> Because node A only increments P['us-east-1'] and node B only increments P['eu-west-1'], taking the maximum vector for each node during merge guarantees that all regional increments are preserved additively.",
        styles, title="Additive Convergence Guarantee"
    ))

    story.append(PageBreak())

    # =========================================================
    # PAGE 11: RECIPE 6 - WRITE-BEHIND REPLICATION & MEMORY FIX
    # =========================================================
    story.append(Paragraph("Recipe 6: Asynchronous Write-Behind Replication Engine & Buffer Capping", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph(
        "The Flask worker accumulates writes in an in-memory write-behind buffer and flushes them to peers every 500ms. "
        "Below is the production-hardened replication loop with strict queue limits.",
        body_style
    ))

    story.append(Paragraph("Replication Loop (worker/app.py)", subsec_title))
    rep_code = """buffer_lock = threading.Lock()
pending_deltas = []  # list of {"type": "lww"|"counter", "key": ..., "entry"/"state": ...}
MAX_BUFFER_SIZE = 5000  # Hard ceiling prevents unbounded memory growth

def replication_loop():
    \"\"\"Background daemon: flushes deltas to peers every SYNC_INTERVAL_MS.\"\"\"
    while True:
        time.sleep(SYNC_INTERVAL_MS / 1000)
        with buffer_lock:
            if not pending_deltas:
                continue
            batch = pending_deltas[:]
            pending_deltas.clear()

        # Send delta batch asynchronously to all peers
        for peer in PEERS:
            try:
                requests.post(f"http://{peer}/sync", json={"deltas": batch}, timeout=2)
            except requests.RequestException as e:
                # Peer unreachable: Re-buffer failed batch but enforce buffer ceiling
                with buffer_lock:
                    pending_deltas.extend(batch)
                    if len(pending_deltas) > MAX_BUFFER_SIZE:
                        overflow = len(pending_deltas) - MAX_BUFFER_SIZE
                        del pending_deltas[:overflow]  # Drop oldest deltas to protect RAM
                        print(f"[{REGION_ID}] Buffer capped, dropped {overflow} oldest deltas")
                print(f"[{REGION_ID}] Sync to {peer} failed: {e}")"""
    story.append(create_code_block(rep_code, styles))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Engineering Finding: Fixing the Unbounded Memory Growth Defect", subsec_title))
    story.append(Paragraph(
        "Under extended network partitions, failed sync batches were re-appended to pending_deltas on every tick without deduplication. "
        "Over a 15-minute outage, the queue grew to over 45,000 items, causing the Linux kernel Out-Of-Memory (OOM) killer to terminate "
        "the worker container. Capping the buffer to 5,000 items resolved this failure mode permanently.",
        body_style
    ))
    story.append(Spacer(1, 4))

    img_oom = os.path.join("cookbook_assets", "image10.png")
    if os.path.exists(img_oom):
        story.append(Image(img_oom, width=USABLE_WIDTH, height=52))
        story.append(Spacer(1, 4))
        story.append(Paragraph("<font size=7 color='#64748B'>Figure R6: Root-cause analysis of the unbounded memory growth defect in the worker retry logic.</font>", body_style))

    story.append(PageBreak())

    # =========================================================
    # PAGE 12: RECIPE 7 - LWW CONFLICT DEMONSTRATION
    # =========================================================
    story.append(Paragraph("Recipe 7: Verification — Concurrent Conflicting Writes (01-lww-demo.ps1)", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph(
        "This recipe executes two conflicting writes to the exact same key at the same instant: 'active' to US and 'inactive' to Europe. "
        "It verifies that all three nodes converge to the identical winning value and HLC timestamp.",
        body_style
    ))

    story.append(Paragraph("PowerShell Test Script Execution", subsec_title))
    lww_run = """# Run from the geo-cache directory:
cd "c:\\Users\\HP\\Desktop\\ACC\\ACC Miniproject\\geo-cache"
.\\01-lww-demo.ps1"""
    story.append(create_code_block(lww_run, styles))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Test Script Logic Walkthrough", subsec_title))
    story.append(Paragraph("1. Generates a unique timestamped key: demo-lww-YYYYMMDD-HHmmss-fff.", bullet_style))
    story.append(Paragraph("2. Uses Start-Job to fire parallel POST /set requests simultaneously to US (54.242.141.54:5000) and Europe (34.241.36.71:5000).", bullet_style))
    story.append(Paragraph("3. Waits 3 seconds for asynchronous cross-region replication.", bullet_style))
    story.append(Paragraph("4. Queries GET /get/<key> on US, Europe, and Asia.", bullet_style))
    story.append(Paragraph("5. Confirms all three regions hold the same winning value and HLC timestamp.", bullet_style))
    story.append(Spacer(1, 6))

    img_lww = os.path.join("cookbook_assets", "image16.png")
    if os.path.exists(img_lww):
        story.append(Paragraph("<b>Observed Execution Output:</b>", subsec_title))
        story.append(Image(img_lww, width=USABLE_WIDTH, height=85))
        story.append(Spacer(1, 4))
        story.append(Paragraph("<font size=7 color='#64748B'>Figure R7: Test execution confirming all 3 regions converged to identical winning value.</font>", body_style))

    story.append(Spacer(1, 6))
    story.append(create_note_box(
        "<b>Expected Console Output:</b> The script prints SUCCESS: ALL THREE REGIONS CONVERGED! along with the winning value and winning HLC timestamp.",
        styles, title="Verification Checkpoint"
    ))

    story.append(PageBreak())

    # =========================================================
    # PAGE 13: RECIPE 8 - PN-COUNTER DEMONSTRATION
    # =========================================================
    story.append(Paragraph("Recipe 8: Verification — Concurrent Counter Increments (02-pn-counter-demo.ps1)", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph(
        "This test verifies that distributed counter increments issued concurrently across three continents are merged "
        "additively with zero lost updates.",
        body_style
    ))

    story.append(Paragraph("PowerShell Test Script Execution", subsec_title))
    pn_run = """# Run from the geo-cache directory:
cd "c:\\Users\\HP\\Desktop\\ACC\\ACC Miniproject\\geo-cache"
.\\02-pn-counter-demo.ps1"""
    story.append(create_code_block(pn_run, styles))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Test Script Logic Walkthrough", subsec_title))
    story.append(Paragraph("1. Generates a unique key: demo-pn-YYYYMMDD-HHmmss-fff.", bullet_style))
    story.append(Paragraph("2. Concurrently dispatches increments using parallel background jobs: <b>US (+5)</b>, <b>Europe (+3)</b>, and <b>Asia (+2)</b>.", bullet_style))
    story.append(Paragraph("3. Polls GET /counter/<key> across all three nodes every 500ms until convergence.", bullet_style))
    story.append(Paragraph("4. Confirms that every node reports a counter value of exactly <b>10</b> (5 + 3 + 2).", bullet_style))
    story.append(Spacer(1, 6))

    img_pn = os.path.join("cookbook_assets", "image8.png")
    if os.path.exists(img_pn):
        story.append(Paragraph("<b>Observed Execution Output:</b>", subsec_title))
        story.append(Image(img_pn, width=USABLE_WIDTH, height=75))
        story.append(Spacer(1, 4))
        story.append(Paragraph("<font size=7 color='#64748B'>Figure R8: Terminal output showing counter value 10 converging across all 3 regions.</font>", body_style))

    story.append(Spacer(1, 6))
    story.append(create_note_box(
        "<b>Expected Console Output:</b> The script prints SUCCESS: all regions converged to 10. showing US -> 10, Europe -> 10, Asia -> 10.",
        styles, title="Verification Checkpoint"
    ))

    story.append(PageBreak())

    # =========================================================
    # PAGE 14: RECIPE 9 - FAULT TOLERANCE & OUTAGE RECOVERY
    # =========================================================
    story.append(Paragraph("Recipe 9: Verification — Fault Tolerance & Regional Outage Recovery", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph(
        "This recipe simulates a catastrophic regional container failure. The target regional worker is stopped via SSH. "
        "Surviving nodes continue accepting client updates without interruption. When the stopped worker is revived, "
        "it catches up automatically on all queued write-behind deltas.",
        body_style
    ))

    story.append(Paragraph("PowerShell Test Script Execution", subsec_title))
    outage_run = """# Run from the geo-cache directory:
cd "c:\\Users\\HP\\Desktop\\ACC\\ACC Miniproject\\geo-cache"
.\\03-worker-outage-recovery.ps1"""
    story.append(create_code_block(outage_run, styles))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Test Script Logic Walkthrough", subsec_title))
    story.append(Paragraph("1. Prompts you to pick a worker to take down (e.g., Node 3: Asia).", bullet_style))
    story.append(Paragraph("2. Executes docker compose stop worker on the remote node via SSH (Redis remains running).", bullet_style))
    story.append(Paragraph("3. Sends live counter increments to surviving nodes: US (+4) and Europe (+6).", bullet_style))
    story.append(Paragraph("4. Verifies surviving nodes accept writes and return status 200 OK.", bullet_style))
    story.append(Paragraph("5. Prompts you to hit ENTER to restart the stopped worker (docker compose start worker).", bullet_style))
    story.append(Paragraph("6. Within 2 sync cycles, peers flush their buffered deltas; the revived node converges to 10.", bullet_style))
    story.append(Spacer(1, 6))

    img_outage = os.path.join("cookbook_assets", "image1.png")
    if os.path.exists(img_outage):
        story.append(Paragraph("<b>Observed Execution Output:</b>", subsec_title))
        story.append(Image(img_outage, width=USABLE_WIDTH, height=75))
        story.append(Spacer(1, 4))
        story.append(Paragraph("<font size=7 color='#64748B'>Figure R9: Automatic catch-up and reconciliation after container restart.</font>", body_style))

    story.append(Spacer(1, 6))
    story.append(create_note_box(
        "<b>Expected Console Output:</b> RECOVERY SUCCESS: all three regions converged. The restarted node returns the exact total (10) without any human data repair.",
        styles, title="Verification Checkpoint"
    ))

    story.append(PageBreak())

    # =========================================================
    # PAGE 15: RECIPE 10 - PERFORMANCE BENCHMARKING
    # =========================================================
    story.append(Paragraph("Recipe 10: Performance Benchmarking & Latency Analysis", sec_title))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    story.append(Paragraph(
        "Empirical benchmarks measure the real performance advantages of active-active caching compared to centralized single-primary architectures.",
        body_style
    ))

    story.append(Paragraph("Measured Latency & Convergence Figures", subsec_title))
    bench_data = [
        [Paragraph("<b>Metric</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Scenario / Route</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Measured Value</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
         Paragraph("<b>Architectural Benefit</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white))],
        [Paragraph("Client Latency (Local)", body_style), Paragraph("India Client -> Singapore (Asia)", body_style), Paragraph("<b>166 ms</b>", body_style), Paragraph("Direct connection to nearest regional cache", body_style)],
        [Paragraph("Client Latency (Distant)", body_style), Paragraph("India Client -> N. Virginia (US)", body_style), Paragraph("<b>504 ms</b>", body_style), Paragraph("3.0x slower latency without geo-cache", body_style)],
        [Paragraph("Client Latency (Distant)", body_style), Paragraph("India Client -> Ireland (Europe)", body_style), Paragraph("<b>522 ms</b>", body_style), Paragraph("3.1x slower latency without geo-cache", body_style)],
        [Paragraph("Convergence Delay", body_style), Paragraph("US write -> Asia readable (10 runs)", body_style), Paragraph("<b>924 ms – 1413 ms</b><br/>(Avg: 1120 ms)", body_style), Paragraph("Bounded by 500ms sync loop + network RTT", body_style)],
        [Paragraph("Replication Accuracy", body_style), Paragraph("100 concurrent LWW & PN operations", body_style), Paragraph("<b>100% Convergence</b>", body_style), Paragraph("Zero dropped increments or split-brain states", body_style)],
    ]
    t_bench = Table(bench_data, colWidths=[110, 140, 95, USABLE_WIDTH - 345])
    t_bench.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TABLE_HEADER_BG),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, TABLE_ROW_ALT]),
    ]))
    story.append(t_bench)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Copy-Paste Latency Measurement Command", subsec_title))
    bench_cmd = """# Measure total HTTP round-trip latency to each region from local machine
curl.exe -s -o NUL -w "Asia (Singapore) : %{time_total}s\\n" http://52.77.218.56:5000/health
curl.exe -s -o NUL -w "US (N. Virginia)  : %{time_total}s\\n" http://54.242.141.54:5000/health
curl.exe -s -o NUL -w "Europe (Ireland)  : %{time_total}s\\n" http://34.241.36.71:5000/health"""
    story.append(create_code_block(bench_cmd, styles))
    story.append(Spacer(1, 6))

    story.append(create_note_box(
        "<b>Performance Takeaway:</b> By routing traffic to the nearest regional worker, clients observe a <b>67% latency reduction</b> (166 ms vs 504 ms) while retaining write availability during cross-continental network partitions.",
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
         Paragraph("<b>Description & Behavior</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white))],
        [Paragraph("/set", body_style), Paragraph("POST", body_style), Paragraph('{"key":"k", "value":"v"}', body_style), Paragraph("Writes LWW-Register key; ticks HLC; buffers delta", body_style)],
        [Paragraph("/get/&lt;key&gt;", body_style), Paragraph("GET", body_style), Paragraph("None", body_style), Paragraph("Returns current value, HLC timestamp tuple, and region", body_style)],
        [Paragraph("/incr", body_style), Paragraph("POST", body_style), Paragraph('{"key":"k", "amount":1}', body_style), Paragraph("Increments PN-Counter local vector; buffers delta", body_style)],
        [Paragraph("/counter/&lt;key&gt;", body_style), Paragraph("GET", body_style), Paragraph("None", body_style), Paragraph("Computes sum(P) - sum(N) across all known regions", body_style)],
        [Paragraph("/sync", body_style), Paragraph("POST", body_style), Paragraph('{"deltas": [...]}', body_style), Paragraph("Receives delta batch from peer; folds HLC; merges CRDT", body_style)],
        [Paragraph("/health", body_style), Paragraph("GET", body_style), Paragraph("None", body_style), Paragraph("Reports node health, assigned REGION_ID, and peer list", body_style)],
    ]
    t_api = Table(api_data, colWidths=[90, 45, 130, USABLE_WIDTH - 265])
    t_api.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TABLE_HEADER_BG),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, TABLE_ROW_ALT]),
    ]))
    story.append(t_api)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Key Environment Variables", subsec_title))
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
    t_env = Table(env_data, colWidths=[120, 160, USABLE_WIDTH - 280])
    t_env.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TABLE_HEADER_BG),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, TABLE_ROW_ALT]),
    ]))
    story.append(t_env)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Developer CLI Quick Reference", subsec_title))
    quick_cmds = """# Local launch:
cd geo-cache && docker compose up --build -d

# Run all test suites:
.\\01-lww-demo.ps1                 # Concurrent conflicting writes
.\\02-pn-counter-demo.ps1          # Multi-region counter increments
.\\03-worker-outage-recovery.ps1   # Worker outage & reconciliation"""
    story.append(create_code_block(quick_cmds, styles))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Engineering Cookbook PDF successfully created: {filename}")

if __name__ == "__main__":
    build_pdf()
