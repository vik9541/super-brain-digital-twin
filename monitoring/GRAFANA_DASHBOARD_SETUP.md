# Grafana Dashboard Setup Guide - TEAM-4

## Обзор

Этот документ описывает процесс создания и настройки профессионального Grafana dashboard для мониторинга Super Brain Digital Twin системы.

**Dashboard Name**: SUPER BRAIN v4.0  
**Estimated Time**: 4 hours  
**Priority**: HIGH  

---

## Предварительные требования

- Grafana установлен в Kubernetes кластере
- Prometheus собирает метрики
- kubectl настроен для работы с кластером
- Доступ к Grafana UI (через port-forward)

---

## 1. Доступ к Grafana

### Port Forward для локального доступа

```bash
# Port forward к Grafana сервису
kubectl port-forward svc/prometheus-grafana -n monitoring 3000:80

# Открыть в браузере
# http://localhost:3000

# Логин credentials (по умолчанию)
# Username: admin
# Password: prom-operator
```

### Проверка подключения

1. Открыть http://localhost:3000
2. Войти с учетными данными
3. Проверить что Grafana загрузился корректно

---

## 2. Dashboard Setup (1 час)

### Шаг 1: Создать новый Dashboard

1. **Навигация**: Dashboards → New → New Dashboard
2. **Settings** (иконка шестеренки):
   - **Name**: `SUPER BRAIN v4.0`
   - **Description**: `Production monitoring dashboard for Super Brain Digital Twin system`
   - **Tags**: `production`, `super-brain`, `monitoring`
   - **Timezone**: `Browser Time`
   - **Refresh**: `5s` (каждые 5 секунд)

### Шаг 2: Подключить Data Source

1. Перейти в **Configuration → Data Sources**
2. Выбрать **Prometheus**
3. Проверить URL: `http://prometheus-kube-prometheus-prometheus.monitoring:9090`
4. Test & Save

### Шаг 3: Настроить Variables (опционально)

Variables позволяют фильтровать данные динамически:

```
Name: namespace
Type: Query
Query: label_values(up, namespace)
```

---

## 3. System Metrics Panels (1 час)

### Panel 1: API Uptime
**Type**: Stat  
**Query**: 
```promql
up{job="digital-twin-api"}
```
**Thresholds**:
- Green: 1
- Red: 0

**Display**: 
- Unit: `none`
- Text: `UP` / `DOWN`
- Color: Green/Red based on value

---

### Panel 2: Requests Per Second
**Type**: Graph / Time Series  
**Query**:
```promql
rate(http_requests_total{job="digital-twin-api"}[5m])
```
**Display**:
- Unit: `requests/sec (reqps)`
- Line width: 2
- Fill opacity: 20%

---

### Panel 3: Error Rate
**Type**: Gauge  
**Query**:
```promql
(rate(http_requests_total{job="digital-twin-api",status=~"5.."}[5m]) / rate(http_requests_total{job="digital-twin-api"}[5m])) * 100
```
**Thresholds**:
- Green: 0-0.5%
- Yellow: 0.5-1%
- Red: >1%

**Display**:
- Unit: `percent (0-100)`
- Max: 100
- Min: 0

---

### Panel 4: Response Time (P95)
**Type**: Stat  
**Query**:
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="digital-twin-api"}[5m])) * 1000
```
**Thresholds**:
- Green: 0-200ms
- Yellow: 200-500ms
- Red: >500ms

**Display**:
- Unit: `milliseconds (ms)`

---

### Panel 5: Active Connections
**Type**: Stat  
**Query**:
```promql
sum(http_connections_active{job="digital-twin-api"})
```
**Display**:
- Unit: `none`
- Color: Blue

---

### Panel 6: Pod Restart Count
**Type**: Stat  
**Query**:
```promql
sum(kube_pod_container_status_restarts_total{namespace="production", pod=~"digital-twin-api.*"})
```
**Thresholds**:
- Green: 0
- Red: >0

**Display**:
- Unit: `none`
- Text: Show restart count

---

## 4. Application Metrics Panels (1 час)

### Panel 7: Healthy Endpoints
**Type**: Stat  
**Query**:
```promql
count(up{job="digital-twin-api"} == 1)
```
**Display**:
- Format: `X/7` (7 total endpoints)
- Color: Green if all healthy

---

### Panel 8: Supabase Query Performance
**Type**: Graph  
**Query**:
```promql
rate(supabase_query_duration_seconds_sum{job="digital-twin-api"}[5m]) / rate(supabase_query_duration_seconds_count{job="digital-twin-api"}[5m]) * 1000
```
**Display**:
- Unit: `milliseconds (ms)`
- Line chart

---

### Panel 9: Telegram Bot Messages
**Type**: Stat  
**Query**:
```promql
increase(telegram_messages_total{job="digital-twin-bot"}[24h])
```
**Display**:
- Unit: `messages/day`
- Color: Blue

---

### Panel 10: N8N Workflow Success Rate
**Type**: Gauge  
**Query**:
```promql
(sum(n8n_workflow_success_total) / sum(n8n_workflow_total)) * 100
```
**Thresholds**:
- Red: <90%
- Yellow: 90-95%
- Green: >95%

**Display**:
- Unit: `percent (0-100)`

---

### Panel 11: File Upload Volume
**Type**: Graph  
**Query**:
```promql
rate(file_upload_bytes_total{job="digital-twin-api"}[1h]) / 1024 / 1024
```
**Display**:
- Unit: `megabytes (MB)`
- Aggregation: Sum over time

---

### Panel 12: Analysis Completion Rate
**Type**: Gauge  
**Query**:
```promql
(sum(analysis_completed_total) / sum(analysis_started_total)) * 100
```
**Thresholds**:
- Red: <70%
- Yellow: 70-85%
- Green: >85%

**Display**:
- Unit: `percent (0-100)`

---

## 5. Alerts Configuration (0.5 часа)

### Alert Rule 1: High Error Rate
**Condition**: Error rate > 1%  
**Expression**:
```promql
(rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])) * 100 > 1
```
**Severity**: Critical  
**Notification**: Telegram

---

### Alert Rule 2: Slow Response Time
**Condition**: P95 latency > 500ms  
**Expression**:
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) * 1000 > 500
```
**Severity**: Warning  
**Notification**: Telegram

---

### Alert Rule 3: Pod Restarts Detected
**Condition**: Pod restarts > 0  
**Expression**:
```promql
increase(kube_pod_container_status_restarts_total{namespace="production"}[5m]) > 0
```
**Severity**: Critical  
**Notification**: Telegram

---

### Alert Rule 4: Low Uptime
**Condition**: Uptime < 95%  
**Expression**:
```promql
avg_over_time(up{job="digital-twin-api"}[5m]) < 0.95
```
**Severity**: Critical  
**Notification**: Telegram

---

### Telegram Alert Notification Setup

1. **Перейти**: Alerting → Notification channels
2. **Создать новый канал**:
   - **Type**: Telegram
   - **Name**: `Super Brain Alerts`
   - **Bot Token**: `<TELEGRAM_BOT_TOKEN>` (из secrets)
   - **Chat ID**: `<TELEGRAM_CHAT_ID>` (из secrets)
3. **Test**: Отправить тестовое уведомление
4. **Save**

---

## 6. Dashboard Styling & Layout (0.5 часа)

### Layout Рекомендации

**Row 1: System Health (Top)**
- Panel 1 (Uptime) - 20% width
- Panel 3 (Error Rate) - 20% width  
- Panel 4 (Response Time) - 20% width
- Panel 5 (Active Connections) - 20% width
- Panel 6 (Pod Restarts) - 20% width

**Row 2: Traffic**
- Panel 2 (Requests/sec) - Full width

**Row 3: Application Metrics**
- Panel 7 (Endpoints) - 25% width
- Panel 8 (DB Query) - 25% width
- Panel 9 (Bot Messages) - 25% width
- Panel 10 (Workflow Success) - 25% width

**Row 4: Storage & Analysis**
- Panel 11 (Upload Volume) - 50% width
- Panel 12 (Analysis Rate) - 50% width

### Theme Settings

- **Theme**: Dark (recommended for production monitoring)
- **Time picker**: Show last 6 hours by default
- **Auto-refresh**: 5 seconds

### Folder Organization

1. Создать папку: **Production Monitoring**
2. Переместить dashboard в эту папку
3. Установить права: **Admin editing only**

---

## 7. Export & Backup

### Экспорт Dashboard JSON

1. Dashboard Settings → JSON Model
2. Copy JSON
3. Сохранить в `monitoring/grafana-dashboard.json`
4. Commit в Git

### Импорт Dashboard

```bash
# Импорт через UI
Dashboard → Import → Upload JSON file

# Или через API
curl -X POST -H "Content-Type: application/json" \
  -d @monitoring/grafana-dashboard.json \
  http://admin:prom-operator@localhost:3000/api/dashboards/db
```

---

## 8. Проверка и Тестирование

### Чек-лист перед production

- [ ] Все 12 панелей отображают данные
- [ ] Все метрики обновляются в real-time (5s refresh)
- [ ] Цвета thresholds настроены правильно
- [ ] Все 4 alert rules созданы
- [ ] Telegram уведомления работают
- [ ] Dashboard сохранён и backed up в JSON
- [ ] Documentation complete
- [ ] Dashboard accessible по ссылке

### Тестирование Alerts

```bash
# Симулировать высокую нагрузку для теста
kubectl run load-test --image=busybox --restart=Never -- \
  sh -c "while true; do wget -q -O- http://digital-twin-api:8000/health; done"

# Проверить что alert сработал через 1-2 минуты
```

---

## 9. Troubleshooting

### Проблема: Metrics не отображаются

**Решение**:
1. Проверить что Prometheus собирает метрики:
```bash
kubectl port-forward svc/prometheus-kube-prometheus-prometheus -n monitoring 9090:9090
# Открыть http://localhost:9090
# Проверить Targets → All targets are UP
```

2. Проверить ServiceMonitor:
```bash
kubectl get servicemonitor -n production
```

### Проблема: Alerts не отправляются

**Решение**:
1. Проверить AlertManager:
```bash
kubectl logs -n monitoring alertmanager-prometheus-kube-prometheus-alertmanager-0
```

2. Проверить Telegram bot token:
```bash
kubectl get secret api-credentials -n production -o yaml
```

---

## 10. Maintenance

### Регулярные задачи

**Еженедельно**:
- Проверить что все метрики актуальны
- Проверить что alerts срабатывают корректно
- Обновить thresholds если нужно

**Ежемесячно**:
- Review panel layout и optimization
- Backup dashboard JSON в Git
- Update documentation если были изменения

---

## Полезные ссылки

- **Grafana Documentation**: https://grafana.com/docs/grafana/latest/
- **Prometheus Query Language**: https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Best Practices**: https://grafana.com/docs/grafana/latest/best-practices/

---

## Контакты

При проблемах с dashboard:
- **Email**: 9541@bk.ru
- **GitHub**: @vik9541
- **Issue Tracker**: https://github.com/vik9541/super-brain-digital-twin/issues

---

**Дата создания**: 8 декабря 2025  
**Версия**: 1.0  
**Автор**: vik9541  
**Task**: TEAM-4 - Issue #15
