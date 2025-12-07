# 📃 TASK-004: GRAFANA DASHBOARD KPI & MONITORING

**Фаза:** WEEK 1 (пятница, 11 декабря)
**Уровень приоритета:** 🟣 IMPORTANT
**Ответственная команда:** INFRA
**Наследует он:** TASK-002 (Batch Analyzer работает)

---

## цель

Создать **комплексный Grafana Dashboard** с KPI метриками для:
- API производительности
- Bot работы
- Batch анализатора
- K8s нодов
- Ошибок и алертов

---

## что НАДО сделать

### Этап 1: Prometheus метрики добавить (2 часа)

**Файл:** `monitoring/prometheus-custom-metrics.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-additional-scrape-configs
  namespace: monitoring
data:
  additional-scrape-configs.yaml: |
    # API метрики
    - job_name: 'digital-twin-api'
      static_configs:
        - targets: ['digital-twin-api:8000']
      metrics_path: '/metrics'
      scrape_interval: 15s
    
    # Bot метрики
    - job_name: 'telegram-bot'
      static_configs:
        - targets: ['telegram-bot:8080']
      metrics_path: '/metrics'
      scrape_interval: 30s
    
    # Batch Analyzer метрики (Прометей под кронжоб вывод)
    - job_name: 'batch-analyzer'
      static_configs:
        - targets: ['batch-analyzer-metrics:9090']
      scrape_interval: 5m
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-recording-rules
  namespace: monitoring
data:
  recording-rules.yaml: |
    groups:
    - name: digital-twin
      interval: 1m
      rules:
      # API производительность
      - record: api:request_duration:p99
        expr: histogram_quantile(0.99, rate(api_request_duration_seconds_bucket[5m]))
      
      - record: api:request_duration:p95
        expr: histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))
      
      - record: api:error_rate
        expr: rate(api_requests_total{status=~"5.."}[5m])
      
      # Bot метрики
      - record: bot:message_latency:avg
        expr: rate(bot_message_processing_seconds_sum[5m]) / rate(bot_message_processing_seconds_count[5m])
      
      - record: bot:messages_per_minute
        expr: rate(bot_messages_total[1m])
      
      # Batch анализатор
      - record: batch:processing_duration:avg
        expr: rate(batch_processing_duration_seconds_sum[5m]) / rate(batch_processing_duration_seconds_count[5m])
      
      - record: batch:error_rate
        expr: rate(batch_errors_total[5m])
      
      # K8s ноды
      - record: node:cpu_usage
        expr: (1 - avg without (mode) (rate(node_cpu_seconds_total{mode="idle"}[5m]))) * 100
      
      - record: node:memory_usage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

### Этап 2: Grafana Dashboard JSON (3 часа)

**Файл:** `monitoring/grafana-dashboard.json`

```json
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": "-- Grafana --",
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": null,
  "links": [],
  "panels": [
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "lineWidth": 1,
            "showPoints": "auto"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "red",
                "value": 1000
              }
            ]
          },
          "unit": "ms"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "id": 2,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom"
        }
      },
      "pluginVersion": "8.0.0",
      "targets": [
        {
          "expr": "api:request_duration:p99",
          "interval": "",
          "legendFormat": "p99",
          "refId": "A"
        },
        {
          "expr": "api:request_duration:p95",
          "interval": "",
          "legendFormat": "p95",
          "refId": "B"
        }
      ],
      "title": "API Response Time (p99, p95)",
      "type": "timeseries"
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "thresholds"
          },
          "mappings": [],
          "max": 100,
          "min": 0,
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "yellow",
                "value": 5
              },
              {
                "color": "red",
                "value": 10
              }
            ]
          },
          "unit": "percent"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 0
      },
      "id": 3,
      "options": {
        "orientation": "auto",
        "showThresholdLabels": false,
        "showThresholdMarkers": true
      },
      "pluginVersion": "8.0.0",
      "targets": [
        {
          "expr": "api:error_rate * 100",
          "interval": "",
          "legendFormat": "Error Rate",
          "refId": "A"
        }
      ],
      "title": "API Error Rate %",
      "type": "gauge"
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "lineWidth": 1,
            "showPoints": "auto"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              }
            ]
          },
          "unit": "ms"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 8
      },
      "id": 4,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom"
        }
      },
      "pluginVersion": "8.0.0",
      "targets": [
        {
          "expr": "bot:message_latency:avg",
          "interval": "",
          "legendFormat": "Avg Latency",
          "refId": "A"
        }
      ],
      "title": "Bot Message Latency (avg)",
      "type": "timeseries"
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "lineWidth": 1,
            "showPoints": "auto"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              }
            ]
          },
          "unit": "short"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 8
      },
      "id": 5,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom"
        }
      },
      "pluginVersion": "8.0.0",
      "targets": [
        {
          "expr": "bot:messages_per_minute",
          "interval": "",
          "legendFormat": "Messages/min",
          "refId": "A"
        }
      ],
      "title": "Bot Messages Per Minute",
      "type": "timeseries"
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "lineWidth": 1,
            "showPoints": "auto"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              }
            ]
          },
          "unit": "percent"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 16
      },
      "id": 6,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom"
        }
      },
      "pluginVersion": "8.0.0",
      "targets": [
        {
          "expr": "batch:error_rate * 100",
          "interval": "",
          "legendFormat": "Error Rate",
          "refId": "A"
        }
      ],
      "title": "Batch Analyzer Error Rate %",
      "type": "timeseries"
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "lineWidth": 1,
            "showPoints": "auto"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              }
            ]
          },
          "unit": "percent"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 16
      },
      "id": 7,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom"
        }
      },
      "pluginVersion": "8.0.0",
      "targets": [
        {
          "expr": "node:cpu_usage",
          "interval": "",
          "legendFormat": "CPU %",
          "refId": "A"
        },
        {
          "expr": "node:memory_usage",
          "interval": "",
          "legendFormat": "Memory %",
          "refId": "B"
        }
      ],
      "title": "K8s Node Resources (CPU, Memory)",
      "type": "timeseries"
    }
  ],
  "schemaVersion": 27,
  "style": "dark",
  "tags": [
    "digital-twin",
    "production",
    "kpi"
  ],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "Digital Twin - KPI Dashboard",
  "uid": "digital-twin-kpi",
  "version": 0
}
```

### Этап 3: Alert Rules для Prometheus (1.5 часа)

**Файл:** `monitoring/prometheus-alert-rules.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-alert-rules
  namespace: monitoring
data:
  alert-rules.yaml: |
    groups:
    - name: digital-twin-alerts
      interval: 1m
      rules:
      # API алерты
      - alert: HighAPIErrorRate
        expr: api:error_rate > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High API error rate ({{ $value | humanizePercentage }})"
          description: "API error rate is above 5%"
      
      - alert: SlowAPIResponse
        expr: api:request_duration:p99 > 2000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Slow API response time ({{ $value | humanizeDuration }})"
          description: "p99 response time is above 2 seconds"
      
      # Bot алерты
      - alert: BotHighLatency
        expr: bot:message_latency:avg > 5000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Bot message latency is high ({{ $value | humanizeDuration }})"
          description: "Average message latency exceeds 5 seconds"
      
      # Batch анализатор алерты
      - alert: BatchAnalyzerErrors
        expr: batch:error_rate > 0.1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Batch analyzer errors ({{ $value | humanizePercentage }})"
          description: "Error rate exceeds 10%"
      
      # K8s алерты
      - alert: HighNodeCPU
        expr: node:cpu_usage > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage ({{ $value | humanizePercentage }})"
          description: "Node CPU usage exceeds 80%"
      
      - alert: HighNodeMemory
        expr: node:memory_usage > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage ({{ $value | humanizePercentage }})"
          description: "Node memory usage exceeds 85%"
```

### Этап 4: Deploy Dashboard (1 час)

```bash
# Применить Prometheus конфигурацию
kubectl apply -f monitoring/prometheus-custom-metrics.yaml
kubectl apply -f monitoring/prometheus-recording-rules.yaml
kubectl apply -f monitoring/prometheus-alert-rules.yaml

# Обновить Prometheus podы
kubectl rollout restart deployment/prometheus-server -n monitoring

# Тест Метрик (proxy к Prometheus)
kubectl port-forward svc/prometheus-server 9090:80 -n monitoring

# Открыть http://localhost:9090 и поиск:
# api:request_duration:p99
# bot:message_latency:avg
# batch:error_rate
```

### Этап 5: Import Dashboard в Grafana (30 мин)

```bash
# Proxy к Grafana
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring

# Открыть http://localhost:3000
# Импорт: +/Import Dashboard
# Выбрать monitoring/grafana-dashboard.json
# Конфигурация:
#   - Data source: Prometheus
#   - Name: "Digital Twin - KPI Dashboard"
#   - Save
```

### Этап 6: Setup Alerting в Grafana (30 мин)

```bash
# Alert Notification Channel:
# 1. Открыть Alert Notification Channels
# 2. Новый Telegram channel
# 3. Заполнить:
#    - Name: "Telegram Alerts"
#    - Bot Token: ${TELEGRAM_BOT_TOKEN}
#    - Chat ID: ${TELEGRAM_CHAT_ID}
# 4. Протестировать
```

### Этап 7: Testing дашборда (1 час)

```bash
# Открыть Grafana дашборд
# Проверить:
# 1. Все метрики отображаются
# 2. Графики актуальны
# 3. Алерты триггерятся правильно
# 4. Telegram нотификации поступают
```

---

## Успех Критерии

- ✅ Prometheus scrape configs: **Все таргеты активны**
- ✅ Recording rules: **Получают данные**
- ✅ Grafana Dashboard: **Все 6 панелей видны**
- ✅ Alert rules: **Все алерты сконфигурированы**
- ✅ Telegram notifications: **Нотификации принимаются**

---

## ПОЛЕЗНЫЕ ГИТХАБ РЕСУРсы

- https://github.com/prometheus/prometheus (Prometheus docs)
- https://github.com/grafana/grafana (Grafana docs)
- https://github.com/prometheus/alertmanager (AlertManager)
- https://github.com/loki-project/loki (Loki logs)

---

## ЭКСПЕРТЫ

| Отдел | Эксперт | Тема |
|:---:|:---:|:---:|
| **INFRA** | Marina G. (SRE) | Dashboard design и alerts |
| **INFRA** | Pavel T. (K8s Lead) | K8s deployment |
| **INFRA** | Alexei M. (Cloud Arch) | Metrics optimization |

---

**Статус:** 🟢 READY FOR ASSIGNMENT
**Время на выполнение:** 📅 Пятница, 11 дек (09:00-17:00)
**Предыдущая задача:** TASK-002 и TASK-003 (готовы)
**Место принятия:** `/TASKS/TASK-004-GRAFANA-DASHBOARD.md`
