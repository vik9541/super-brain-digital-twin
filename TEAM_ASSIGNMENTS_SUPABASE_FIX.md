# 📋 ТЗ ДЛЯ КОМАНД: SUPABASE CLARIFICATION & PRODUCTION SECRETS

**Версия:** 1.0  
**Дата:** 8 декабря 2025, 20:55 MSK  
**Статус:** 🔴 КРИТИЧНО - ТРЕБУЕТ НЕМЕДЛЕННОГО ВЫПОЛНЕНИЯ  
**Дедлайн:** 9 декабря 2025, 14:00 MSK  

---

## 🎯 ПРОБЛЕМА И РЕШЕНИЕ

### Что произошло:
- ❌ В документации указан несуществующий Project ID: `hbdrmgtcvlwjcecptfxd`
- ❌ Есть путаница между двумя Supabase проектами
- ❌ Production Secrets не добавлены в GitHub
- ❌ Deployment заблокирован

### Решение:
- ✅ Четко разделить два проекта Supabase
- ✅ Обновить всю документацию
- ✅ Добавить правильные Secrets в GitHub
- ✅ Запустить Production Deployment

---

## 📊 СТРУКТУРА SUPABASE PROJECTS

| Название | ID | Назначение | Регион | Статус |
|:---|:---|:---|:---|:---|
| **Knowledge_DBnanoAWS** | `lvixtpatqrtuwnygtpjx` | 🟢 **PRODUCTION Super Brain v4.0** | eu-central-1 | ✅ ACTIVE |
| **internetMagazinmicroAWS** | `bvspfvshgpidpbhkvykb` | 🟡 STAGING (97k.ru) | eu-west-1 | ⚠️ SEPARATE |
| **DEPRECATED** | `hbdrmgtcvlwjcecptfxd` | 🔴 НЕ СУЩЕСТВУЕТ | - | ❌ DELETE |

---

## 👨‍💼 ЗАДАЧИ ПО КОМАНДАМ

### INFRA TEAM 🏗️

#### TASK-INFRA-001: Обновить CREDENTIALS/.env.example

**Что сделать:**
1. Открыть файл: `CREDENTIALS/.env.example`
2. Найти строку:
   ```bash
   SUPABASE_URL=https://hbdrmgtcvlwjcecptfxd.supabase.co
   ```
3. Заменить на:
   ```bash
   SUPABASE_URL=https://lvixtpatqrtuwnygtpjx.supabase.co
   SUPABASE_DB_HOST=db.lvixtpatqrtuwnygtpjx.supabase.co
   ```
4. Сохранить и commit'ить

**File:** `CREDENTIALS/.env.example`  
**Priority:** 🔴 CRITICAL  
**Assignee:** @devops-team  
**Estimation:** 15 min  

---

#### TASK-INFRA-002: Обновить CREDENTIALS_MANAGEMENT.md

**Что сделать:**
1. Найти в документе:
   ```bash
   # Перейти: https://app.supabase.com/project/hbdrmgtcvlwjcecptfxd/settings/api
   ```
2. Заменить на:
   ```bash
   # Перейти: https://app.supabase.com/project/lvixtpatqrtuwnygtpjx/settings/api
   ```
3. Добавить комментарий:
   ```
   # Production: Knowledge_DBnanoAWS (lvixtpatqrtuwnygtpjx, eu-central-1)
   # Staging: internetMagazinmicroAWS (bvspfvshgpidpbhkvykb, eu-west-1)
   ```
4. Сохранить и commit'ить

**File:** `CREDENTIALS_MANAGEMENT.md`  
**Priority:** 🔴 CRITICAL  
**Assignee:** @devops-team  
**Estimation:** 20 min  

---

#### TASK-INFRA-003: Обновить MASTER_README.md

**Что сделать:**
1. Открыть файл: `MASTER_README.md`
2. Добавить в конец раздела про Supabase:
   ```markdown
   ## ✅ SUPABASE PROJECTS CLARITY

   ### 🟢 PRODUCTION (Super Brain v4.0)
   - **Project ID:** `lvixtpatqrtuwnygtpjx`
   - **URL:** https://lvixtpatqrtuwnygtpjx.supabase.co
   - **Settings/API:** https://app.supabase.com/project/lvixtpatqrtuwnygtpjx/settings/api
   - **Region:** eu-central-1
   - **Name:** Knowledge_DBnanoAWS

   ### 🟡 STAGING (97k.ru)
   - **Project ID:** `bvspfvshgpidpbhkvykb`
   - **URL:** https://bvspfvshgpidpbhkvykb.supabase.co
   - **Region:** eu-west-1
   - **Name:** internetMagazinmicroAWS

   ### ❌ DEPRECATED (DO NOT USE)
   - **Project ID:** `hbdrmgtcvlwjcecptfxd`
   - **Status:** НЕ СУЩЕСТВУЕТ
   - **Action:** Удалена из всей документации
   ```
3. Сохранить и commit'ить

**File:** `MASTER_README.md`  
**Priority:** 🔴 CRITICAL  
**Assignee:** @devops-team  
**Estimation:** 15 min  

---

### PRODUCT/SECURITY TEAM 🔐

#### TASK-PRODUCT-001: Получить SUPABASE_SERVICE_ROLE_KEY

**Что сделать:**
1. Открыть Supabase Dashboard:
   ```
   https://app.supabase.com/project/lvixtpatqrtuwnygtpjx/settings/api
   ```
2. Найти **Service Role Key** (не ANON KEY!)
3. Нажать **"Show"** если скрыто
4. Нажать кнопку **Copy** (скопировать в буфер обмена)
5. Передать значение безопасно (НЕ в GitHub, НЕ в чате!)

**Ожидаемое значение:** Строка начинающаяся с `eyJ...` (JWT token)

**Priority:** 🔴 CRITICAL  
**Assignee:** @security-team  
**Estimation:** 10 min  

---

#### TASK-PRODUCT-002: Добавить GitHub Production Secrets

**Что сделать:**

1. Перейти в GitHub Repository Settings:
   ```
   https://github.com/vik9541/super-brain-digital-twin/settings/environments
   ```

2. Выбрать **production** environment

3. Нажать **"Add environment secret"** и добавить ВСЕ 7 secrets:

   ```bash
   # 1. KUBECONFIG_PROD (base64 encoded)
   Name: KUBECONFIG_PROD
   Value: <содержимое /tmp/KUBECONFIG_PROD.txt закодированное в base64>
   
   # 2. SUPABASE_URL (Production)
   Name: SUPABASE_URL
   Value: https://lvixtpatqrtuwnygtpjx.supabase.co
   
   # 3. SUPABASE_ANON_KEY
   Name: SUPABASE_ANON_KEY
   Value: sb_publishable_XuGBRG6gYskYpeoFAWRshw_LaQyHtP9
   
   # 4. SUPABASE_SERVICE_ROLE_KEY (из TASK-PRODUCT-001)
   Name: SUPABASE_SERVICE_ROLE_KEY
   Value: <значение из Knowledge_DBnanoAWS>
   
   # 5. TELEGRAM_BOT_TOKEN
   Name: TELEGRAM_BOT_TOKEN
   Value: <токен от BotFather для @astra_VIK_bot>
   
   # 6. DO_REGISTRY_USERNAME
   Name: DO_REGISTRY_USERNAME
   Value: vik9541@bk.ru
   
   # 7. DO_REGISTRY_TOKEN
   Name: DO_REGISTRY_TOKEN
   Value: <токен из DigitalOcean API>
   ```

4. **ВАЖНО:** Убедитесь что вводите в **production environment**, а не в репозиторий!

5. Каждый secret сохраняйте нажатием кнопки **"Add secret"**

**Checklist:**
- [ ] KUBECONFIG_PROD добавлен
- [ ] SUPABASE_URL = https://lvixtpatqrtuwnygtpjx.supabase.co
- [ ] SUPABASE_ANON_KEY добавлен
- [ ] SUPABASE_SERVICE_ROLE_KEY добавлен (из Production Knowledge_DB!)
- [ ] TELEGRAM_BOT_TOKEN добавлен
- [ ] DO_REGISTRY_USERNAME добавлен
- [ ] DO_REGISTRY_TOKEN добавлен

**Priority:** 🔴 CRITICAL  
**Assignee:** @security-team  
**Estimation:** 30 min  
**After completion:** 👉 Notify @devops-team for deployment

---

### DEVOPS TEAM 🚀

#### TASK-DEVOPS-001: Trigger Production Deployment

**Когда начать:**
- После того как INFRA TEAM завершил TASK-INFRA-001, TASK-INFRA-002, TASK-INFRA-003
- После того как PRODUCT TEAM завершил TASK-PRODUCT-002

**Что сделать:**
1. Убедиться что все 7 secrets добавлены в GitHub production environment
2. Проверить что документация обновлена
3. Trigger GitHub Actions workflow:
   ```
   https://github.com/vik9541/super-brain-digital-twin/actions/workflows/deploy-with-secrets.yml
   ```
   Нажать **"Run workflow"** на ветке **main**

4. Ждать completion (примерно 5-10 минут)
5. Проверить статус:
   ```bash
   kubectl get all -n production
   kubectl logs -n production -l app=api --tail=100
   ```

6. Проверить endpoints:
   ```bash
   curl https://97v.ru/health
   curl https://97v.ru/
   ```

**Expected result:**
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "timestamp": "2025-12-09T..."
}
```

**Priority:** 🔴 CRITICAL  
**Assignee:** @devops-team  
**Estimation:** 15 min (после других задач)  
**After completion:** 👉 Notify everyone that Production is LIVE

---

#### TASK-DEVOPS-002: Verify Production is Healthy

**Что сделать:**
1. ✅ Проверить Health Check:
   ```bash
   curl https://97v.ru/health
   ```
   Должен вернуть `{"status": "healthy", ...}`

2. ✅ Проверить API Info:
   ```bash
   curl https://97v.ru/
   ```
   Должен вернуть информацию о API v3.0.0

3. ✅ Проверить Supabase connection:
   ```bash
   kubectl logs -n production -l app=api | grep -i supabase | tail -20
   ```
   Не должно быть ошибок подключения

4. ✅ Проверить Telegram Bot:
   ```bash
   curl -X POST https://t.me/astra_VIK_bot -d "test"
   ```
   Бот должен быть доступен

5. ✅ Проверить Database connection:
   ```bash
   kubectl exec -it -n production $(kubectl get pod -n production -l app=api -o jsonpath='{.items[0].metadata.name}') -- psql -h db.lvixtpatqrtuwnygtpjx.supabase.co -U postgres -d postgres -c "SELECT 1;"
   ```

**Priority:** 🟡 HIGH  
**Assignee:** @devops-team  
**Estimation:** 20 min  
**After completion:** 👉 Report results in Issue #38

---

## 📅 TIMELINE

```
9 Dec 2025
├─ 08:00 MSK: INFRA TEAM starts (3 tasks, ~50 min total)
├─ 09:00 MSK: PRODUCT TEAM starts (2 tasks, ~40 min total)
├─ 10:00 MSK: All tasks should be done
├─ 10:30 MSK: DEVOPS TEAM triggers deployment
├─ 10:45 MSK: DEVOPS TEAM verifies health
└─ 11:00 MSK: 🎉 PRODUCTION LIVE!
```

**DEADLINE: 14:00 MSK (end of business day)**

---

## ✅ FINAL CHECKLIST

### INFRA Team
- [ ] TASK-INFRA-001: CREDENTIALS/.env.example updated
- [ ] TASK-INFRA-002: CREDENTIALS_MANAGEMENT.md updated
- [ ] TASK-INFRA-003: MASTER_README.md updated
- [ ] All files committed and pushed
- [ ] 👉 Notify PRODUCT & DEVOPS teams

### PRODUCT/Security Team
- [ ] TASK-PRODUCT-001: SERVICE_ROLE_KEY obtained from Knowledge_DBnanoAWS
- [ ] TASK-PRODUCT-002: All 7 secrets added to GitHub production environment
- [ ] Verified that SUPABASE_URL points to lvixtpatqrtuwnygtpjx (NOT bvspfvshgpidpbhkvykb!)
- [ ] Verified that SERVICE_ROLE_KEY is from Knowledge_DBnanoAWS
- [ ] 👉 Notify DEVOPS team

### DEVOPS Team
- [ ] TASK-DEVOPS-001: Deployment triggered via GitHub Actions
- [ ] Deployment completed successfully
- [ ] TASK-DEVOPS-002: All health checks passed
- [ ] 👉 Report status in Issue #38

---

## 🚨 CRITICAL REMINDERS

⚠️ **НИКОГДА не добавляйте:**
- ❌ Ключи из `internetMagazinmicroAWS` (bvspfvshgpidpbhkvykb) в production!
- ❌ Ссылки на `hbdrmgtcvlwjcecptfxd` (несуществующий проект)!
- ❌ Secrets в GitHub commits (только в environment secrets!)!

✅ **ВСЕГДА используйте:**
- ✅ Project ID: `lvixtpatqrtuwnygtpjx` для production Super Brain
- ✅ URL: `https://lvixtpatqrtuwnygtpjx.supabase.co` для production
- ✅ GitHub environment: **production** (НЕ repository secrets!)

---

## 📞 CONTACTS & ESCALATION

**Issues:** GitHub Issue #38 - https://github.com/vik9541/super-brain-digital-twin/issues/38

**Team Leads:**
- INFRA Team: @devops-team
- PRODUCT Team: @security-team  
- DEVOPS Team: @devops-lead

**Escalation:** If blocked on any task, ping @vik9541 immediately

---

**Version:** 1.0  
**Status:** 🔴 ACTIVE - REQUIRES IMMEDIATE ACTION  
**Last Updated:** 8 December 2025, 20:55 MSK  
**Author:** Perplexity AI Research Agent  

---

## Ссылки для команд

1. **GitHub Repository**: https://github.com/vik9541/super-brain-digital-twin
2. **Issue #38 (Main)**: https://github.com/vik9541/super-brain-digital-twin/issues/38
3. **GitHub Environments**: https://github.com/vik9541/super-brain-digital-twin/settings/environments
4. **GitHub Actions**: https://github.com/vik9541/super-brain-digital-twin/actions
5. **Production Supabase**: https://app.supabase.com/project/lvixtpatqrtuwnygtpjx/
6. **Staging Supabase**: https://app.supabase.com/project/bvspfvshgpidpbhkvykb/

---

🎯 **LET'S GO PRODUCTION!** 🚀