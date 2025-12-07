# 📃 TASK-002: BATCH ANALYZER CRONJOB

**Фаза:** WEEK 1 (среда, 9 декабря)
**Уровень приоритета:** 🟣 CRITICAL
**Ответственная команда:** INFRA
**Наследует он:** TASK-001 (Bot готов)

---

## цель

Создать **K8s CronJob** на DigitalOcean DOKS, который каждые 2 часа (в 02:00 UTC) берет данные из Supabase и анализирует их с Perplexity API.

---

## Что надо сделать

### Этап 1: K8s CronJob YAML (2 часа)

**Файл:** `k8s/batch-analyzer-cronjob.yaml`

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: batch-analyzer
  namespace: production
  labels:
    app: digital-twin
    component: batch-analyzer
spec:
  # Каждые 2 часа в 02:00 UTC (00:00, 02:00, 04:00 ... 22:00)
  schedule: "0 */2 * * *"
  concurrencyPolicy: Forbid  # Не рав другому
  successfulJobsHistoryLimit: 3  # Хранить 3 успешных
  failedJobsHistoryLimit: 3  # Хранить 3 неудачных
  
  jobTemplate:
    spec:
      backoffLimit: 3  # Пересопробюй 3 раза
      activeDeadlineSeconds: 3600  # Таймаут 1 час
      
      template:
        metadata:
          labels:
            app: digital-twin
            batch: analyzer
        spec:
          serviceAccountName: batch-analyzer
          restartPolicy: OnFailure
          
          containers:
          - name: analyzer
            image: registry.digitalocean.com/digital-twin-registry/batch-analyzer:latest
            imagePullPolicy: Always
            
            env:
            - name: SUPABASE_URL
              valueFrom:
                secretKeyRef:
                  name: supabase-credentials
                  key: url
            - name: SUPABASE_KEY
              valueFrom:
                secretKeyRef:
                  name: supabase-credentials
                  key: key
            - name: PERPLEXITY_API_KEY
              valueFrom:
                secretKeyRef:
                  name: api-credentials
                  key: perplexity
            - name: TELEGRAM_BOT_TOKEN
              valueFrom:
                secretKeyRef:
                  name: api-credentials
                  key: telegram
            - name: BATCH_SIZE
              value: "100"
            - name: MAX_WORKERS
              value: "5"
            - name: TIMEOUT_SECONDS
              value: "300"
            
            resources:
              requests:
                cpu: 500m
                memory: 1Gi
              limits:
                cpu: 2000m
                memory: 2Gi
            
            livenessProbe:
              exec:
                command: ["python", "-c", "import sys; sys.exit(0)"]
              initialDelaySeconds: 10
              periodSeconds: 30
            
            volumeMounts:
            - name: tmp
              mountPath: /tmp
            
          volumes:
          - name: tmp
            emptyDir: {}
```

### Этап 2: ServiceAccount + RBAC (30 мин)

**Файл:** `k8s/batch-analyzer-rbac.yaml`

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: batch-analyzer
  namespace: production
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: batch-analyzer
  namespace: production
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: batch-analyzer
  namespace: production
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: batch-analyzer
subjects:
- kind: ServiceAccount
  name: batch-analyzer
  namespace: production
```

### Этап 3: Python batch_analyzer.py (3 часа)

**Ключевые ретипс:**

```python
import os
import asyncio
from supabase import create_client
from perplexity import PerplexityClient
import telegram

class BatchAnalyzer:
    def __init__(self):
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        self.perplexity = PerplexityClient(
            api_key=os.getenv("PERPLEXITY_API_KEY")
        )
        self.telegram_bot = telegram.Bot(
            token=os.getenv("TELEGRAM_BOT_TOKEN")
        )
    
    async def run(self):
        """Main batch analysis function"""
        # 1. Получи данные нуждающиеся анализа
        unanalyzed = await self.get_unanalyzed_data()
        
        # 2. Анализируй с Perplexity
        results = await self.analyze_with_perplexity(unanalyzed)
        
        # 3. Сохрани в Supabase
        await self.save_results(results)
        
        # 4. Отправь отчет в Telegram
        await self.send_report(results)
        
        print(f"Batch analysis completed: {len(results)} records")

if __name__ == "__main__":
    analyzer = BatchAnalyzer()
    asyncio.run(analyzer.run())
```

### Этап 4: Docker образ (1 час)

**Файл:** `Dockerfile.batch-analyzer`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Зависимости
COPY requirements.batch-analyzer.txt .
RUN pip install --no-cache-dir -r requirements.batch-analyzer.txt

# Код
COPY batch_analyzer.py .
COPY src/ src/

CMD ["python", "batch_analyzer.py"]
```

### Этап 5: Docker push в DOCR (30 мин)

```bash
# Собрать
docker build -f Dockerfile.batch-analyzer \
  -t registry.digitalocean.com/digital-twin-registry/batch-analyzer:v1.0.0 .

# Пушить
docker push registry.digitalocean.com/digital-twin-registry/batch-analyzer:v1.0.0

# Не u0437абудь login!
docker login registry.digitalocean.com
```

### Этап 6: Deploy K8s (1 час)

```bash
# Примени
 kubectl apply -f k8s/batch-analyzer-rbac.yaml
kubectl apply -f k8s/batch-analyzer-cronjob.yaml

# Проверь
kubectl get cronjobs -n production
kubectl describe cronjob batch-analyzer -n production
```

### Этап 7: Monitoring & Testing (1 час)

```bash
# Ьтестируй вручную (Job выстрелит на 1 мин)
kubectl create job --from=cronjob/batch-analyzer test-batch -n production

# Монитори
kubectl logs job/test-batch -n production -f

# Посмотри все jobs
kubectl get jobs -n production
```

---

## Успех Критерии

- ✅ CronJob состояние: **Active**
- ✅ Job выполнен: **1 успешная**
- ✅ Pod logs: **Нет ошибок**
- ✅ Supabase: **Данные сохранены**
- ✅ Telegram: **Отчет получен**

---

## ПРОИГНОРИРОВАННЫЕ ОШИБки & НАПОМиНАНиЕ

| Ошибка | Решение |
|:---|:---|
| Job завешывается | Проверь activeDeadlineSeconds (3600) |
| ImagePullBackOff | docker login registry.digitalocean.com |
| Permission denied | Проверь RBAC role |
| Timeout от API | Ограничь batch_size, увеличь timeout |

---

## ПОЛЕЗНЫЕ ГИТХАб РЕСУРСЫ

- **Kubernetes CronJob:** https://github.com/kubernetes/kubernetes
- **Kubeflow:** https://github.com/kubeflow/kubeflow
- **K8s Examples:** https://github.com/kubernetes/examples

---

## ЭКСПЕРТЫ

| Отдел | Эксперт | Тема |
|:---:|:---:|:---:|
| **INFRA** | Pavel T. | K8s deployment |
| **INFRA** | Sergey B. | CI/CD integration |
| **INFRA** | Marina G. | Monitoring CronJob |
| **AI-ML** | Dmitry K. | Batch analyzer logic |

---

**Статус:** 🟢 READY FOR ASSIGNMENT
**Дата:** 7 декабря 2025
**Время на выполнение:** 📅 Среда, 9 дек (09:00-17:00)
