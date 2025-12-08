# 🚀 DEPLOYMENT QUICKSTART GUIDE

**Дата:** 8 декабря 2025
**Статус:** ✅ DNS настроен | ⏳ Готов к деплою
**Кластер:** super-brain-prod (NYC2)

---

## 📋 ТЕКУЩИЙ СТАТУС

### ✅ ЗАВЕРШЕНО
1. **DNS конфигурация:**
   - 97v.ru → 138.197.242.93 (Load Balancer IP)
   - 97k.ru → 138.197.242.93 (Load Balancer IP)
   - *.97k.ru → 138.197.242.93 (Load Balancer IP)

2. **Kubernetes кластер:**
   - Имя: super-brain-prod
   - Регион: NYC2 (New York 2)
   - Ноды: 3x (4vCPU, 8GB RAM each)
   - Статус: 3/3 Running
   - Стоимость: $144/month

3. **Установленные компоненты (Marketplace):**
   - ✅ NGINX Ingress Controller
   - ✅ cert-manager (для SSL)
   - ✅ Prometheus + Grafana (мониторинг)
   - ✅ ArgoCD (GitOps)

4. **Namespaces (манифесты созданы):**
   - `super-brain-prod` - для SUPER BRAIN API + Bot
   - `shop-97k-prod` - для интернет-магазина ООО Защита

---

## ⚡ БЫСТРЫЙ СТАРТ - ПОШАГОВАЯ ИНСТРУКЦИЯ

### Шаг 1: Подключение к кластеру

```bash
# Скачать kubeconfig из DigitalOcean Console
# Настроить kubectl
export KUBECONFIG=~/Downloads/super-brain-prod-kubeconfig.yaml

# Проверить подключение
kubectl cluster-info
kubectl get nodes
```

### Шаг 2: Создать namespaces

```bash
# Применить манифест namespace
kubectl apply -f k8s/namespaces.yaml

# Проверить
kubectl get namespaces
```

### Шаг 3: Настроить ClusterIssuer для cert-manager (Let's Encrypt)

```bash
# Создать ClusterIssuer для production SSL сертификатов
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@97v.ru
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

# Проверить статус
kubectl get clusterissuer
```

### Шаг 4: Создать Ingress для 97v.ru (SUPER BRAIN)

```bash
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: super-brain-ingress
  namespace: super-brain-prod
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - 97v.ru
    - www.97v.ru
    - api.97v.ru
    secretName: super-brain-tls
  rules:
  - host: 97v.ru
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: super-brain-api
            port:
              number: 8000
  - host: api.97v.ru
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: super-brain-api
            port:
              number: 8000
EOF
```

### Шаг 5: Создать Ingress для 97k.ru (Интернет-магазин)

```bash
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: shop-97k-ingress
  namespace: shop-97k-prod
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - 97k.ru
    - www.97k.ru
    secretName: shop-97k-tls
  rules:
  - host: 97k.ru
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: shop-frontend
            port:
              number: 80
  - host: www.97k.ru
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: shop-frontend
            port:
              number: 80
EOF
```

### Шаг 6: Проверить SSL сертификаты

```bash
# Проверить статус Certificate
kubectl get certificate -n super-brain-prod
kubectl get certificate -n shop-97k-prod

# Посмотреть детали
kubectl describe certificate super-brain-tls -n super-brain-prod
kubectl describe certificate shop-97k-tls -n shop-97k-prod
```

---

## 🔧 ДАЛЬНЕЙШИЕ ШАГИ

### Приоритет 1: Деплой SUPER BRAIN (97v.ru)
1. Создать Secrets для Supabase credentials
2. Создать Secrets для Perplexity API key
3. Создать Secrets для Telegram Bot token
4. Деплой API Service + Deployment
5. Деплой Bot Service + Deployment  
6. Настроить HPA (Horizontal Pod Autoscaler)

### Приоритет 2: Деплой Магазина (97k.ru)
1. Создать Secrets для e-commerce платформы
2. Деплой frontend + backend
3. Настроить базу данных
4. Настроить систему заказов

### Приоритет 3: Настройка GitOps (ArgoCD)
1. Подключить GitHub репозиторий
2. Создать ArgoCD Applications для каждого namespace
3. Настроить auto-sync

### Приоритет 4: Настройка мониторинга
1. Импортировать Grafana dashboards
2. Настроить Prometheus alerts
3. Настроить AlertManager уведомления

---

## 📊 ПОЛЕЗНЫЕ КОМАНДЫ

```bash
# Проверить состояние Ingress
kubectl get ingress --all-namespaces

# Проверить Load Balancer IP
kubectl get svc -n ingress-nginx

# Логи NGINX Ingress Controller
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx

# Проверить cert-manager
kubectl get pods -n cert-manager
kubectl logs -n cert-manager -l app=cert-manager

# Проверить все ресурсы в namespace
kubectl get all -n super-brain-prod
kubectl get all -n shop-97k-prod
```

---

## 🔗 ВАЖНЫЕ ССЫЛКИ

- **Cluster Dashboard:** https://cloud.digitalocean.com/kubernetes/clusters/3fbf1852-b6c2-437f-b86e-9aefe81d2ec6
- **Load Balancer IP:** 138.197.242.93
- **Reserved IPs:** https://cloud.digitalocean.com/networking/reserved_ips
- **Domains:** https://cloud.digitalocean.com/networking/domains

---

## ⚠️ ВАЖНО

1. **SSL сертификаты:** Let's Encrypt может занять до 5-10 минут для выпуска сертификата
2. **DNS propagation:** Изменения DNS могут занять до 24-48 часов для полного распространения
3. **Rate limits:** Let's Encrypt имеет лимит 50 сертификатов в неделю на домен
4. **Backups:** Убедиться что настроены регулярные backup'ы для всех критичных данных

---

**Следующий шаг:** Приступить к деплою приложений согласно приоритетам выше
