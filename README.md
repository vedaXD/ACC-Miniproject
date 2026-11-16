# Geo-Distributed Active-Active Cache Cluster
### Architectural Blueprint & Engineering Cookbook
[![YouTube Demo](https://img.shields.io/badge/YouTube-Demo%20Video-red?logo=youtube)](https://youtu.be/OwtLWvFsUC4)
[![Docker](https://img.shields.io/badge/Docker-Compose%20v2-blue?logo=docker)](https://www.docker.com/)
[![AWS EC2](https://img.shields.io/badge/AWS-3%20Regions%20(EC2)-orange?logo=amazon-aws)](https://aws.amazon.com/ec2/)
[![Redis](https://img.shields.io/badge/Redis-7.0%20Alpine-red?logo=redis)](https://redis.io/)
[![Python](https://img.shields.io/badge/Python-3.11%20Flask-yellow?logo=python)](https://python.org/)
[![SDG 9](https://img.shields.io/badge/UN%20SDG-9%20Industry%2C%20Innovation-orange)](https://sdgs.un.org/goals/goal9)

> **Repository:** [https://github.com/vedaXD/ACC-Miniproject](https://github.com/vedaXD/ACC-Miniproject)  
> **Live Video Demonstration:** [https://youtu.be/OwtLWvFsUC4](https://youtu.be/OwtLWvFsUC4)  
> **Course:** Advanced Cloud Computing (ACC) • Sem 7, 2026 • Group 6  
> **Institute:** Vivekanand Education Society's Institute of Technology (VESIT), Mumbai  
> **Mentor:** Prof. Richard Joseph  
> **Team:** Veda Patki (43), Akul Patre (44), Isha Palkar (37), Soham Patil (40)  

---

## 📖 Executive Summary
Conventional caching systems rely on a single primary cluster in one geographic region. A client in Asia querying a primary in North America incurs an unavoidable **400ms – 550ms round-trip latency penalty** on every request. Furthermore, if the transatlantic connection or the central region fails, write availability is completely lost.

This project designs, containerizes, and deploys an **Active-Active (Multi-Master) Geo-Distributed Cache Cluster** across three continents (**US**, **Europe**, and **Asia**). Every region accepts reads and writes locally with sub-millisecond response times. Writes are stamped using **Hybrid Logical Clocks (HLC)** and reconciled asynchronously using **Conflict-Free Replicated Data Types (CRDTs)**:
- **LWW-Register (Last-Write-Wins):** Deterministically resolves concurrent key-value conflicts without distributed locks.
- **PN-Counter (Positive-Negative Counter):** Merges concurrent multi-region increments/decrements additively with zero lost updates.
- **Asynchronous Write-Behind Engine:** Buffers updates locally and dispatches delta batches every 500ms, protected by a 5,000-delta queue cap to prevent out-of-memory (OOM) failures during network partitions.

---

## 🏗️ Architecture & Component Roles

| Component | Technology | Architectural Role in Cluster |
| :--- | :--- | :--- |
| **In-Memory Cache** | Redis 7 (Alpine) | Sub-millisecond region-local data store for keys and counters |
| **Replication Gateway** | Python 3.11 + Flask | Client HTTP API (`/set`, `/get`, `/incr`, `/counter`) and peer `/sync` engine |
| **Causal Clock** | Hybrid Logical Clock (HLC) | Generates monotonic `(physical_ms, logical_counter, node_id)` timestamps |
| **Key-Value CRDT** | LWW-Register | Deterministic conflict resolution; highest HLC timestamp wins |
| **Counter CRDT** | State-Based PN-Counter | Commutative and idempotent per-node maxima vector merging |
| **Replication Strategy** | Asynchronous Write-Behind | Immediate local commit + 500ms background thread push (capped at 5,000 deltas) |
| **Cloud Deployment** | AWS EC2 (3 Regions) | `us-east-1` (US), `eu-west-1` (Europe), and `ap-southeast-1` (Asia) |
| **Local Emulation** | Docker Compose v2 | 6-container bridge cluster mapped to ports `5001`, `5002`, and `5003` |

---

## 🌐 Geo-Distributed Replication Pipeline

```
  [Client in US]                     [Client in Europe]                  [Client in Asia]
        | (POST /set)                        | (POST /set)                       | (POST /incr)
        v                                    v                                   v
+-----------------------+            +-----------------------+           +-----------------------+
| AWS US: us-east-1     |            | AWS Europe: eu-west-1 |           | AWS Asia: ap-se-1     |
| EC2: 54.242.141.54    |            | EC2: 34.241.36.71     |           | EC2: 52.77.218.56     |
|                       |            |                       |           |                       |
|  +-----------------+  |            |  +-----------------+  |           |  +-----------------+  |
|  |  Flask Worker   |  |            |  |  Flask Worker   |  |           |  |  Flask Worker   |  |
|  |  (app.py :5000) |  |            |  |  (app.py :5000) |  |           |  |  (app.py :5000) |  |
|  +--------+--------+  |            +--------+--------+  |           +--------+--------+  |
|           |           |                     |           |                    |           |
|    (1) Tick HLC       |              (1) Tick HLC       |             (1) Tick HLC       |
|    (2) Local Redis SET|              (2) Local Redis SET|             (2) Local Redis SET|
|    (3) Buffer Delta   |              (3) Buffer Delta   |             (3) Buffer Delta   |
|           |           |                     |           |                    |           |
|  +--------v--------+  |            |  +--------v--------+  |           |  +--------v--------+  |
|  | Redis 7 Storage |  |            |  | Redis 7 Storage |  |           |  | Redis 7 Storage |  |
|  +-----------------+  |            |  +-----------------+  |           |  +-----------------+  |
|           |           |                     |           |                    |           |
|   [Write-Behind Buf]  |            |   [Write-Behind Buf]  |           |   [Write-Behind Buf]  |
|   (max 5000 deltas)   |            |   (max 5000 deltas)   |           |   (max 5000 deltas)   |
+-----------+-----------+            +-----------+-----------+           +-----------+-----------+
            |                                    |                                   |
            |======= HTTP POST /sync (500ms) ====+= ===== HTTP POST /sync (500ms) ===|
            +------------------------------------+-----------------------------------+
                                    Inter-Region Network Mesh
```

---

## 🚀 Quick Start: Running the Cluster

### Option 1: Run Locally via Docker Compose (Zero Cloud Setup)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vedaXD/ACC-Miniproject.git
   cd ACC-Miniproject/geo-cache
   ```

2. **Start the 6-container cluster (3 Redis instances + 3 Flask workers):**
   ```bash
   docker compose up --build -d
   ```

3. **Verify running containers:**
   ```bash
   docker compose ps
   ```
   - **US Worker:** `http://localhost:5001`
   - **Europe Worker:** `http://localhost:5002`
   - **Asia Worker:** `http://localhost:5003`

4. **Check node health:**
   ```powershell
   curl.exe http://localhost:5001/health
   curl.exe http://localhost:5002/health
   curl.exe http://localhost:5003/health
   ```

---

### Option 2: Deploy on AWS EC2 (True Multi-Region Cloud)

The production cluster runs across three AWS regions:
- **US Node (`us-east-1`):** `54.242.141.54`
- **Europe Node (`eu-west-1`):** `34.241.36.71`
- **Asia Node (`ap-southeast-1`):** `52.77.218.56`

#### Deployment steps for each EC2 instance (`t3.small`, Ubuntu 24.04):
```bash
# 1. SSH into the instance
ssh -i geo-key.pem ubuntu@<INSTANCE_PUBLIC_IP>

# 2. Install Docker
curl -fsSL https://get.docker.com | sudo sh

# 3. Clone and navigate to project
git clone https://github.com/vedaXD/ACC-Miniproject.git
cd ACC-Miniproject/geo-cache

# 4. Set region environment file (e.g. for US node)
cp .env.us .env

# 5. Start persistent stack
sudo docker compose -f docker-compose.aws.yml up --build -d

# 6. Verify health
curl http://localhost:5000/health
```

> **Security Group Invariant:** Port `5000` is opened strictly to the Elastic IPs of peer nodes and the administrator IP (`/32`). It is never opened to `0.0.0.0/0`.

---

## 🧪 Verification & Automated Test Suites

Three automated PowerShell test scripts are provided in `geo-cache/` to validate cluster invariants:

### 1. Concurrent Conflicting Writes (LWW-Register)
Simultaneously sends conflicting values for the exact same key: `"active"` to US and `"inactive"` to Europe in parallel background jobs:
```powershell
cd geo-cache
.\01-lww-demo.ps1
```
- **Expected Outcome:** Replicas sync within 1.5s. All 3 nodes return the identical winning value and matching HLC timestamp via deterministic tie-breaking.

### 2. Distributed Concurrent Counter (PN-Counter)
Fires concurrent increments from 3 continents simultaneously: US (+5), Europe (+3), Asia (+2):
```powershell
.\02-pn-counter-demo.ps1
```
- **Expected Outcome:** Zero lost increments. Every region evaluates `sum(P) - sum(N)` and converges to `10`.

### 3. Fault Tolerance & Outage Recovery
Stops a regional worker container via SSH (`docker compose stop worker`), sends live writes to surviving nodes, restarts the stopped worker (`docker compose start worker`), and verifies automatic reconciliation:
```powershell
.\03-worker-outage-recovery.ps1
```
- **Expected Outcome:** Surviving nodes remain 100% available during the outage. The restarted node catches up on queued write-behind deltas within one sync cycle.

---

## 📊 Empirical Benchmarks

| Benchmark Metric | Measurement Scenario | Observed Value | Performance Interpretation |
| :--- | :--- | :--- | :--- |
| **Client Latency (Local)** | India Client $\to$ Singapore (Asia) | **166 ms** | Lowest latency path for South Asian traffic |
| **Client Latency (Cross-Ocean)** | India Client $\to$ N. Virginia (US) | **504 ms** | 3.0x slower without active-active replication |
| **Client Latency (Cross-Ocean)** | India Client $\to$ Dublin (Europe) | **522 ms** | 3.1x slower without active-active replication |
| **Replication Convergence** | US write $\to$ Asia readable (10 runs) | **924 ms – 1413 ms** (Avg: 1120 ms) | Lower bounded by 500ms sync interval + transatlantic RTT |
| **Replication Accuracy** | 100 concurrent LWW & PN operations | **100% Agreement** | Zero lost updates or divergent states |

> **Key Result:** Geo-distributed active-active caching delivers a **67% latency reduction** (166 ms vs 504 ms) for regional clients while maintaining 100% write availability.

---

## 🛡️ Critical Bug Fix: Unbounded Memory Leak
During initial failure testing on 1 GB RAM instances, prolonged network partitions caused `pending_deltas` to accumulate over 45,000 items because failed batches were re-queued indefinitely on every 500ms tick. This triggered Linux kernel Out-Of-Memory (OOM) kills.

**The Fix ([`worker/app.py`](geo-cache/worker/app.py)):**
```python
MAX_BUFFER_SIZE = 5000  # Hard ceiling on pending deltas

# When re-buffering failed sync attempts:
with buffer_lock:
    pending_deltas.extend(batch)
    if len(pending_deltas) > MAX_BUFFER_SIZE:
        overflow = len(pending_deltas) - MAX_BUFFER_SIZE
        del pending_deltas[:overflow]  # Drop oldest deltas to prevent crash
```

---

## 📚 REST API Cheat Sheet

| Endpoint | Method | Payload Example | Functionality |
| :--- | :--- | :--- | :--- |
| `/set` | `POST` | `{"key":"user:100", "value":"active"}` | Writes LWW key; ticks HLC; buffers delta |
| `/get/<key>` | `GET` | _None_ | Returns `{key, value, ts: [ms, counter, node], region}` |
| `/incr` | `POST` | `{"key":"post:likes", "amount":1}` | Increments PN-Counter local vector; buffers delta |
| `/counter/<key>` | `GET` | _None_ | Computes net value: $\sum P - \sum N$ across all nodes |
| `/sync` | `POST` | `{"deltas": [...]}` | Ingests peer batch; updates local clock & merges CRDT |
| `/health` | `GET` | _None_ | Returns `{status: "up", region: "...", peers: [...]}` |

---

## 📁 Repository Structure
```
ACC-Miniproject/
├── Geo_Distributed_Cache_Cookbook.pdf    # Full 16-page publication-grade PDF cookbook
├── COOKBOOK_EXCEL_READY.md              # Tabular documentation structured for Excel
├── README.md                            # Comprehensive project guide and runbook
├── video/
│   └── ACC Miniproject Demo Video.mp4   # Full demonstration video recording
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

---

## 📜 References & Acknowledgements
1. **L. Lamport (1978):** *Time, Clocks, and the Ordering of Events in a Distributed System.*
2. **S. Kulkarni et al. (2014):** *Logical Physical Clocks and Consistent Snapshots in Globally Distributed Databases (HLC).*
3. **M. Shapiro et al. (2011):** *Conflict-Free Replicated Data Types (CRDTs).*
4. **G. DeCandia et al. (2007):** *Dynamo: Amazon's Highly Available Key-value Store.*
5. **UN Sustainable Development Goals:** *Aligned with SDG 9: Industry, Innovation and Infrastructure.*
