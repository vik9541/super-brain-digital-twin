# 📋 TASK-002: Batch Analyzer Deployment — INFRA TEAM CHECKLIST

**🟠 Статус:** АКТИВНА  
**👤 Команда:** INFRA  
**💼 Ответственные:** Pavel T., Sergey B., Marina G., Dmitry K.  
**📅 Дедлайн:** 9 декабря 2025, 17:00 MSK  
**⚡ Приоритет:** 🔴 CRITICAL  

---

## 📝 ТЕХНИЧЕСКОЕ ЗАДАНИЕ

**Цель:** Полный deployment Batch Analyzer CronJob в production K8s кластере с всеми проверками, мониторингом и документацией.

---

## 📄 PHASE 1: PREPARATION (30 min)

### Step 1.1: Прочтите документацию

- [ ] Полная спецификация (GitHub):
  https://github.com/vik9541/super-brain-digital-twin/blob/main/TASKS/TASK-002-batch-analyzer.md
  
- [ ] Код Batch Analyzer:
  https://github.com/vik9541/super-brain-digital-twin/blob/main/batch_analyzer.py
  
- [ ] Dockerfile:
  https://github.com/vik9541/super-brain-digital-twin/blob/main/Dockerfile.batch-analyzer
  
- [ ] K8s конфиги:
  https://github.com/vik9541/super-brain-digital-twin/tree/main/k8s

### Step 1.2: Настройка окружения

```bash
# Убедитесь что вы в нужном энвайронменте
$ kubectl config current-context
# Ожидаем: production-cluster или similar

# Проверите namespace
$ kubectl get ns | grep production
# Ожидаем: production ACTIVE
```

- [ ] Context настроен верно
- [ ] Namespace production существует
- [ ] Docker registry credentials настроены

### Step 1.3: Получите credentials

```bash
# Получите DigitalOcean registry credentials
$ doctl registry login

# Получите Supabase credentials
$ echo "SUPABASE_URL=" && echo "SUPABASE_KEY="

# Получите Telegram Token
$ echo "TELEGRAM_BOT_TOKEN=" && echo "DEFAULT_USER_ID="
```

- [ ] Registry login выполнен
- [ ] Supabase учетные данные получены
- [ ] Telegram credentials получены

---

## 🐨 PHASE 2: DOCKER BUILD & PUSH (1 hour)

### Step 2.1: Клонируйте репозиторий

```bash
$ cd /tmp && git clone https://github.com/vik9541/super-brain-digital-twin.git
$ cd super-brain-digital-twin
$ git pull origin main
```

**Почтарь:**
```bash
$ git log --oneline -1
# Ожидаем: понедельниковые коммиты
```

- [ ] Репозиторий клонирован

### Step 2.2: Встройте Docker образ

```bash
$ docker build -f Dockerfile.batch-analyzer -t batch-analyzer:v1.0.0 .
```

**Ожидаемые сообщения:**
```
Step 1/6 : FROM python:3.11-slim
Step 2/6 : WORKDIR /app
Step 3/6 : COPY requirements.txt .
Step 4/6 : RUN pip install --no-cache-dir -r requirements.txt
Step 5/6 : COPY bot/ .
Step 6/6 : CMD ["python", "batch_analyzer.py"]
Successfully built <HASH>
```

- [ ] Docker build успешно завершен
- [ ] Не юта ошибок в логах

### Step 2.3: Оттегируйте образ

```bash
# Замените YOUR_REGISTRY_URL на ваш
$ REGISTRY="registry.digitalocean.com/your-account"

$ docker tag batch-analyzer:v1.0.0 $REGISTRY/batch-analyzer:v1.0.0
$ docker tag batch-analyzer:v1.0.0 $REGISTRY/batch-analyzer:latest

$ echo "Tagged images:"
$ docker images | grep batch-analyzer
```

- [ ] Образы оттегированы

### Step 2.4: Залите в registry

```bash
$ docker push $REGISTRY/batch-analyzer:v1.0.0
$ docker push $REGISTRY/batch-analyzer:latest

# Покажет прогресс
Pushing [====] 50.12MB/50.12MB
v1.0.0: digest: sha256:abc123def456...
latest: digest: sha256:abc123def456...
```

- [ ] Push v1.0.0 успешны
- [ ] Push latest успешны

### Step 2.5: Проверите в registry

```bash
# Проверите что образ действительно в registry
$ docker pull $REGISTRY/batch-analyzer:v1.0.0
# Ожидаем: Successfully pulled image
```

- [ ] Image pull с registry успешен
- [ ] Digest зафиксирован

---

## ⚒️ PHASE 3: KUBERNETES DEPLOYMENT (1 hour)

### Step 3.1: Настройка secrets

```bash
# Проверите что секреты уже настроены
$ kubectl get secrets -n production
# Ожидаем:
# - supabase-secrets
# - perplexity-secrets
# - telegram-secrets
# - registry-credentials

# Если нет, создайте:
$ kubectl create secret generic supabase-secrets \
  --from-literal=url=$SUPABASE_URL \
  --from-literal=key=$SUPABASE_KEY \
  -n production

$ kubectl create secret generic telegram-secrets \
  --from-literal=bot-token=$TELEGRAM_BOT_TOKEN \
  -n production
```

- [ ] supabase-secrets наличся
- [ ] telegram-secrets наличся
- [ ] registry-credentials наличся

### Step 3.2: Настройка RBAC

```bash
$ kubectl apply -f k8s/batch-analyzer-rbac.yaml

# Проверите результат:
serviceaccount/batch-analyzer created
clusterrole.rbac.authorization.k8s.io/batch-analyzer created
clusterrolebinding.rbac.authorization.k8s.io/batch-analyzer created
```

- [ ] RBAC все элементы созданы

### Step 3.3: Обновите image в YAML

```bash
# Откройте k8s/batch-analyzer-cronjob.yaml
# И режиме линию до вашего image:

image: registry.digitalocean.com/your-account/batch-analyzer:v1.0.0

# Проверите что это строка на месте
```

- [ ] Image URL обновлен

### Step 3.4: Разверните CronJob

```bash
$ kubectl apply -f k8s/batch-analyzer-cronjob.yaml

# Ожидаемые результаты:
cronjob.batch/batch-analyzer created
```

- [ ] CronJob создан

### Step 3.5: Проверите CronJob

```bash
$ kubectl get cronjobs -n production
# Ожидаем:
NAME                SCHEDULE     SUSPEND   ACTIVE   LAST SCHEDULE   AGE
batch-analyzer      0 2 * * *    False     0        <none>          10s

$ kubectl describe cronjob batch-analyzer -n production
```

- [ ] Schedule: `0 2 * * *`
- [ ] Suspend: `False`
- [ ] Status: ОК

---

## 🧙 PHASE 4: TESTING (1 hour)

### Step 4.1: Тестовый Job

```bash
$ kubectl create job --from=cronjob/batch-analyzer test-batch-run \
  --dry-run=client -o yaml | \
  kubectl set env -f - SUPABASE_URL=$SUPABASE_URL \
  SUPABASE_KEY=$SUPABASE_KEY \
  TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN | \
  kubectl apply -f -

# Простейший вариант:
$ kubectl create job test-batch-001 --from=cronjob/batch-analyzer -n production
```

- [ ] Job создан

### Step 4.2: Мониторите Job

```bash
# Мосмотрите статус
$ kubectl get jobs -n production -w
# Ctrl+C когда статус изменится

# Покажет pod name
$ kubectl get pods -n production | grep test-batch

# Заполните pod name и смотрите логи
$ kubectl logs pod/test-batch-001-xxxx -n production -f
```

- [ ] Pod сохранен и запускается
- [ ] Логи нолжны показывать анализ данных

### Step 4.3: Проверите ПО кончились

```bash
# Ожидаем Job до конца
$ kubectl get jobs -n production
# Ожидаем: COMPLETIONS 1/1, SUCCESS

# Проверите последние логи
$ kubectl logs job/test-batch-001 -n production
```

- [ ] Job COMPLETED
- [ ] Exit code 0
- [ ] Нет ошибок в логах

### Step 4.4: Проверите Supabase

```bash
# Способ 1: В Supabase Dashboard
# Найти: table analysis_queue
# Проверить: SELECT COUNT(*) WHERE status='completed' > 0

# Способ 2: в SQL
# SELECT id, project_name, status, created_at FROM analysis_queue 
# WHERE created_at > NOW() - INTERVAL '1 hour'
# ORDER BY created_at DESC LIMIT 10;
```

- [ ] В Supabase есть новые записи
- [ ] status = 'completed'

### Step 4.5: Проверите Telegram

```bash
# Проверите что в Telegram пришло сообщение:
# - Название проекта
# - Аналитика
# - Timestamp
```

- [ ] Telegram сообщение получено

---

## 📊 PHASE 5: VERIFICATION & MONITORING (30 min)

### Step 5.1: Проверите Prometheus

```bash
# Проверите что метрики собираются
$ kubectl port-forward -n monitoring svc/prometheus-server 9090:80 &
# Откройте http://localhost:9090

# В Prometheus Targets проверите:
# - batch-analyzer pod наличся
# - metrics scraping работает

# В Prometheus Alerts проверите:
# - BatchAnalyzerJobDuration
# - BatchAnalyzerErrorRate
```

- [ ] Prometheus собирает метрики
- [ ] Alert rules активны

### Step 5.2: Проверите в Grafana

```bash
# Откройте Grafana
$ kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80 &
# Откройте http://localhost:3000

# Найдите dashboard: Batch Analyzer Metrics
# Проверите что метрики отображаются
```

- [ ] Grafana доступен
- [ ] Metrics видны

---

## 📋 DOCUMENTATION & REPORTING

### Step 6.1: Составите отчет

**Репозиторий файл:** `TASKS/TASK-002-BATCH-ANALYZER-COMPLETED.md`

```markdown
# ✅ TASK-002: Batch Analyzer — COMPLETION REPORT

**Статус:** 🟢 COMPLETED  
**Дата Начала:** 9 дек 2025 09:00 MSK  
**Дата Завершения:** [TODAY] [TIME] MSK  
**Ответственные:** Pavel T., Sergey B., Marina G.  

## ✅ Что сделано

### Docker
- [x] Docker образ собран
- [x] Образ залит в registry
- [x] Image digest: [YOUR_DIGEST]

### Kubernetes
- [x] RBAC настроен
- [x] CronJob развернута
- [x] Test job запускался и вычислена

### Верификация
- [x] Supabase: [XX] новых рекордов
- [x] Telegram: уведомление получено
- [x] Prometheus: метрики собираются

## 📊 Ключевые метрики

| Метрика | Значение |
|:---|:---|
| Execution Time | [XX] sec |
| Projects Processed | [XX] |
| Success Rate | 100% |
| Error Count | 0 |
| Memory Peak | [XX] Mi |
| CPU Peak | [XX] m |

## 🔗 GitHub References

- Commit: [YOUR_COMMIT_HASH]
- Dockerfile: https://github.com/vik9541/super-brain-digital-twin/blob/main/Dockerfile.batch-analyzer
- Code: https://github.com/vik9541/super-brain-digital-twin/blob/main/batch_analyzer.py
- K8s Config: https://github.com/vik9541/super-brain-digital-twin/tree/main/k8s

## 📸 Screenshots

```
Output from: kubectl get cronjobs -n production
Output from: kubectl logs job/test-batch-001 -n production
Screenshot: Supabase records
Screenshot: Telegram message
Screenshot: Prometheus metrics
```

## ✅ Критерии успеха

- [x] CronJob status: ACTIVE
- [x] Test job: COMPLETED
- [x] Data in Supabase: OK
- [x] Telegram alerts: OK
- [x] Prometheus metrics: OK
- [x] No pod errors: OK

---
**Проверено:** [YOUR_MANAGER]  
**Дата:** [TODAY]
```

- [ ] Report составлен

### Step 6.2: Git commit

```bash
$ git add TASKS/TASK-002-BATCH-ANALYZER-COMPLETED.md
$ git commit -m "Complete TASK-002: Batch Analyzer deployed successfully"
$ git push origin main
```

- [ ] Report залит в GitHub

---

## 🗑️ CLEANING UP (optional)

```bash
# Удалить test job если нужно
$ kubectl delete job test-batch-001 -n production

# Проверить что CronJob готов к next run
$ kubectl describe cronjob batch-analyzer -n production
```

---

## 📞 SUPPORT & TROUBLESHOOTING

**Проблема:** `ImagePullBackOff`  
**Решение:** Проверьте registry credentials в k8s
```bash
kubectl get secrets -n production | grep registry
```

**Проблема:** `CrashLoopBackOff`  
**Решение:** Проверьте логи
```bash
kubectl logs <pod> -n production
```

**Проблема:** CronJob не запускается  
**Решение:** Проверьте schedule синтаксис и системное время
```bash
kubectl describe cronjob batch-analyzer -n production
```

---

**🎉 При успешном завершении:**

✅ Notify team in Slack #super-brain-deployment  
✅ Update CHECKLIST.md mark as [x] TASK-002  
✅ Schedule next task: TASK-003 (Reports Generator)
