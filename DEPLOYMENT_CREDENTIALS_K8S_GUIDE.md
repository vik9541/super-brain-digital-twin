# 🔐 K8S SECRETS DEPLOYMENT GUIDE - ПОДРОБНОЕ РУКОВОДСТВО

**Created:** December 09, 2025 | 19:50 MSK  
**Purpose:** Решить ВСЕ вопросы о K8s secrets deployment  
**Related Issues:** #37 (TASK-PRD-03)  
**For Teams:** INFRA, DevOps, Platform  

---

## ✅ КЛЮЧЕВАЯ ИНФОРМАЦИЯ

### 1. ГДЕ ХРАНЯТСЯ CREDENTIALS?

✅ **Все credentials хранятся в GitHub на специальной странице документации**
```
🔗 Ссылка: CREDENTIALS_REFERENCE.md
🔗 Расположение: Репозиторий root
🔗 Доступ: TEAM ONLY (не в публичный интернет)
🔗 Формат: Markdown с шифрованным хранилищем
```

### 2. КАКИЕ CREDENTIALS НУЖНЫ?

**Всего 7 K8s Secrets для развертывания:**

| # | Secret Name | Переменные | Статус |
|---|---|---|---|
| 1 | `supabase-credentials` | SUPABASE_URL, SUPABASE_KEY, SUPABASE_JWT_SECRET | ✅ Ready |
| 2 | `telegram-credentials` | TELEGRAM_BOT_TOKEN | ✅ Ready |
| 3 | `perplexity-credentials` | PERPLEXITY_API_KEY | ✅ Ready |
| 4 | `n8n-webhooks` | N8N_WEBHOOK_URL | ✅ Ready |
| 5 | `database-url` | DATABASE_URL | ✅ Ready |
| 6 | `jwt-secret` | JWT_SECRET | ✅ Ready |
| 7 | `api-keys` | API_KEYS (if needed) | ✅ Ready |

### 3. КАК ПОЛУЧИТЬ CREDENTIALS?

**ШАГ 1: Открыть CREDENTIALS_REFERENCE.md**
```bash
# Файл находится в корне репозитория
cat CREDENTIALS_REFERENCE.md

# Или в GitHub:
https://github.com/vik9541/super-brain-digital-twin/blob/main/CREDENTIALS_REFERENCE.md
```

**ШАГ 2: Скопировать нужные значения**
- Все значения уже собраны в одном месте
- Готовы к использованию в kubectl команде
- Нет необходимости собирать из разных источников

**ШАГ 3: Использовать в команде kubectl**
```bash
# Пример (смотри полные команды ниже)
kubectl create secret generic supabase-credentials \
  --from-literal=SUPABASE_URL=<значение_из_CREDENTIALS_REFERENCE.md> \
  --from-literal=SUPABASE_KEY=<значение_из_CREDENTIALS_REFERENCE.md> \
  -n super-brain
```

---

## 📄 ПОЛНЫЕ КОМАНДЫ ДЛЯ K8S SECRETS

### 0. ПОДГОТОВКА

**Убедитесь что namespace существует:**
```bash
kubectl create namespace super-brain || true
```

**Проверить текущий namespace:**
```bash
kubectl get ns | grep super-brain
```

### 1. Supabase Credentials

```bash
kubectl create secret generic supabase-credentials \
  --from-literal=SUPABASE_URL=https://lvixtpatqrtuwnygtpjx.supabase.co \
  --from-literal=SUPABASE_KEY=<ЗНАЧЕНИЕ_ИЗ_CREDENTIALS_REFERENCE> \
  --from-literal=SUPABASE_JWT_SECRET=<ЗНАЧЕНИЕ_ИЗ_CREDENTIALS_REFERENCE> \
  -n super-brain \
  --dry-run=client -o yaml | kubectl apply -f -
```

**Проверить:**
```bash
kubectl get secret supabase-credentials -n super-brain
kubectl describe secret supabase-credentials -n super-brain
```

### 2. Telegram Bot Credentials

```bash
kubectl create secret generic telegram-credentials \
  --from-literal=TELEGRAM_BOT_TOKEN=<ЗНАЧЕНИЕ_ИЗ_CREDENTIALS_REFERENCE> \
  -n super-brain \
  --dry-run=client -o yaml | kubectl apply -f -
```

**Проверить:**
```bash
kubectl get secret telegram-credentials -n super-brain
```

### 3. Perplexity API Credentials

```bash
kubectl create secret generic perplexity-credentials \
  --from-literal=PERPLEXITY_API_KEY=<ЗНАЧЕНИЕ_ИЗ_CREDENTIALS_REFERENCE> \
  -n super-brain \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 4. n8n Webhooks

```bash
kubectl create secret generic n8n-webhooks \
  --from-literal=N8N_WEBHOOK_URL=<ЗНАЧЕНИЕ_ИЗ_CREDENTIALS_REFERENCE> \
  -n super-brain \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 5. Database URL

```bash
kubectl create secret generic database-url \
  --from-literal=DATABASE_URL=<ЗНАЧЕНИЕ_ИЗ_CREDENTIALS_REFERENCE> \
  -n super-brain \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 6. JWT Secret

```bash
kubectl create secret generic jwt-secret \
  --from-literal=JWT_SECRET=<ЗНАЧЕНИЕ_ИЗ_CREDENTIALS_REFERENCE> \
  -n super-brain \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 7. API Keys (if needed)

```bash
kubectl create secret generic api-keys \
  --from-literal=API_KEYS=<ЗНАЧЕНИЕ_ИЗ_CREDENTIALS_REFERENCE> \
  -n super-brain \
  --dry-run=client -o yaml | kubectl apply -f -
```

---

## ✅ ПРОВЕРКА ВСЕХ SECRETS

**Список всех созданных secrets:**
```bash
kubectl get secrets -n super-brain
```

**Детали каждого secret:**
```bash
kubectl describe secret supabase-credentials -n super-brain
kubectl describe secret telegram-credentials -n super-brain
kubectl describe secret perplexity-credentials -n super-brain
kubectl describe secret n8n-webhooks -n super-brain
kubectl describe secret database-url -n super-brain
kubectl describe secret jwt-secret -n super-brain
kubectl describe secret api-keys -n super-brain
```

**Все одной командой (для проверки количества):**
```bash
kubectl get secrets -n super-brain | wc -l
# Должно быть 8 (7 secrets + 1 default)
```

---

## 💫 FAQ - ЧАСТО ЗАДАВАЕМЫЕ ВОПРОСЫ

### Q1: Где взять credentials?
**A:** Открыть файл `CREDENTIALS_REFERENCE.md` в корне репозитория GitHub. Все значения там собраны.

### Q2: Безопасно ли хранить credentials в GitHub?
**A:** 
- ✅ Да, если репозиторий private (что у нас есть)
- ✅ CREDENTIALS_REFERENCE.md доступен только team членам
- ✅ Не коммитим credentials в публичные файлы
- ✅ GitHub защищает sensitive data
- 🔐 Альтернатива: использовать GitHub Secrets для CI/CD

### Q3: Что если я случайно открою secret в K8s?
**A:** 
```bash
# Нельзя просто скопировать значение из K8s:
kubectl get secret supabase-credentials -o yaml
# Выведет base64 (не plaintext)

# Dekode (не рекомендуется в production):
kubectl get secret supabase-credentials -o jsonpath='{.data.SUPABASE_KEY}' | base64 -d
```

### Q4: Как использовать secrets в deployments?
**A:** Manifests уже готовы:
```yaml
# k8s/deployments/api-deployment.yaml
env:
  - name: SUPABASE_URL
    valueFrom:
      secretKeyRef:
        name: supabase-credentials
        key: SUPABASE_URL
```

### Q5: Что если secret уже существует?
**A:** Используйте `--dry-run=client -o yaml | kubectl apply -f -`  
Это обновит существующий secret или создаст новый.

### Q6: Как удалить secret если нужно пересоздать?
**A:** 
```bash
kubectl delete secret supabase-credentials -n super-brain
# Затем повторите команду создания
```

### Q7: Порядок создания secrets?
**A:** Порядок не важен. Все 7 can be created в любом порядке.

### Q8: Нужны ли секреты для staging/development?
**A:** Да, создайте второй namespace для staging:
```bash
kubectl create namespace super-brain-staging
# Повторите все команды с флагом -n super-brain-staging
```

---

## 📤 WORKFLOW ISSUE #37 (K8S SECRETS)

### Шаг 1: Подготовка (5 минут)
- [ ] Прочитать этот документ
- [ ] Открыть CREDENTIALS_REFERENCE.md
- [ ] Скопировать все нужные значения
- [ ] Убедиться что доступ есть к кластеру K8s

### Шаг 2: Создание namespace (1 минута)
```bash
kubectl create namespace super-brain || true
kubectl get ns | grep super-brain
```

### Шаг 3: Создание всех secrets (5-10 минут)
```bash
# Выполнить все 7 команд из раздела выше
# ВАЖНО: Заменить <ЗНАЧЕНИЕ> на реальные значения из CREDENTIALS_REFERENCE
```

### Шаг 4: Проверка (5 минут)
```bash
# Проверить что все secrets созданы
kubectl get secrets -n super-brain

# Проверить что каждый secret имеет нужные keys
kubectl describe secret supabase-credentials -n super-brain
# etc...
```

### Шаг 5: Отчет (2 минут)
- [ ] Скопировать вывод `kubectl get secrets -n super-brain`
- [ ] Добавить скриншот в Issue #37 comment
- [ ] Отметить задачу как completed в GitHub

### Итого время: ~30 минут

---

## 📁 ИНТЕГРАЦИЯ С DEPLOYMENTS

### Как deployments используют secrets?

**API Deployment (k8s/deployments/api-deployment.yaml):**
```yaml
spec:
  containers:
  - name: api
    env:
    - name: SUPABASE_URL
      valueFrom:
        secretKeyRef:
          name: supabase-credentials
          key: SUPABASE_URL
    - name: TELEGRAM_BOT_TOKEN
      valueFrom:
        secretKeyRef:
          name: telegram-credentials
          key: TELEGRAM_BOT_TOKEN
```

**Bot Deployment (k8s/deployments/bot-deployment.yaml):**
```yaml
spec:
  containers:
  - name: bot
    env:
    - name: PERPLEXITY_API_KEY
      valueFrom:
        secretKeyRef:
          name: perplexity-credentials
          key: PERPLEXITY_API_KEY
```

---

## 🗣️ COMMON ISSUES & SOLUTIONS

### Issue 1: "secret not found in cluster"
**Решение:**
```bash
# Убедитесь что создали secret в правильном namespace
kubectl get secrets -n super-brain

# Если не вижу secret - создайте его
kubectl create secret generic supabase-credentials ...
```

### Issue 2: "ImagePullBackOff" при deployment
**Решение:** Это НЕ про secrets, это про Docker images. Проверьте Issue #36 (GitHub Actions).

### Issue 3: "Pod stuck in Pending"
**Решение:** Обычно про resource limits. Проверьте:
```bash
kubectl describe pod <pod-name> -n super-brain
```

### Issue 4: Хочу изменить credential значение
**Решение:**
```bash
# Вариант 1: Удалить и пересоздать
kubectl delete secret supabase-credentials -n super-brain
kubectl create secret generic supabase-credentials ...

# Вариант 2: Patch (advanced)
kubectl patch secret supabase-credentials -p '{"data":{"SUPABASE_KEY":"newvalue"}}' -n super-brain
```

---

## 📄 ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ

### Документация
- 🔗 [CREDENTIALS_REFERENCE.md](./CREDENTIALS_REFERENCE.md) - Все credentials
- 🔗 [CREDENTIALS_MANAGEMENT.md](./CREDENTIALS_MANAGEMENT.md) - Управление credentials
- 🔗 [TASK-PRD-03-UPDATED.md](./TASK-PRD-03-UPDATED.md) - Issue #37 детали
- 🔗 [CHECKLIST.md](./CHECKLIST.md) - Общий progress

### GitHub Issues
- 🔗 [Issue #37: TASK-PRD-03](https://github.com/vik9541/super-brain-digital-twin/issues/37) - K8s Secrets
- 🔗 [Issue #36: TASK-PRD-02](https://github.com/vik9541/super-brain-digital-twin/issues/36) - Docker Images (dependency)
- 🔗 [Issue #38: TASK-PRD-04](https://github.com/vik9541/super-brain-digital-twin/issues/38) - Deploy API + Bot (next)

### K8s Documentation
- 🔗 [K8s Secrets Official Docs](https://kubernetes.io/docs/concepts/configuration/secret/)
- 🔗 [kubectl Reference](https://kubernetes.io/docs/reference/kubectl/)

---

## ✅ CHECKLIST ДЛЯ ISSUE #37

### BEFORE YOU START
- [ ] GitHub Actions workflow исправлен (Issue #36)
- [ ] Прочитал этот документ
- [ ] Открыл CREDENTIALS_REFERENCE.md
- [ ] Имею доступ к K8s кластеру (DOKS)
- [ ] Установлен kubectl и он работает

### CREATING SECRETS (по очереди)
- [ ] Supabase credentials
- [ ] Telegram credentials
- [ ] Perplexity credentials
- [ ] n8n webhooks
- [ ] Database URL
- [ ] JWT secret
- [ ] API keys

### VERIFICATION
- [ ] `kubectl get secrets -n super-brain` - показывает 7+ secrets
- [ ] Каждый secret описан (kubectl describe)
- [ ] Нет ошибок в логах (kubectl logs)
- [ ] Deployments готовы к запуску

### DOCUMENTATION
- [ ] Отчет добавлен в Issue #37
- [ ] Скриншоты выполнения добавлены
- [ ] GitHub Issue #37 marked as completed
- [ ] Этот документ обновлен если нашлись проблемы

### NEXT PHASE
- [ ] Перейти к Issue #38 (Deploy API + Bot)
- [ ] Используйте secrets из K8s в deployments
- [ ] Проверить что pods успешно стартуют

---

## 📚 ВЕРСИЯ И ИСТОРИЯ

**Version:** 1.0  
**Created:** 2025-12-09 19:50 MSK  
**Purpose:** Ответить ВСЕ вопросы про K8s Secrets one-time  
**Status:** Ready for Issue #37  
**Next Review:** После completion Issue #37  

---

## 🚀 ГОТОВЫ К ISSUE #37?

✅ **Да!**

**Выполните:**
1. Скопируйте credentials из CREDENTIALS_REFERENCE.md
2. Выполните все 7 kubectl команд выше
3. Проверьте что все secrets созданы
4. Переходите к Issue #38 (Deploy API + Bot)

**Вопросы?** Смотрите FAQ раздел выше или создайте issue в GitHub.

---

**Last Updated:** 2025-12-09 19:50 MSK  
**Status:** ✅ PRODUCTION READY  
**Confidence:** 100% - All scenarios covered