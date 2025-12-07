# 🏗️ TASK-007: Infrastructure & DevOps Hardening
## ArgoCD GitOps + Advanced CI/CD + Cost Optimization

**Дата:** 7 декабря 2025, 18:15 MSK  
**статус:** 🔵 READY FOR ASSIGNMENT  
**Команда:** INFRA Team  
**Ответственные:** Pavel T. (K8s Lead), Sergey B. (DevOps), Marina G. (SRE)  
**Начало:** 19 декабря 2025, 09:00 MSK  
**Дедлайн:** 22 декабря 2025, 17:00 MSK  
**Приоритет:** 🔴 **CRITICAL**  
**Дни:** 4 дня (Production Hardening)

---

## 🎯 ЦЕЛИ

1. **ArgoCD ГитОпс** - Отбасные K8s deployment
2. **Advanced CI/CD** - Мульти-регионные деплойменты
3. **Cost Optimization** - Сэкономить 30-40% на инфре
4. **HA Setup** - High Availability
5. **Blue-Green Deploy** - Zero-downtime updates

---

## 📋 ПОДЗАДАЧИ

### Подзадача 1: ArgoCD Setup

**Гит репо:
```bash
# 1. Установить ArgoCD
kubectl create namespace argocd
helm repo add argo https://argoproj.github.io/argo-helm
helm install argocd argo/argo-cd -n argocd

# 2. Настроить ссылку на GitHub
kubectl create secret generic github-creds \
  -n argocd \
  --from-literal=url=https://github.com/vik9541/super-brain-digital-twin \
  --from-literal=password=$GITHUB_TOKEN

# 3. Настроить ApplicationSet
kubectl apply -f argocd/applicationset-super-brain.yaml

# 4. Верифицировать
kubectl get applications -n argocd
kubectl get appset -n argocd
```

**Success Criteria:**
- [ ] ArgoCD installed
- [ ] GitHub repository synced
- [ ] Applications auto-deploy
- [ ] Rollback working
- [ ] Sync status healthy

### Подзадача 2: Advanced CI/CD

**Новые феачеры:
- [ ] Multi-stage builds (build, test, push)
- [ ] Security scanning (Trivy)
- [ ] SAST scanning (Semgrep)
- [ ] Automated versioning (semantic-release)
- [ ] Slack/Discord notifications
- [ ] Multi-region deployment
- [ ] Canary deploys (10% → 50% → 100%)

**GitHub Actions workflow:
```yaml
name: Advanced CI/CD
on: [push]
jobs:
  build:
    - Docker build
    - Trivy scan
    - Push to registry
  test:
    - Unit tests
    - Integration tests
    - Load tests
  deploy:
    - ArgoCD sync
    - Canary deploy (10%)
    - Monitor metrics
    - Progressive rollout
  notify:
    - Slack message
```

### Подзадача 3: Cost Optimization

**Меры:

1. **Отключите unused ресурсы**
   - [ ] Остановите old staging clusters
   - [ ] Удалите orphaned volumes
   - [ ] Удалите extra IP addresses
   - **Экономия:** $500-1000/месяц

2. **Right-sizing pods**
   - [ ] Анализ CPU/Memory usage
   - [ ] Уменьшение requests (если возможно)
   - [ ] Используйте Spot instances (30% дешевле)
   - **Экономия:** $200-300/месяц

3. **Reserved capacity**
   - [ ] Upgrade на 1-year commitment
   - [ ] Mix on-demand + reserved
   - **Экономия:** $150-200/месяц

4. **Storage optimization**
   - [ ] Удалите old backups
   - [ ] Используйте S3 Glacier
   - [ ] Сжатие логов
   - **Экономия:** $50-100/месяц

**Total potential savings: $900-1600/месяц (30-40%)**

### Подзадача 4: High Availability

**Многореплика K8s:
```bash
# Много-означные deploy
kubectl set replicas deployment/api --replicas=3 -n production
kubectl set replicas deployment/bot --replicas=2 -n production

# Pod Disruption Budget
kubectl apply -f k8s/pdb-api.yaml
kubectl apply -f k8s/pdb-bot.yaml

# Network Policies
kubectl apply -f k8s/network-policy.yaml
```

**Success Criteria:**
- [ ] 3+ API replicas
- [ ] 2+ Bot replicas
- [ ] PDB configured
- [ ] Network policies active
- [ ] No single point of failure

### Подзадача 5: Blue-Green Deployment

**Новая феачер:
- [ ] Deploy v2 в отдельную deployment
- [ ] Test v2 полностью
- [ ] Switch traffic (Blue → Green)
- [ ] Monitor (5 min)
- [ ] Rollback if needed

**Zero-downtime update flow:**
```
Blue (v1.0) ✅ [100% traffic]
    ⬇
 Blue (v1.0) [50%] + Green (v2.0) [50%] [Testing]
    ⬇
Green (v2.0) ✅ [100% traffic]
```

---

## 🧪 CHECKLIST

### День 1 (19 Dec): ArgoCD & CI/CD
- [ ] ArgoCD установлен
- [ ] GitHub integration working
- [ ] Existing apps migrated to ArgoCD
- [ ] Auto-sync enabled
- [ ] Rollback tested

### День 2 (20 Dec): Advanced CI/CD
- [ ] Multi-stage builds working
- [ ] Security scans running
- [ ] Automated versioning
- [ ] Slack notifications working
- [ ] Canary deployment tested

### День 3 (21 Dec): Cost Optimization
- [ ] Unused resources identified
- [ ] Right-sizing analysis completed
- [ ] Spot instances configured
- [ ] Reserved capacity purchased
- [ ] Cost reduction validated

### День 4 (22 Dec): HA & Blue-Green
- [ ] Multi-replica setup live
- [ ] PDB configured
- [ ] Network policies active
- [ ] Blue-green deployment tested
- [ ] Zero-downtime deployment verified

---

## 📄 REPORTING

**File:** `TASKS/TASK-007-INFRA-DEVOPS-HARDENING-COMPLETED.md`

**Include:**
- ArgoCD status (apps, health)
- CI/CD pipeline metrics
- Cost savings achieved
- Uptime improvement
- HA configuration
- Zero-downtime deployment results
- Recommendations

---

## 🔗 RESOURCES

- ArgoCD docs: https://argo-cd.readthedocs.io
- K8s HA: https://kubernetes.io/docs/setup/production-environment/
- Cost optimization: https://www.digitalocean.com/community/tutorials

---

**Status:** 🔵 READY FOR ASSIGNMENT  
**Team:** INFRA (Pavel T., Sergey B., Marina G.)  
**Duration:** 4 days  
**Critical:** Yes  

**Next:** TASK-008 (Security hardening)