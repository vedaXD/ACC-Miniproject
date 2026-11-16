# Geo-Distributed Active-Active Cache Cluster
### Architectural Blueprint & Engineering Cookbook

[![YouTube Demo](https://img.shields.io/badge/YouTube-Demo%20Video-red?logo=youtube)](https://youtu.be/OwtLWvFsUC4)
[![Docker](https://img.shields.io/badge/Docker-Compose%20v2-blue?logo=docker)](https://www.docker.com/)
[![AWS EC2](https://img.shields.io/badge/AWS-3%20Regions%20(EC2)-orange?logo=amazon-aws)](https://aws.amazon.com/ec2/)
[![Redis](https://img.shields.io/badge/Redis-7.0%20Alpine-red?logo=redis)](https://redis.io/)
[![Python](https://img.shields.io/badge/Python-3.11%20Flask-yellow?logo=python)](https://python.org/)

> **Live Video Demonstration:** [https://youtu.be/OwtLWvFsUC4](https://youtu.be/OwtLWvFsUC4)  
> **PDF Cookbook:** [`Geo_Distributed_Cache_Cookbook.pdf`](Geo_Distributed_Cache_Cookbook.pdf)  
> **Excel-Ready Documentation:** [`COOKBOOK_EXCEL_READY.md`](COOKBOOK_EXCEL_READY.md)  

---

## ⚡ What is this Project?
An **Active-Active (Multi-Master) Geo-Distributed Cache Cluster** designed to serve global clients with sub-millisecond local latency.

Traditional single-region caches force global users (e.g. in Asia) to suffer **400ms – 550ms round-trip latency** on every read and write to a central US primary. This cluster runs active replicas across three continents (**US**, **Europe**, and **Asia**). Every node accepts local reads and writes, replicates asynchronously in the background every 500ms, and deterministically merges concurrent writes using **Hybrid Logical Clocks (HLC)** and **Conflict-Free Replicated Data Types (CRDTs)** without requiring distributed locks or consensus algorithms (Paxos/Raft).

---

## 🛠️ Stack Architecture

| Component | Technology | Role in System |
| :--- | :--- | :--- |
| **In-Memory Storage** | Redis 7 (Alpine) | Sub-millisecond region-local data store for raw keys & counters |
| **Worker & Gateway** | Python 3.11 + Flask | HTTP API (`/set`, `/get`, `/incr`, `/counter`) & peer `/sync` engine |
| **Causal Ordering** | Hybrid Logical Clock (HLC) | Monotonic timestamps: `(physical_ms, logical_counter, node_id)` |
| **Key-Value CRDT** | LWW-Register | Last-Write-Wins deterministic merge with node-ID tie breaker |
| **Counter CRDT** | State-Based PN-Counter | Positive-Negative vectors with idempotent per-node maxima merging |
| **Replication Strategy** | Asynchronous Write-Behind | Immediate local commit + 500ms background thread push (capped at 5,000) |
| **Cloud Infrastructure** | AWS EC2 (3 Regions) | `us-east-1` (US), `eu-west-1` (Europe), `ap-southeast-1` (Asia) |
| **Local Emulation** | Docker Compose v2 | 6-container bridge cluster mapped to ports `5001`, `5002`, and `5003` |

---

## 🌐 Replication Pipeline

```
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
```

---

## 🏃 How to Run the Program

### Method 1: Run Locally in 60 Seconds (Docker Compose)

No cloud account required. This runs the full 3-region active-active cluster locally on your PC:

1. **Clone and enter the directory:**
   ```bash
   git clone https://github.com/vedaXD/ACC-Miniproject.git
   cd ACC-Miniproject/geo-cache
   ```

2. **Launch all 6 containers:**
   ```bash
   docker compose up --build -d
   ```

3. **Verify running services:**
   ```bash
   docker compose ps
   ```
   * **US Region:** `http://localhost:5001`
   * **Europe Region:** `http://localhost:5002`
   * **Asia Region:** `http://localhost:5003`

4. **Verify health:**
   ```powershell
   curl.exe http://localhost:5001/health
   curl.exe http://localhost:5002/health
   curl.exe http://localhost:5003/health
   ```

---

### Method 2: Deploy Across AWS Multi-Region EC2

Deploy across 3 AWS regions for authentic transatlantic and cross-Pacific testing:
* **US Node:** `us-east-1` (N. Virginia) • IP: `54.242.141.54`
* **Europe Node:** `eu-west-1` (Dublin) • IP: `34.241.36.71`
* **Asia Node:** `ap-southeast-1` (Singapore) • IP: `52.77.218.56`

#### On each EC2 instance (`t3.small`, Ubuntu 24.04):
```bash
# 1. Connect via SSH
ssh -i geo-key.pem ubuntu@<PUBLIC_IP>

# 2. Install Docker
curl -fsSL https://get.docker.com | sudo sh

# 3. Clone repository
git clone https://github.com/vedaXD/ACC-Miniproject.git
cd ACC-Miniproject/geo-cache

# 4. Apply region configuration (.env.us / .env.eu / .env.asia)
cp .env.us .env   # On US node

# 5. Start Redis + Worker
sudo docker compose -f docker-compose.aws.yml up --build -d

# 6. Verify health
curl -s http://localhost:5000/health
```

> **Security Group Inbound Rule:** Port `5000` is allowed only from peer Elastic IPs and the admin IP (`/32`). Never allow `0.0.0.0/0`.

---

## 🧪 How to Run the Tests

From the `geo-cache/` directory in PowerShell:

### 1. Test Concurrent Conflicting Writes (LWW-Register)
Simultaneously sends conflicting values for the same key (`user:100 = "active"` to US and `"inactive"` to Europe):
```powershell
.\01-lww-demo.ps1
```
* **Expected Output:** Both writes succeed immediately locally. Replicas sync within 1.5s, and all 3 regions converge to the write with the higher HLC timestamp.

### 2. Test Multi-Region Distributed Counter (PN-Counter)
Fires concurrent increments simultaneously from 3 continents: US (+5), Europe (+3), Asia (+2):
```powershell
.\02-pn-counter-demo.ps1
```
* **Expected Output:** All 3 nodes evaluate `sum(P) - sum(N)` and converge to **`10`** with zero lost counts.

### 3. Test Regional Outage & Automatic Recovery
Stops a remote worker container (`docker compose stop worker`), writes updates to surviving nodes, restarts the worker, and observes automatic delta reconciliation:
```powershell
.\03-worker-outage-recovery.ps1
```
* **Expected Output:** Surviving nodes continue accepting writes with zero downtime. The restarted node catches up automatically within 1 sync cycle.

---

## ⚡ Manual cURL Verification Commands

```powershell
# 1. Write key to US node:
curl.exe -X POST http://54.242.141.54:5000/set -H "Content-Type: application/json" -d '{\"key\":\"session:123\",\"value\":\"user_profile\"}'

# 2. Read immediately from Europe or Asia (converges in ~1 second):
curl.exe http://34.241.36.71:5000/get/session:123
curl.exe http://52.77.218.56:5000/get/session:123

# 3. Increment counter on Asia:
curl.exe -X POST http://52.77.218.56:5000/incr -H "Content-Type: application/json" -d '{\"key\":\"post:999:views\",\"amount\":1}'

# 4. Fetch counter from US:
curl.exe http://54.242.141.54:5000/counter/post:999:views
```

---

## 📊 Measured Benchmarks

| Metric | Route / Scenario | Observed Result | Impact |
| :--- | :--- | :--- | :--- |
| **Local Client Latency** | India Client $\to$ Singapore (Asia) | **166 ms** | Baseline lowest-latency path |
| **Cross-Ocean Latency** | India Client $\to$ N. Virginia (US) | **504 ms** | **3.0x slower** without geo-cache |
| **Cross-Ocean Latency** | India Client $\to$ Ireland (Europe) | **522 ms** | **3.1x slower** without geo-cache |
| **Convergence Speed** | US write $\to$ Asia readable (10 runs) | **924 ms – 1413 ms** (Avg: 1120 ms) | Eventual consistency in ~1.1s |
| **Replication Accuracy** | 100 concurrent LWW & PN operations | **100% Agreement** | Zero lost updates |

---

## 🛡️ Critical Bug Fix: 5,000-Delta Queue Cap
During partition testing, an unbounded memory leak was discovered: failed peer sync calls re-buffered deltas indefinitely. Over a 15-minute network partition, the queue exceeded 45,000 items, triggering Linux kernel Out-Of-Memory (OOM) kills.

**The Fix in [`worker/app.py`](geo-cache/worker/app.py):**
```python
MAX_BUFFER_SIZE = 5000

with buffer_lock:
    pending_deltas.extend(batch)
    if len(pending_deltas) > MAX_BUFFER_SIZE:
        overflow = len(pending_deltas) - MAX_BUFFER_SIZE
        del pending_deltas[:overflow]  # Protects container from OOM crashes
```

---

## 📖 REST API Cheat Sheet

| Endpoint | Method | Example Payload | Architectural Role |
| :--- | :--- | :--- | :--- |
| `/set` | `POST` | `{"key":"k", "value":"v"}` | Writes LWW key; ticks local HLC; enqueues delta |
| `/get/<key>` | `GET` | _None_ | Returns `{key, value, ts: [ms, counter, node], region}` |
| `/incr` | `POST` | `{"key":"k", "amount":1}` | Increments PN-Counter local vector; enqueues delta |
| `/counter/<key>` | `GET` | _None_ | Computes net value: $\sum P - \sum N$ across all nodes |
| `/sync` | `POST` | `{"deltas": [...]}` | Peer sync endpoint: folds HLC and merges CRDT |
| `/health` | `GET` | _None_ | Returns `{status: "up", region: "...", peers: [...]}` |

---

## 📁 Repository Layout
```
ACC-Miniproject/
├── Geo_Distributed_Cache_Cookbook.pdf    # Full 16-page developer cookbook PDF
├── COOKBOOK_EXCEL_READY.md              # Tabular documentation for Excel
├── README.md                            # Complete developer cookbook & guide
└── geo-cache/
    ├── docker-compose.yml               # Local 6-container cluster definition
    ├── docker-compose.aws.yml           # AWS single-node production compose file
    ├── .env.us / .env.eu / .env.asia    # Per-region configuration definitions
    ├── 01-lww-demo.ps1                  # Concurrent conflicting writes test suite
    ├── 02-pn-counter-demo.ps1           # Distributed counter increment test suite
    ├── 03-worker-outage-recovery.ps1    # Regional outage & partition recovery suite
    └── worker/
        ├── app.py                       # Flask HTTP API & write-behind sync engine
        ├── crdt.py                      # LWW-Register & PN-Counter CRDT logic
        ├── hlc.py                       # Hybrid Logical Clock timestamp generator
        ├── Dockerfile                   # Worker container image definition
        └── requirements.txt             # Python dependencies (flask, redis, requests)
```
