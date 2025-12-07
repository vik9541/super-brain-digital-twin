# 📃 TASK-003: REPORTS GENERATOR CRONJOB

**Фаза:** WEEK 1 (четверг, 10 декабря)
**Уровень приоритета:** 🟣 IMPORTANT
**Ответственная команда:** PRODUCT
**Наследует он:** TASK-002 (Batch Analyzer работает)

---

## цель

Создать **ежечасные отчеты** в формате **Excel** и наборы **email и Telegram** навигация в 00:00 UTC каждого часа.

---

## Что надо сделать

### Этап 1: K8s CronJob YAML (1 час)

**Файл:** `k8s/reports-generator-cronjob.yaml`

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: reports-generator
  namespace: production
  labels:
    app: digital-twin
    component: reports-generator
spec:
  # Каждый час в XX:00 (00:00, 01:00, 02:00 ... 23:00)
  schedule: "0 * * * *"
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 5
  failedJobsHistoryLimit: 3
  
  jobTemplate:
    spec:
      backoffLimit: 2
      activeDeadlineSeconds: 1800  # 30 минут
      
      template:
        metadata:
          labels:
            app: digital-twin
            reports: generator
        spec:
          serviceAccountName: reports-generator
          restartPolicy: OnFailure
          
          containers:
          - name: generator
            image: registry.digitalocean.com/digital-twin-registry/reports-generator:latest
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
            - name: TELEGRAM_BOT_TOKEN
              valueFrom:
                secretKeyRef:
                  name: api-credentials
                  key: telegram
            - name: TELEGRAM_CHAT_ID
              valueFrom:
                secretKeyRef:
                  name: api-credentials
                  key: telegram-chat-id
            - name: SMTP_HOST
              valueFrom:
                configMapKeyRef:
                  name: email-config
                  key: smtp-host
            - name: SMTP_USER
              valueFrom:
                secretKeyRef:
                  name: email-credentials
                  key: user
            - name: SMTP_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: email-credentials
                  key: password
            - name: SMTP_FROM
              valueFrom:
                configMapKeyRef:
                  name: email-config
                  key: from-email
            - name: SMTP_TO
              valueFrom:
                configMapKeyRef:
                  name: email-config
                  key: to-emails
            - name: REPORT_TEMPLATE
              value: "hourly"
            
            resources:
              requests:
                cpu: 250m
                memory: 512Mi
              limits:
                cpu: 1000m
                memory: 1Gi
            
            volumeMounts:
            - name: tmp
              mountPath: /tmp
            
          volumes:
          - name: tmp
            emptyDir: {}
```

### Этап 2: Python reports_generator.py (3 часа)

**Ключевые функции:**

```python
import os
import asyncio
from datetime import datetime, timedelta
from supabase import create_client
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.encoders import encode_base64
import telegram

class ReportsGenerator:
    def __init__(self):
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        self.telegram_bot = telegram.Bot(
            token=os.getenv("TELEGRAM_BOT_TOKEN")
        )
        self.smtp_config = {
            "host": os.getenv("SMTP_HOST"),
            "user": os.getenv("SMTP_USER"),
            "password": os.getenv("SMTP_PASSWORD"),
            "from": os.getenv("SMTP_FROM"),
            "to": os.getenv("SMTP_TO").split(",")
        }
    
    async def run(self):
        """Main report generation function"""
        try:
            # 1. Приготовь данные
            data = await self.fetch_hourly_data()
            
            # 2. Генерируй Excel
            excel_file = self.generate_excel_report(data)
            
            # 3. Отправь email
            await self.send_email_report(excel_file)
            
            # 4. Отправь Telegram
            await self.send_telegram_report(excel_file)
            
            print(f"Report generated successfully at {datetime.utcnow().isoformat()}")
            
        except Exception as e:
            print(f"Error generating report: {e}")
            await self.send_error_alert(str(e))
    
    async def fetch_hourly_data(self) -> dict:
        """Fetch data for the last hour"""
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        
        # Получи анализы
        response = self.supabase.table("analyses") \
            .select("*") \
            .gte("created_at", hour_ago.isoformat()) \
            .lte("created_at", now.isoformat()) \
            .execute()
        
        return response.data
    
    def generate_excel_report(self, data: list) -> str:
        """Generate Excel report from data"""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Hourly Report"
        
        # Заголовки
        headers = [
            "ID", "Timestamp", "Status", "Duration (s)",
            "Records Processed", "Records Failed", "Success Rate"
        ]
        
        # Оформление
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Данные
        for row, record in enumerate(data, 2):
            ws.cell(row=row, column=1, value=record.get("id"))
            ws.cell(row=row, column=2, value=record.get("created_at"))
            ws.cell(row=row, column=3, value=record.get("status"))
            ws.cell(row=row, column=4, value=record.get("duration"))
            ws.cell(row=row, column=5, value=record.get("records_processed"))
            ws.cell(row=row, column=6, value=record.get("records_failed"))
            
            # Расчет процента
            success_rate = 100 if record.get("records_processed") == 0 else (
                (record.get("records_processed") - record.get("records_failed")) / 
                record.get("records_processed") * 100
            )
            ws.cell(row=row, column=7, value=f"{success_rate:.1f}%")
        
        # Авто ширина
        for column in ws.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column[0].column_letter].width = adjusted_width
        
        # Сохрани
        filename = f"/tmp/report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
        wb.save(filename)
        return filename
    
    async def send_email_report(self, excel_file: str) -> bool:
        """Send report via email"""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.smtp_config["from"]
            msg["To"] = ", ".join(self.smtp_config["to"])
            msg["Subject"] = f"Digital Twin Hourly Report - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
            
            # Body
            body = f"""Hourly report for Digital Twin system.
            
Generated at: {datetime.utcnow().isoformat()}
            
Please see attached Excel file for details.
            
Best regards,
Digital Twin Bot
            """
            msg.attach(MIMEText(body, "plain"))
            
            # Attachment
            with open(excel_file, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {excel_file.split('/')[-1]}",
                )
                msg.attach(part)
            
            # Send
            with smtplib.SMTP_SSL(self.smtp_config["host"], 465) as server:
                server.login(self.smtp_config["user"], self.smtp_config["password"])
                server.sendmail(
                    self.smtp_config["from"],
                    self.smtp_config["to"],
                    msg.as_string()
                )
            
            print(f"Email sent to {self.smtp_config['to']}")
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    async def send_telegram_report(self, excel_file: str) -> bool:
        """Send report via Telegram"""
        try:
            chat_id = int(os.getenv("TELEGRAM_CHAT_ID"))
            
            with open(excel_file, "rb") as f:
                await self.telegram_bot.send_document(
                    chat_id=chat_id,
                    document=f,
                    caption=f"Hourly Report - {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
                )
            
            print(f"Telegram report sent to {chat_id}")
            return True
        except Exception as e:
            print(f"Error sending Telegram report: {e}")
            return False
    
    async def send_error_alert(self, error: str):
        """Send error alert to Telegram"""
        try:
            chat_id = int(os.getenv("TELEGRAM_CHAT_ID"))
            await self.telegram_bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ ERROR in Reports Generator:\n{error}"
            )
        except:
            pass

if __name__ == "__main__":
    generator = ReportsGenerator()
    asyncio.run(generator.run())
```

### Этап 3: Конфигурация ConfigMap для Email (30 мин)

**Файл:** `k8s/reports-generator-config.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: email-config
  namespace: production
data:
  smtp-host: "smtp.gmail.com"
  from-email: "noreply@97v.ru"
  to-emails: "admin@97v.ru,team@97v.ru"
---
apiVersion: v1
kind: Secret
metadata:
  name: email-credentials
  namespace: production
type: Opaque
stringData:
  user: "your-email@gmail.com"
  password: "your-app-password"
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: reports-generator
  namespace: production
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: reports-generator
  namespace: production
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: reports-generator
  namespace: production
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: reports-generator
subjects:
- kind: ServiceAccount
  name: reports-generator
  namespace: production
```

### Этап 4: Docker (1 час)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.reports.txt .
RUN pip install --no-cache-dir -r requirements.reports.txt

COPY reports_generator.py .
COPY src/ src/

CMD ["python", "reports_generator.py"]
```

### Этап 5: Deploy (1 час)

```bash
# Build & Push
docker build -f Dockerfile.reports \
  -t registry.digitalocean.com/digital-twin-registry/reports-generator:v1.0.0 .
docker push registry.digitalocean.com/digital-twin-registry/reports-generator:v1.0.0

# Apply K8s
kubectl apply -f k8s/reports-generator-config.yaml
kubectl apply -f k8s/reports-generator-cronjob.yaml

# Check
kubectl get cronjobs -n production
kubectl describe cronjob reports-generator -n production
```

### Этап 6: Testing (30 мин)

```bash
# Manual trigger
kubectl create job --from=cronjob/reports-generator test-report -n production

# Monitor
kubectl logs job/test-report -n production -f

# Check for file
ls -la /tmp/report_*.xlsx
```

---

## Успех Критерии

- ✅ CronJob состояние: **Active**
- ✅ Job выполнен: **Часово в 00:00**
- ✅ Excel генерируется: **На каждые сырье**
- ✅ Email отсылается: **То каждые полные часы**
- ✅ Telegram отправляется: **Файл поступает**

---

## ПОЛЕЗНЫЕ ГИТХАБ РЕСУРсы

- https://github.com/openpyxl/openpyxl (Excel работа)
- https://github.com/eternnoir/pyTelegramBotAPI (Telegram API)
- https://github.com/kubernetes/kubernetes (K8s docs)

---

## ЭКСПЕРТЫ

| Отдел | Эксперт | Тема |
|:---:|:---:|:---:|
| **PRODUCT** | Elena R. | Prioritization |
| **PRODUCT** | Dmitry P. | Test scenarios |
| **INFRA** | Sergey B. | Deployment |
| **INFRA** | Marina G. | Monitoring |

---

**Статус:** 🟢 READY FOR ASSIGNMENT
**Время на выполнение:** 📅 Четверг, 10 дек (09:00-17:00)
**Предыдущая задача:** TASK-002 (готова)
**Место принятия:** `/TASKS/TASK-003-REPORTS-GENERATOR.md`
