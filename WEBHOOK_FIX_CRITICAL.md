# КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Webhook 500 Error

## Дата: 14 декабря 2025, 20:25

## Проблема
Telegram webhook не работал из-за **500 Internal Server Error** при обработке сообщений.

## Корневая причина
```python
# ❌ БЫЛО (НЕПРАВИЛЬНО):
async def get_db_pool():
    return await asyncpg.create_pool(DATABASE_URL)

# В webhook handler:
pool = await get_db_pool()  # Создавал НОВЫЙ pool каждый раз
try:
    # ...обработка...
finally:
    await pool.close()  # Закрывал pool после каждого запроса
```

**Проблемы:**
1. **Создание нового pool при каждом запросе** - медленно и неэффективно
2. **Закрытие pool в finally** - приводило к ошибкам соединения
3. **Отсутствие настроек для Supabase pooler** - pgbouncer требует `jit: off`

## Исправление
```python
# ✅ СТАЛО (ПРАВИЛЬНО):
_db_pool: Optional[asyncpg.Pool] = None

async def get_db_pool():
    global _db_pool
    
    if _db_pool is None:
        _db_pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=1,
            max_size=5,
            server_settings={'jit': 'off'}  # Required for pgbouncer
        )
        logger.info("✅ Database pool created")
    
    return _db_pool

# В webhook handler:
pool = await get_db_pool()  # Получает СУЩЕСТВУЮЩИЙ pool
try:
    # ...обработка...
except Exception as e:
    # ...обработка ошибок...
# НЕТ finally с pool.close()! Pool живет всё время работы приложения
```

## Что изменилось
1. ✅ Глобальный singleton DB pool (создается один раз при первом запросе)
2. ✅ Настройки для Supabase pooler: `server_settings={'jit': 'off'}`
3. ✅ Пул-менеджмент: `min_size=1, max_size=5`
4. ✅ Убрали `pool.close()` из webhook handler

## Deployment
- **Commit:** 803d505 "Fix DB pool: create global pool, add Supabase pooler settings"
- **Файл:** `api/victor_bot_router.py`
- **Push:** ✅ Успешно (force-with-lease)
- **GitHub Actions:** Building новый образ...
- **После билда:** Pod автоматически перезапустится с новым образом

## Проверка после деплоя
```bash
# 1. Дождаться билда
kubectl get pods -w

# 2. Отправить /start боту @astra_VIK_bot

# 3. Проверить логи
kubectl logs deployment/victor-bot-v2 --tail=20

# Ожидаем увидеть:
# ✅ Database pool created
# 📥 Received update: ..., message_id: ...
# INFO: ... - "POST /api/telegram/webhook HTTP/1.1" 200 OK
```

## Важно
- **Правильный бот:** @astra_VIK_bot (не @LavrentevViktor_bot!)
- **Token:** 8457627946:AAEKY...
- **Chat ID:** 1743141472

---

**Status:** 🔄 Waiting for GitHub Actions build completion
**Next:** Test webhook with new deployment
