# Geo-Distributed Active-Active Cache Cluster
## Engineering Cookbook — Excel-Ready Tabular Documentation

> **Instructions for Excel Insertion:**
> 1. To copy any table below into Microsoft Excel, select the entire table (including header), press `Ctrl + C`, open Excel, select cell `A1`, and press `Ctrl + V`.
> 2. Alternatively, use Excel's **Data $\to$ From Text/CSV** to import tabular data cleanly into individual workbook sheets.
> 3. Each table below represents a ready-made Excel sheet for academic or technical project tracking.

---

### Sheet 1: Project Metadata & Team Roster

| Field | Value / Details | Reference |
| :--- | :--- | :--- |
| **Project Title** | Geo-Distributed Active-Active Cache Cluster with CRDT Conflict Resolution | ACC-MiniProject |
| **Course & Semester** | Advanced Cloud Computing (ACC) • Semester 7 • Academic Year 2026 | Computer Engineering |
| **Institution** | Vivekanand Education Society's Institute of Technology (VESIT), Mumbai | Mumbai University |
| **Project Mentor** | Prof. Richard Joseph | Department Faculty |
| **Project Group No.** | Group 6 | Academic Year 2023-2027 |
| **GitHub Repository** | https://github.com/vedaXD/ACC-Miniproject | Open Source Public Repo |
| **YouTube Video Demo** | https://youtu.be/OwtLWvFsUC4 | Unlisted 6-minute Video |
| **UN SDG Alignment** | SDG 9: Industry, Innovation and Infrastructure | Resilient Infrastructure |
| **Team Member 1** | Veda Patki (Roll 43) • Class D17C • 2023.veda.patki@ves.ac.in | Containerization, Cloud Automation, Demos |
| **Team Member 2** | Akul Patre (Roll 44) • Class D17C • 2023.akul.patre@ves.ac.in | AWS Infrastructure, Networking, Benchmarking |
| **Team Member 3** | Isha Palkar (Roll 37) • Class D17C • 2023.isha.palkar@ves.ac.in | Hybrid Logical Clock (HLC), Causal Ordering |
| **Team Member 4** | Soham Patil (Roll 40) • Class D17C • 2023.soham.patil@ves.ac.in | CRDTs (LWW & PN-Counter), Flask API Gateway |

---

### Sheet 2: Technology Stack & Architectural Roles

| Component | Technology | Version | Architectural Responsibility |
| :--- | :--- | :--- | :--- |
| **In-Memory Cache** | Redis | 7.0-alpine | Sub-millisecond region-local key-value & counter storage |
| **Gateway & Replication** | Python / Flask | 3.11-slim / Flask 3.x | Client REST API (`/set`, `/get`, `/incr`, `/counter`) & sync engine |
| **Causal Timestamping** | Hybrid Logical Clock | Custom `hlc.py` | Monotonic `(physical_ms, counter, node_id)` total ordering |
| **Key-Value Resolution** | LWW-Register CRDT | Custom `crdt.py` | Last-Write-Wins deterministic merge with node-ID tie breaker |
| **Distributed Counters** | State-Based PN-Counter | Custom `crdt.py` | Additive per-node maxima vector merging with zero lost counts |
| **Write Strategy** | Asynchronous Write-Behind | Custom `app.py` | Immediate local commit + 500ms background thread push |
| **Memory Safety Buffer** | Thread-safe queue | Mutex bounded | Capped at 5,000 deltas to prevent OOM kills during partitions |
| **Cloud Virtual Machines** | AWS EC2 | t3.small (2GB RAM) | Multi-master nodes in US, Europe, and Asia regions |
| **Local Containerization** | Docker Compose | Compose v2 | 6-container bridge mesh mapped to ports 5001, 5002, 5003 |

---

### Sheet 3: Multi-Region Cloud Topology & Network Mapping

| Logical Node | AWS Region | Physical Location | Public Elastic IP | Private Subnet IP | Instance Type | OS Version | Security Group Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **US Node** | `us-east-1` | N. Virginia, USA | `54.242.141.54` | `172.31.27.19` | `t3.small` (2 vCPU, 2GB) | Ubuntu 24.04 LTS | TCP 5000: Peer IPs + Admin IP only |
| **Europe Node** | `eu-west-1` | Dublin, Ireland | `34.241.36.71` | `172.31.28.160` | `t3.small` (2 vCPU, 2GB) | Ubuntu 24.04 LTS | TCP 5000: Peer IPs + Admin IP only |
| **Asia Node** | `ap-southeast-1` | Singapore, Asia | `52.77.218.56` | `172.31.45.223` | `t3.small` (2 vCPU, 2GB) | Ubuntu 24.04 LTS | TCP 5000: Peer IPs + Admin IP only |

---

### Sheet 4: Ten Engineering Recipes & Runbook Matrix

| Recipe # | Recipe Title | Target Scope | Primary Commands / Scripts | Success Verification Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **Recipe 1** | Local Cluster Emulation | 6 Docker containers | `docker compose up --build -d` | All 6 containers Up; ports 5001, 5002, 5003 healthy |
| **Recipe 2** | AWS Multi-Region Deploy | 3 AWS EC2 instances | `docker compose -f docker-compose.aws.yml up -d` | `/health` endpoint returns assigned region and peers |
| **Recipe 3** | Hybrid Logical Clock (HLC) | `worker/hlc.py` | `clock.tick()` and `clock.update(remote_ts)` | Monotonic timestamps `(physical, counter, node)` |
| **Recipe 4** | LWW-Register CRDT | `worker/crdt.py` | `LWWRegister.merge(local, remote)` | Higher HLC timestamp deterministically wins |
| **Recipe 5** | PN-Counter CRDT | `worker/crdt.py` | `PNCounter.merge(local, remote)` | Computes $\sum P - \sum N$; no lost increments |
| **Recipe 6** | Write-Behind Replication | `worker/app.py` | `replication_loop()` with 5000 cap | Memory stays bounded under long partitions |
| **Recipe 7** | Conflicting Writes Test | Cloud & Local | `.\01-lww-demo.ps1` | US ("active") vs EU ("inactive") converge to same state |
| **Recipe 8** | Distributed Counter Test | Cloud & Local | `.\02-pn-counter-demo.ps1` | US (+5) + EU (+3) + ASIA (+2) converges to 10 everywhere |
| **Recipe 9** | Outage & Partition Test | Cloud & Local | `.\03-worker-outage-recovery.ps1` | Stopped worker restarts and auto-catches up on queued deltas |
| **Recipe 10** | Latency Benchmarking | Global routes | `curl -w "%{time_total}\n" <ip>:5000/health` | Nearest region yields 166ms vs 500+ms cross-ocean |

---

### Sheet 5: REST API Endpoint Catalog

| Endpoint | Method | Input Parameters / Payload | Output JSON Response | Status Code | Architectural Function |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/set` | `POST` | `{"key":"user:100", "value":"active"}` | `{"status":"ok", "key":"...", "value":"...", "ts":[...], "region":"..."}` | 200 OK | Writes LWW key; ticks local HLC; enqueues delta |
| `/get/<key>` | `GET` | Key string in URL path | `{"key":"...", "value":"...", "ts":[...], "region":"..."}` | 200 OK | Fetches current value and HLC timestamp from local Redis |
| `/incr` | `POST` | `{"key":"post:likes", "amount":1}` | `{"status":"ok", "key":"...", "value":10, "region":"..."}` | 200 OK | Increments local region slot in PN-Counter vector |
| `/counter/<key>` | `GET` | Key string in URL path | `{"key":"...", "value":10, "region":"..."}` | 200 OK | Computes sum of positive vectors minus negative vectors |
| `/sync` | `POST` | `{"deltas": [{"type":"lww", ...}, ...]}` | `{"status":"merged", "region":"...", "count":N}` | 200 OK | Peer anti-entropy endpoint; advances HLC; merges CRDT |
| `/health` | `GET` | None | `{"status":"up", "region":"...", "peers":[...]}` | 200 OK | Validates worker status, identity, and peer addresses |

---

### Sheet 6: Environment Variables Reference

| Variable Name | Default Local Value | AWS US Example | AWS Europe Example | AWS Asia Example | Functional Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `REGION_ID` | `us-central1` | `us-east-1` | `eu-west-1` | `ap-southeast-1` | Unique node identifier used for tie-breaking and counter vectors |
| `REDIS_HOST` | `us-central1-redis` | `redis` | `redis` | `redis` | Docker container hostname or IP of the local Redis instance |
| `PEERS` | `europe-west1-worker:5000` | `34.241.36.71:5000,52.77.218.56:5000` | `54.242.141.54:5000,52.77.218.56:5000` | `54.242.141.54:5000,34.241.36.71:5000` | Comma-separated list of peer worker host:port endpoints |
| `SYNC_INTERVAL_MS` | `500` | `500` | `500` | `500` | Frequency in milliseconds for flushing write-behind deltas |
| `SIMULATED_LATENCY_MS` | `0` | `0` | `0` | `0` | Artificial delay injected into replication calls for local testing |

---

### Sheet 7: Test Cases & Validation Results Matrix

| Test ID | Test Scenario | Execution Environment | Expected Behavior | Observed Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Basic write and convergence | Local Docker (ports 5001-5003) | Write to US appears on EU and Asia within 1s | Replicated with matching value and HLC timestamp | **PASS** |
| **TC-02** | Concurrent conflicting writes (LWW) | AWS EC2 (US & Europe) | Node with later HLC wins deterministically | All 3 regions converged to identical winning value | **PASS** |
| **TC-03** | Multi-region concurrent counter (PN) | AWS EC2 (US, EU, Asia) | US +5, EU +3, Asia +2 converges to total 10 | All 3 regions converged to exact total 10 | **PASS** |
| **TC-04** | Cross-ocean convergence timing | AWS (`us-east-1` $\to$ `ap-southeast-1`) | Appears within sync interval + network delay | Min: 924 ms, Max: 1413 ms, Avg: 1120 ms (10 runs) | **PASS** |
| **TC-05** | Regional client latency reduction | India laptop $\to$ AWS nodes | Nearest node (Singapore) fastest response | Asia: 166 ms vs US: 504 ms vs Europe: 522 ms (67% gain) | **PASS** |
| **TC-06** | Outage & automatic catch-up | AWS EC2 (Asia worker stopped) | Surviving nodes stay up; stopped node catches up | Asia catches up on queued deltas within 1 sync cycle | **PASS** |
| **TC-07** | Bounded memory under partition | Local Docker / AWS EC2 | Queue does not cause Out-Of-Memory crash | Buffer capped at 5,000 deltas; 0 OOM crashes | **PASS** |

---

### Sheet 8: Latency & Convergence Benchmarks

| Measurement Scenario | Origin Client | Target Endpoint | Distance / Route | Observed RTT / Latency | Architectural Performance Benefit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Nearest Region (Active-Active)** | India | `52.77.218.56` (Singapore) | Direct South Asia $\to$ Southeast Asia | **166 ms** | Baseline optimal response time for local users |
| **Distant Primary (Centralized US)** | India | `54.242.141.54` (N. Virginia) | Cross-Pacific / Transatlantic | **504 ms** | **3.0x higher latency** if using single-primary cache |
| **Distant Primary (Centralized EU)** | India | `34.241.36.71` (Dublin) | India $\to$ Middle East $\to$ Western Europe | **522 ms** | **3.1x higher latency** if using single-primary cache |
| **Replication Convergence (Min)** | US | Asia (`us-east-1` $\to$ `ap-se-1`) | Global AWS backbone fiber | **924 ms** | Bounded by 500ms sync loop + ~420ms TCP RTT |
| **Replication Convergence (Max)** | US | Asia (`us-east-1` $\to$ `ap-se-1`) | Global AWS backbone fiber | **1,413 ms** | Peak network jitter under cross-ocean routing |
| **Replication Convergence (Avg)** | US | Asia (`us-east-1` $\to$ `ap-se-1`) | Global AWS backbone fiber (10 runs) | **1,120 ms** | Guaranteed eventual consistency in ~1.1 seconds |

---

### Sheet 9: UN SDG 9 Alignment & Sustainability Matrix

| Dimension | Evaluation Question | Project Assessment & Engineering Evidence |
| :--- | :--- | :--- |
| **SDG 9: Industry, Innovation & Infrastructure** | Does the design build resilient, high-availability digital systems? | **Yes:** Active-active multi-master architecture eliminates single-point-of-failure risks and remains fully writable during transatlantic network cuts. |
| **SDG 8: Decent Work & Economic Growth** | Does the system democratize high-speed digital performance? | **Yes:** Slashes latency from 500ms+ down to 166ms for users in developing regions (e.g., India) without requiring expensive enterprise databases. |
| **SDG 13: Climate Action & Energy Efficiency** | How is cloud energy consumption optimized? | **Optimized:** Runs on lightweight `t3.small` instances (2GB RAM) and Alpine containers; nodes can be idled/scaled dynamically during low-traffic windows. |
| **Resource Efficiency** | How is network bandwidth conserved during replication? | **Delta-only replication:** Sends only modified keys/counters rather than full state dumps; in-memory buffer is capped at 5,000 items. |
