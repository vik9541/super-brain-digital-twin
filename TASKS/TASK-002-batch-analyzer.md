# 📃 TASK-002: Batch Analyzer CronJob

**Ответственные ТИМ:М AI-ML отдел**

| Роль | Ответственность | Требуемые Кнания |
|:---:|:---|:---:|
| **Dmitry K.** (ML Ops Lead) | Kubernetes CronJob YAML | kubectl, helm, K8s |
| **Natalia V.** (Data Science) | batch_analyzer.py логика | Python, Pandas, SQL |
| **Andrey M.** (AI Lead) | Perplexity API интеграция | API, async/await |
| **Igor S.** (NLP Specialist) | Обработка текста | NLP, parsing |

**Приоритет:** 🟡 IMPORTANT  
**На дату:** Среда, 9 декабря 2025  
**Время выполнения:** 6 часов  
**Зависимости:** TASK-001 (Bot) может работать 

---

## 🏗️ АРХИТЕКТУРА

```
Supabase Database
    ↑ (SELECT projects WHERE status='active')
    │
    └─ batch_analyzer.py (CronJob Pod)
    │   └─ Начинается в 02:00 UTC
    │   └─ Проверит активные проекты
    │   └─ Отравит каждый в Perplexity API
    │   └─ Отправит результаты в Telegram
    │
    └─ K8s API (Prometheus metrics)
         └─ batch.duration_seconds
         └─ batch.projects_processed
         └─ batch.errors_count
```

---

## 📊 ПОНЕдЕЛЬНО-ПЦИКЛОГРАММА

### Этап 1: K8s CronJob YAML (09:00-10:30)

**Файл:** `k8s/batch-analyzer-cronjob.yaml`

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: batch-analyzer
  namespace: production
spec:
  # Час 2:00 AM UTC каждые сутки
  schedule: "0 2 * * *"
  
  # Не u0434ерживать более 3 одновременных запусков
  concurrencyPolicy: Forbid
  
  # Выполнять предыдущие Job если они еще работают
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  
  jobTemplate:
    spec:
      backoffLimit: 2  # Перезапуск в случае ошибки
      activeDeadlineSeconds: 3600  # 1 час макс
      
      template:
        spec:
          serviceAccountName: batch-analyzer
          restartPolicy: OnFailure
          
          containers:
          - name: analyzer
            image: registry.digitalocean.com/digital-twin-registry/batch-analyzer:latest
            imagePullPolicy: Always
            
            # Переменные окружения
            env:
            - name: SUPABASE_URL
              valueFrom:
                secretKeyRef:
                  name: supabase-secrets
                  key: url
            - name: SUPABASE_KEY
              valueFrom:
                secretKeyRef:
                  name: supabase-secrets
                  key: key
            - name: PERPLEXITY_API_KEY
              valueFrom:
                secretKeyRef:
                  name: perplexity-secrets
                  key: api-key
            - name: TELEGRAM_BOT_TOKEN
              valueFrom:
                secretKeyRef:
                  name: telegram-secrets
                  key: bot-token
            
            # Ресурсы
            resources:
              requests:
                cpu: 500m
                memory: 1Gi
              limits:
                cpu: 2000m
                memory: 2Gi
            
            # Liveness & Readiness
            livenessProbe:
              exec:
                command:
                - /bin/sh
                - -c
                - test -f /tmp/batch_running || exit 0
              initialDelaySeconds: 30
              periodSeconds: 60
```

**Команды:**
```bash
# Сохранить YAML
git add k8s/batch-analyzer-cronjob.yaml

# Нанести в K8s
kubectl apply -f k8s/batch-analyzer-cronjob.yaml

# Проверить
kubectl get cronjobs -n production
```

---

### Этап 2: Python batch_analyzer.py (10:30-13:00)

**Файл:** `bot/batch_analyzer.py`

```python
import asyncio
import os
from datetime import datetime
from typing import List, Dict
import aiohttp
from supabase import create_client
from telegram import Bot
import logging

# Конфиг
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEFAULT_USER_ID = int(os.getenv("DEFAULT_USER_ID"))

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class BatchAnalyzer:
    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.perplexity_url = "https://api.perplexity.ai/openai/v1/chat/completions"
        self.stats = {
            "processed": 0,
            "errors": 0,
            "start_time": datetime.now()
        }
    
    async def get_active_projects(self) -> List[Dict]:
        """Получи активные проекты из Supabase"""
        try:
            response = self.supabase.table("projects").select("*").eq("status", "active").execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching projects: {e}")
            return []
    
    async def analyze_project_with_ai(self, project: Dict) -> str:
        """Пошли проект в Perplexity для анализа"""
        prompt = f"""
        Analyze this project:
        - Name: {project['name']}
        - Description: {project['description']}
        - Status: {project['status']}
        - Progress: {project['progress']}%
        
        Provide:
        1. Quick assessment
        2. Risks identified
        3. Next steps
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "sonar-reasoning-pro",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500
                }
                
                async with session.post(self.perplexity_url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        logger.error(f"Perplexity API error: {resp.status}")
                        return "Analysis failed"
        except Exception as e:
            logger.error(f"Error analyzing project: {e}")
            self.stats["errors"] += 1
            return f"Error: {str(e)}"
    
    async def send_telegram_report(self, project: Dict, analysis: str):
        """Пошли отчет в Telegram"""
        try:
            message = f"""
            📊 **Batch Analysis Report**
            
            **Project:** {project['name']}
            **Progress:** {project['progress']}%
            
            **AI Analysis:**
            {analysis}
            
            ⏰ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
            """
            
            await self.bot.send_message(
                chat_id=DEFAULT_USER_ID,
                text=message,
                parse_mode="Markdown"
            )
            self.stats["processed"] += 1
        except Exception as e:
            logger.error(f"Error sending telegram: {e}")
            self.stats["errors"] += 1
    
    async def run(self):
        """Главный цикл batch analyzer"""
        logger.info("Starting batch analyzer...")
        
        projects = await self.get_active_projects()
        logger.info(f"Found {len(projects)} active projects")
        
        for project in projects:
            logger.info(f"Analyzing project: {project['name']}")
            analysis = await self.analyze_project_with_ai(project)
            await self.send_telegram_report(project, analysis)
        
        # Отправь итоговый отчет
        duration = (datetime.now() - self.stats["start_time"]).total_seconds()
        summary = f"""
        ✅ **Batch Analysis Complete**
        
        **Stats:**
        - Projects processed: {self.stats['processed']}
        - Errors: {self.stats['errors']}
        - Duration: {duration:.1f} seconds
        
        ⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
        """
        
        await self.bot.send_message(
            chat_id=DEFAULT_USER_ID,
            text=summary,
            parse_mode="Markdown"
        )

async def main():
    analyzer = BatchAnalyzer()
    await analyzer.run()

if __name__ == "__main__":
    asyncio.run(main())
```

---

### Этап 3: Docker Image (13:00-14:00)

**Файл:** `Dockerfile.batch-analyzer`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot/ .

CMD ["python", "batch_analyzer.py"]
```

**requirements.txt:**
```
aiohttp==3.9.1
supabase==2.4.0
python-telegram-bot==21.0
pydantic==2.5.0
python-dotenv==1.0.0
```

**Команды:**
```bash
# Собрать имаж
docker build -f Dockerfile.batch-analyzer -t registry.digitalocean.com/digital-twin-registry/batch-analyzer:latest .

# Пушить в registry
docker push registry.digitalocean.com/digital-twin-registry/batch-analyzer:latest
```

---

### Этап 4: K8s Deployment + Testing (14:00-15:00)

**Команды:**
```bash
# Проверить CronJob состояние
kubectl get cronjobs -n production
kubectl describe cronjob batch-analyzer -n production

# Мануальное тестирование
kubectl create job --from=cronjob/batch-analyzer test-batch -n production

# Мониторить запуск
kubectl get jobs -n production -w
kubectl logs job/test-batch -n production -f

# Проверить ошибки
kubectl describe pod <pod-name> -n production
```

---

## ✅ Критерии УСПЕХА

- [ ] CronJob создан (kubectl get cronjobs)
- [ ] batch_analyzer.py работает локально
- [ ] Docker имаж в registry
- [ ] Job запускается вручную
- [ ] Telegram отчет получен
- [ ] Prometheus метрики регистрируются

---

## 🔗 Основные ресурсы

- **Kubernetes CronJob:** https://github.com/kubernetes/kubernetes
- **Kubeflow:** https://github.com/kubeflow/kubeflow
- **Supabase Python:** https://github.com/supabase/supabase-py
- **Telegram Bot:** https://github.com/python-telegram-bot/python-telegram-bot
- **Perplexity API:** https://docs.perplexity.ai

---

**Состояние:** 🟢 READY FOR EXECUTION  
**Время снова жение:** 7 декабря 2025