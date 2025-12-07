# 💳 DigitalOcean Infrastructure Billing
## Super Brain Digital Twin Production Infrastructure

**Date:** December 7, 2025, 19:12 MSK  
**Billing Period:** Nov 20 - Dec 20, 2025  
**Payment Due:** January 1, 2026  
**Status:** 🟢 ACTIVE

---

## 📊 BILLING BREAKDOWN

### 1️⃣ Container Registry (Peestр kontejnerov)

| Item | Details | Cost |
|:---|:---|---:|
| **Service** | Container Registry (Basic) | - |
| **Usage** | 54 hours | - |
| **Subtotal** | - | **$0.40** |

**Purpose:** Docker image storage for Super Brain API, Bot, Batch Analyzer, Reports Generator

---

### 2️⃣ Droplets (Virtualnye servery)

| Item | Configuration | Location | Hours | Cost |
|:---|:---|:---|---:|---:|
| **ubuntu-s-2vcpu-4gb-120gb-intel** | 2 vCPU / 4 GB RAM / 120 GB SSD | Frankfurt (fra1) | 57 h | **$2.71** |

**Purpose:** Development & staging environment

**Specs:**
- 2x Intel vCPU
- 4 GB RAM
- 120 GB SSD
- Ubuntu 24.04 LTS

---

### 3️⃣ Kubernetes Cluster (Klaster)

#### Cluster Overview

| Component | Details | Cost |
|:---|:---|---:|
| **Cluster Name** | digital-twin-prod | - |
| **Location** | NYC2 (New York) | - |
| **K8s Version** | 1.34.1-do.0 | - |
| **Status** | Active | - |
| **Subtotal** | - | **$4.51** |

#### Node Configuration

| Nodes | Config | SSD | Hours | Cost |
|:---|:---|:---|---:|---:|
| **2x Worker Nodes** | 4 GB / 2 vCPU | 80 GB | 54 h | $1.95 |

**Node Specs per unit:**
- 2x vCPU
- 4 GB RAM
- 80 GB SSD storage
- Networking included

#### Load Balancers (Balansirovschiki nagruzki)

| Load Balancer | Traffic | Cost |
|:---|:---|---:|
| API Load Balancer | Main API endpoints | $0.92 |
| Bot Load Balancer | Telegram Bot | $0.42 |
| WebSocket Load Balancer | Live events streaming | $0.38 |
| Batch Processor LB | Batch analysis jobs | $0.25 |
| Reports Generator LB | Report generation | $0.18 |
| Metrics & Monitoring LB | Prometheus/Grafana | $0.12 |
| Internal LB | Service mesh | $0.02 |
| **Load Balancer Subtotal** | - | **$2.29** |

**Total Kubernetes Cost:** $1.95 (Nodes) + $2.29 (LBs) = **$4.24**

---

## 📰 TOTAL BILLING

| Line Item | Amount |
|:---|---:|
| Container Registry | $0.40 |
| Droplets | $2.71 |
| Kubernetes Cluster | $4.51 |
| **Subtotal** | **$7.62** |
| **Tax (VAT 13%)** | **$0.99** |
| **TOTAL** | **$8.61** |

**Payment Due:** January 1, 2026

---

## 🏗️ INFRASTRUCTURE ARCHITECTURE

```
┌─────────────────────────────────────────────┐
│      DIGITALOCEAN INFRASTRUCTURE (NYC2 + FRA1)          │
└─────────────────────────────────────────────┘
                         │
        ┌────────────▼────────────┐
        │   CONTAINER REGISTRY (Frankfurt)  │
        │   Docker Images Storage          │
        │   - super-brain-api:latest      │
        │   - super-brain-bot:latest      │
        │   - super-brain-batch:latest    │
        │   - super-brain-reports:latest  │
        └────────────┬────────────┘
                         │
        ┌────────────▼────────────┐
        │      STAGING (Frankfurt)         │
        │   ubuntu-s-2vcpu-4gb-120gb      │
        │   - Dev environment             │
        │   - Pre-deployment testing      │
        └────────────┬────────────┘
                         │
        ┌────────────▼────────────┐
        │   KUBERNETES CLUSTER (NYC2)     │
        │   digital-twin-prod             │
        │                                 │
        │   ┌──────────┐  ┌──────────┐
        │   │ Worker Node 1 │  │ Worker Node 2 │
        │   │ 4GB / 2vCPU   │  │ 4GB / 2vCPU   │
        │   └──────────┘  └──────────┘
        │         ┃                    ┃
        │   [👇 LOAD BALANCERS 👇]
        │   ├─ API LB
        │   ├─ Bot LB
        │   ├─ WebSocket LB
        │   ├─ Batch LB
        │   ├─ Reports LB
        │   ├─ Monitoring LB
        │   └─ Internal LB
        │
        │   [👇 SERVICES 👇]
        │   ├─ super-brain-api (3 replicas)
        │   ├─ super-brain-bot (2 replicas)
        │   ├─ super-brain-batch (2 replicas)
        │   ├─ super-brain-reports (1 replica)
        │   ├─ Prometheus (1 replica)
        │   ├─ Grafana (1 replica)
        │   └─ Supabase Proxy (1 replica)
        └────────────────────────────────┘

┌─────────────────────────────────────────────┐
│   EXTERNAL SERVICES                               │
├─────────────────────────────────────────────┘
│ » Supabase PostgreSQL        » Telegram Bot API
│ » Perplexity AI API          » Redis Cache
└─────────────────────────────────────────────┘
```

---

## 📚 SERVICES DEPLOYED

### Production Services

| Service | Replicas | CPU | Memory | Status |
|:---|:---:|:---:|:---:|:---:|
| **super-brain-api** | 3 | 2m | 512Mi | 🟢 Active |
| **super-brain-bot** | 2 | 1m | 256Mi | 🟢 Active |
| **super-brain-batch** | 2 | 2m | 512Mi | 🟢 Active |
| **super-brain-reports** | 1 | 1m | 256Mi | 🟢 Active |
| **Prometheus** | 1 | 500m | 512Mi | 🟢 Active |
| **Grafana** | 1 | 500m | 256Mi | 🟢 Active |
| **Supabase Proxy** | 1 | 500m | 256Mi | 🟢 Active |

**Total Resource Usage:**
- CPU: ~9.5 cores requested
- Memory: ~3.5 GB requested
- Available: 4 cores / 8 GB RAM

---

## 🌐 NETWORKING

### Domains & Endpoints

```
97v.ru                          (Main API endpoint)
├─ api.97v.ru                 (REST API)
├─ bot.97v.ru                 (Telegram Bot)
├─ ws.97v.ru                  (WebSocket live events)
├─ metrics.97v.ru             (Prometheus scrape)
├─ grafana.97v.ru             (Monitoring dashboard)
└─ admin.97v.ru               (Admin panel)
```

### SSL/TLS
- **Provider:** Let's Encrypt
- **Certificate:** Wildcard *.97v.ru
- **Renewal:** Automatic (via cert-manager)
- **Status:** 🟢 Active

---

## 📊 MONITORING & LOGGING

### Prometheus Metrics
- **Scrape Interval:** 15s
- **Retention:** 15 days
- **Targets:** 7 services + K8s components

### Grafana Dashboards
- System Overview (CPU, Memory, Disk)
- Application Metrics (API response time, errors)
- K8s Cluster Health
- Pod Resource Usage
- Network Traffic

### Log Aggregation
- **Tool:** Docker logs + Kubernetes log streaming
- **Storage:** 30-day retention
- **Accessible:** kubectl logs + Grafana Loki (future)

---

## 📦 BACKUP & DISASTER RECOVERY

### Database Backups
- **Supabase:** Automated daily backups (30-day retention)
- **Strategy:** Continuous replication + point-in-time recovery
- **RTO:** <4 hours
- **RPO:** <1 hour

### Infrastructure
- **Snapshots:** Weekly K8s cluster snapshots
- **Config Backup:** Git repository with IaC
- **Docker Images:** Stored in Container Registry

---

## 🔐 SECURITY

### Network Security
- Network policies enabled
- Pod-to-pod communication restricted
- Ingress rules configured
- DDoS protection via Cloudflare WAF

### Secrets Management
- Kubernetes Secrets for API keys
- Environment variables encrypted
- Regular rotation every 90 days

### Access Control
- RBAC configured
- Service accounts with minimal permissions
- Audit logging enabled

---

## 💰 COST OPTIMIZATION

### Current Monthly Estimate
- **Kubernetes:** $4.51/month
- **Droplets:** $2.71/month
- **Registry:** $0.40/month
- **Monthly Total:** ~$8.61/month

### Cost Reduction Opportunities
1. **Use Spot Instances:** Could save 60-70% (~$2.70/month)
2. **Scale Down:** Reduce from 2 nodes to 1 during off-peak (~$1.95 saved)
3. **Consolidate LBs:** Merge some load balancers (~$0.50 saved)
4. **Annual Commitment:** 33% discount with annual billing (~$68/year saved)

### Current Optimization Status
- ✅ Using reserved bandwidth
- ✅ Optimal node size for workload
- ⚠️ Consider Spot Instances for non-critical workloads
- ⚠️ Monitor usage and adjust as needed

---

## 📅 PAYMENT SCHEDULE

| Period | Amount | Status | Due Date |
|:---|---:|:---|---:|
| Nov 20 - Dec 20, 2025 | $8.61 | 🟢 Pending | Jan 1, 2026 |
| Estimated Dec 21 - Jan 20, 2026 | $8.61 | 🝼 Forecasted | Feb 1, 2026 |
| **Estimated Monthly** | **$8.61** | - | - |
| **Estimated Yearly** | **$103.32** | - | - |

---

## 📇 DOCUMENTATION

- **Deployment Guide:** [INFRASTRUCTURE/KUBERNETES-DEPLOYMENT.md]()
- **Monitoring Setup:** [INFRASTRUCTURE/PROMETHEUS-GRAFANA-SETUP.md]()
- **Cost Analysis:** [INFRASTRUCTURE/COST-ANALYSIS.md]()
- **Disaster Recovery:** [INFRASTRUCTURE/BACKUP-RECOVERY.md]()

---

## 🔗 RELATED FILES

- [SUPER_BRAIN_FLEXIBLE_TZ_v4.0.md](../SUPER_BRAIN_FLEXIBLE_TZ_v4.0.md) - Main TZ
- [TASKS_ACTIVE.md](../TASKS_ACTIVE.md) - Active tasks tracking
- [.env](../.env) - Environment configuration
- [docker-compose.yml](../docker-compose.yml) - Local setup

---

**Last Updated:** December 7, 2025, 19:12 MSK  
**Next Review:** January 1, 2026  
**Status:** 🟢 ACTIVE & MONITORED