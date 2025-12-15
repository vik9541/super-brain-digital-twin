# 🚀 GITHUB COPILOT TASKS - SUPER BRAIN + VICTOR BOT
## Декабрь 2025 - 10 Технических Заданий

---

## ТЗ-001: FILE STORAGE & MULTI-FILE ANALYSIS

**[STORAGE] File Storage & Multi-File Analysis System**

**Context**: Victor Bot needs ability to collect multiple files from user and perform batch analysis via AI.

**Requirements**:
- File: `requirements.txt`
  - Add: `redis>=5.0.0`, `python-multipart>=0.0.6`
  
- File: `docker-compose.yml`
  - Add Redis service (image: redis:7-alpine, port: 6379)
  
- File: `api/victor_bot_router.py`
  - Function: `handle_document()` - Save file to `/tmp/uploads/{user_id}/`, store metadata in Redis with TTL 12h
  - Function: `handle_photo()` - Similar to handle_document but for images
  - Function: `handle_files_command()` - List files in user session from Redis
  - Function: `handle_analyze_command()` - Process all files via AI, save results to Supabase
  - Function: `handle_clear_command()` - Clear Redis session
  
- File: `api/file_processor.py` (NEW)
  - Function: `process_document(file_path)` - PDF/document OCR or parsing
  - Function: `process_image(file_path)` - Vision AI analysis
  - Function: `save_analysis_to_db(user_id, files, results, pool)` - Store in Supabase
  - Function: `format_analysis_results(results)` - Format for Telegram response

**Commands to Add**:
- `/add` - Instruct user to send file
- `/files` - Show files in current session
- `/analyze` - Process all files via AI
- `/clear` - Clear session

**Acceptance Criteria**:
- [ ] Redis stores files with correct structure (user:${id}:files key)
- [ ] Files persist for 12 hours with TTL
- [ ] /analyze processes all files and returns summary
- [ ] Results saved to Supabase with correct schema
- [ ] User receives formatted response in Telegram

**Estimate**: 1.5h | **Complexity**: MEDIUM | **Tokens**: ~800

---

## ТЗ-002: BATCH PROCESSING WITH CELERY

**[ASYNC] Asynchronous Task Queue for Background Processing**

**Context**: Heavy operations (OCR, AI analysis, transcription) should not block webhook responses.

**Requirements**:
- File: `requirements.txt`
  - Add: `celery>=5.3.0`, `redis>=5.0.0`
  
- File: `docker-compose.yml`
  - Add Celery worker service
  - Add Celery beat service (scheduler)
  
- File: `workers/celery_app.py` (NEW)
  - Configure Celery with Redis broker
  - Task: `transcribe_audio_task(file_id)`
  - Task: `ocr_document_task(file_id)`
  - Task: `analyze_batch_files_task(user_id, file_ids)`
  - Task: `generate_daily_report_task(user_id)`
  
- File: `workers/tasks.py` (NEW)
  - Implementation of all Celery tasks
  - Error handling with retry logic (max 3 retries)
  - Status updates to Supabase (`victor_processing_queue` table)
  
- File: `api/victor_bot_router.py`
  - Replace synchronous processing with task queue
  - Function: `enqueue_transcription(file_id)` - Trigger Celery task
  - Function: `enqueue_ocr(file_id)` - Trigger Celery task

**Acceptance Criteria**:
- [ ] Celery worker starts successfully
- [ ] Tasks execute asynchronously without blocking webhook
- [ ] Task status tracked in `victor_processing_queue` table
- [ ] Failed tasks retry with exponential backoff
- [ ] User receives notification when task completes

**Estimate**: 2.5h | **Complexity**: HIGH | **Tokens**: ~1200

---

## ТЗ-003: VECTOR DATABASE INTEGRATION

**[SEARCH] Semantic Search with pgvector**

**Context**: Enable semantic search across all user observations, notes, and documents.

**Requirements**:
- File: `requirements.txt`
  - Add: `pgvector>=0.2.0`, `openai>=1.0.0`, `sentence-transformers>=2.2.0`
  
- File: `database/migrations/003_add_pgvector.sql` (NEW)
  - Enable pgvector extension
  - Add `embedding` column (vector(1536)) to `victor_observations`
  - Create HNSW index on embeddings
  
- File: `api/embeddings.py` (NEW)
  - Function: `generate_embedding(text)` - OpenAI text-embedding-3-small
  - Function: `batch_generate_embeddings(texts)` - Batch processing
  - Function: `semantic_search(query, limit=10)` - Vector similarity search
  
- File: `api/victor_bot_router.py`
  - Command: `/search <query>` - Semantic search across all data
  - Auto-generate embeddings when saving observations
  
- File: `workers/tasks.py`
  - Task: `backfill_embeddings_task()` - Generate embeddings for existing data

**Acceptance Criteria**:
- [ ] pgvector extension enabled in Supabase
- [ ] Embeddings generated on observation create/update
- [ ] `/search` command returns semantically relevant results
- [ ] Search results ranked by cosine similarity
- [ ] Backfill task processes existing observations

**Estimate**: 2h | **Complexity**: MEDIUM | **Tokens**: ~900

---

## ТЗ-004: AI AGENTS SYSTEM

**[AI] Three Specialized AI Agents (Analyzer, Organizer, Teacher)**

**Context**: Implement intelligent agents that process user data and provide insights.

**Requirements**:
- File: `requirements.txt`
  - Add: `openai>=1.0.0`, `langchain>=0.1.0`
  
- File: `api/agents/base_agent.py` (NEW)
  - Class: `BaseAgent` - Abstract base class for agents
  - Method: `process(context)` - Main processing logic
  - Method: `get_system_prompt()` - Agent-specific system prompt
  
- File: `api/agents/analyzer_agent.py` (NEW)
  - Class: `AnalyzerAgent(BaseAgent)`
  - Analyzes observations, detects patterns, suggests insights
  - Output: JSON with patterns, trends, recommendations
  
- File: `api/agents/organizer_agent.py` (NEW)
  - Class: `OrganizerAgent(BaseAgent)`
  - Categorizes observations, creates tags, links entities
  - Output: Updated metadata, tags, entity relationships
  
- File: `api/agents/teacher_agent.py` (NEW)
  - Class: `TeacherAgent(BaseAgent)`
  - Generates educational content based on user questions
  - Output: Formatted lesson, examples, exercises
  
- File: `api/victor_bot_router.py`
  - Command: `/analyze_me` - Run AnalyzerAgent on user data
  - Command: `/organize` - Run OrganizerAgent
  - Command: `/teach <topic>` - Run TeacherAgent

**Acceptance Criteria**:
- [ ] All three agents functional and testable
- [ ] Agents access user data from Supabase
- [ ] Results formatted for Telegram display
- [ ] Agent responses cached to reduce API costs
- [ ] Error handling for OpenAI API failures

**Estimate**: 4h | **Complexity**: HIGH | **Tokens**: ~1500

---

## ТЗ-005: KNOWLEDGE GRAPH

**[GRAPH] Entity Relationship Graph with Neo4j/PostgreSQL**

**Context**: Build knowledge graph to track entities (people, places, concepts) and relationships.

**Requirements**:
- File: `requirements.txt`
  - Add: `neo4j>=5.0.0` OR use PostgreSQL with recursive queries
  
- File: `database/migrations/004_knowledge_graph.sql` (NEW)
  - Table: `entities` (id, type, name, metadata)
  - Table: `relationships` (id, source_id, target_id, type, strength)
  - Indexes on entity names and relationship types
  
- File: `api/knowledge_graph.py` (NEW)
  - Function: `extract_entities(text)` - NER using OpenAI
  - Function: `create_entity(name, type, metadata)` - Add to graph
  - Function: `create_relationship(source, target, type)` - Link entities
  - Function: `query_graph(entity_name)` - Get related entities
  - Function: `visualize_graph(user_id)` - Generate Mermaid diagram
  
- File: `api/victor_bot_router.py`
  - Auto-extract entities from observations
  - Command: `/graph` - Show user's knowledge graph
  - Command: `/connections <entity>` - Show entity relationships

**Acceptance Criteria**:
- [ ] Entities extracted from text automatically
- [ ] Relationships created and stored correctly
- [ ] `/graph` command returns visual representation
- [ ] Graph queries execute in <500ms
- [ ] Duplicate entities handled via fuzzy matching

**Estimate**: 2.5h | **Complexity**: HIGH | **Tokens**: ~1100

---

## ТЗ-006: TELEGRAM UI IMPROVEMENTS

**[UI] Interactive Telegram Interface with Inline Keyboards**

**Context**: Improve user experience with buttons, menus, and interactive elements.

**Requirements**:
- File: `api/telegram_ui.py` (NEW)
  - Function: `create_main_menu()` - Main menu with inline keyboard
  - Function: `create_file_actions_menu(file_id)` - Actions for files
  - Function: `create_pagination(items, page, callback_prefix)` - Paginated lists
  - Class: `CallbackHandler` - Handle callback_query updates
  
- File: `api/victor_bot_router.py`
  - Handle `callback_query` updates
  - Command: `/menu` - Show main interactive menu
  - Improve file listing with pagination
  - Add quick actions (👍 Сохранить, 🗑️ Удалить, 📝 Редактировать)
  
- File: `api/telegram_ui.py`
  - Function: `send_with_keyboard(chat_id, text, keyboard)` - Helper
  - Function: `edit_message_keyboard(message_id, keyboard)` - Update buttons
  - Function: `answer_callback(callback_id, text)` - Callback response

**Acceptance Criteria**:
- [ ] Main menu displays with working buttons
- [ ] Callback queries handled without errors
- [ ] Pagination works for lists >10 items
- [ ] User feedback on button press (<200ms)
- [ ] All UI elements accessible via commands

**Estimate**: 1.5h | **Complexity**: MEDIUM | **Tokens**: ~700

---

## ТЗ-007: REALTIME SYNCHRONIZATION

**[REALTIME] Supabase WebSocket Sync for Multi-Device**

**Context**: Enable real-time updates when user accesses data from multiple devices.

**Requirements**:
- File: `requirements.txt`
  - Add: `websockets>=12.0`, `realtime-py>=1.0.0`
  
- File: `api/realtime.py` (NEW)
  - Function: `setup_realtime_subscriptions(user_id)` - Subscribe to user tables
  - Function: `handle_insert(payload)` - Process new records
  - Function: `handle_update(payload)` - Process updates
  - Function: `handle_delete(payload)` - Process deletes
  - Function: `broadcast_to_telegram(user_id, event)` - Notify user via Telegram
  
- File: `api/victor_bot_router.py`
  - Initialize realtime subscriptions on startup
  - Send notifications when observations change from external source
  
- File: `docker-compose.yml`
  - Add realtime worker service (if needed)

**Acceptance Criteria**:
- [ ] WebSocket connection established to Supabase
- [ ] Changes from web app reflected in Telegram bot
- [ ] User receives notification on data change
- [ ] Reconnection logic handles network failures
- [ ] No duplicate notifications

**Estimate**: 1h | **Complexity**: MEDIUM | **Tokens**: ~600

---

## ТЗ-008: MONITORING & METRICS

**[MONITORING] Prometheus + Grafana Dashboard**

**Context**: Monitor bot performance, API usage, and database health.

**Requirements**:
- File: `requirements.txt`
  - Add: `prometheus-client>=0.19.0`, `psutil>=5.9.0`
  
- File: `api/metrics.py` (NEW)
  - Metric: `telegram_messages_total` (counter by type)
  - Metric: `api_request_duration_seconds` (histogram)
  - Metric: `database_query_duration_seconds` (histogram)
  - Metric: `active_users_total` (gauge)
  - Metric: `file_processing_errors_total` (counter)
  
- File: `api/main.py`
  - Add `/metrics` endpoint for Prometheus scraping
  - Middleware to track request duration
  
- File: `docker-compose.yml`
  - Add Prometheus service (config: prometheus.yml)
  - Add Grafana service (port: 3000)
  
- File: `monitoring/prometheus.yml` (NEW)
  - Scrape config for API metrics
  
- File: `monitoring/grafana_dashboard.json` (NEW)
  - Pre-configured dashboard for Victor Bot

**Acceptance Criteria**:
- [ ] /metrics endpoint returns Prometheus format
- [ ] Prometheus scrapes metrics every 15s
- [ ] Grafana dashboard displays key metrics
- [ ] Alerts configured for high error rates
- [ ] Retention policy set to 30 days

**Estimate**: 1.5h | **Complexity**: MEDIUM | **Tokens**: ~800

---

## ТЗ-009: SECURITY HARDENING

**[SECURITY] JWT Auth, Rate Limiting, Input Validation**

**Context**: Secure API endpoints and protect against abuse.

**Requirements**:
- File: `requirements.txt`
  - Add: `pyjwt>=2.8.0`, `slowapi>=0.1.9`, `pydantic>=2.0.0`
  
- File: `api/security.py` (NEW)
  - Function: `verify_telegram_signature(data, signature)` - Validate webhook
  - Function: `generate_jwt(user_id)` - Create access token
  - Function: `verify_jwt(token)` - Validate token
  - Class: `RateLimiter` - Token bucket algorithm
  - Function: `sanitize_input(text)` - XSS prevention
  
- File: `api/main.py`
  - Add rate limiting middleware (100 req/min per user)
  - Verify Telegram webhook signature on all updates
  
- File: `api/victor_bot_router.py`
  - Validate all user inputs with Pydantic models
  - Implement SQL injection prevention (use parameterized queries)
  - Add CSRF protection for callback queries
  
- File: `.env.example`
  - Add JWT_SECRET_KEY, TELEGRAM_WEBHOOK_SECRET

**Acceptance Criteria**:
- [ ] All webhook requests verified with signature
- [ ] Rate limiting blocks excessive requests
- [ ] SQL injection attempts blocked
- [ ] XSS attempts sanitized
- [ ] JWT tokens expire after 24h

**Estimate**: 2h | **Complexity**: MEDIUM | **Tokens**: ~900

---

## ТЗ-010: COMPREHENSIVE TESTING

**[TESTING] Unit, Integration, E2E Test Suite**

**Context**: Ensure code quality and prevent regressions.

**Requirements**:
- File: `requirements.txt`
  - Add: `pytest>=7.4.0`, `pytest-asyncio>=0.21.0`, `pytest-cov>=4.1.0`, `httpx>=0.25.0`
  
- File: `tests/conftest.py` (NEW)
  - Fixture: `db_pool` - Test database connection
  - Fixture: `redis_client` - Test Redis instance
  - Fixture: `mock_telegram` - Mock Telegram API
  
- File: `tests/unit/test_file_processor.py` (NEW)
  - Test: `test_process_document()` - Document processing
  - Test: `test_process_image()` - Image analysis
  - Test: `test_save_analysis()` - Database save
  
- File: `tests/integration/test_webhook.py` (NEW)
  - Test: `test_receive_text_message()` - Full webhook flow
  - Test: `test_receive_document()` - File handling
  - Test: `test_command_execution()` - Command processing
  
- File: `tests/e2e/test_user_journey.py` (NEW)
  - Test: `test_complete_analysis_flow()` - Upload → Analyze → Results
  
- File: `.github/workflows/test.yml` (NEW)
  - Run tests on every PR
  - Generate coverage report
  - Fail if coverage <80%

**Acceptance Criteria**:
- [ ] All tests pass locally and in CI
- [ ] Code coverage ≥80%
- [ ] E2E tests cover critical user journeys
- [ ] Tests run in <60 seconds
- [ ] Mock external APIs (Telegram, OpenAI)

**Estimate**: 2h | **Complexity**: MEDIUM | **Tokens**: ~1000

---

## 📊 РЕАЛИЗАЦИЯ ROADMAP

### ФАЗА 1 (Основа) - Неделя 1
1. ✅ **ТЗ-001** - File Storage (основа данных)
2. ✅ **ТЗ-009** - Security (критично для продакшна)
3. ✅ **ТЗ-003** - Vector DB (поиск)

### ФАЗА 2 (Ядро) - Неделя 2
4. ✅ **ТЗ-004** - AI Agents (интеллект системы)
5. ✅ **ТЗ-005** - Knowledge Graph (связи данных)

### ФАЗА 3 (Масштабируемость) - Неделя 3
6. ✅ **ТЗ-002** - Batch Processing (производительность)
7. ✅ **ТЗ-008** - Monitoring (наблюдаемость)

### ФАЗА 4 (Полировка) - Неделя 4
8. ✅ **ТЗ-010** - Testing (качество кода)
9. ✅ **ТЗ-006** - Telegram UI (UX улучшения)
10. ✅ **ТЗ-007** - Realtime (синхронизация)

---

## 🎯 КАК ИСПОЛЬЗОВАТЬ С GITHUB COPILOT

### В VS Code:
```
1. Открой этот файл: docs/TASKS.md
2. Нажми: Ctrl+I (Windows) или Cmd+I (Mac)
3. Введи команду:

@workspace Реализуй ТЗ-001: File Storage & Multi-File Analysis

4. Copilot сгенерирует весь необходимый код!
```

### Через GitHub Issues:
```
1. Создай Issue в репозитории
2. Скопируй текст ТЗ в описание
3. Добавь label: copilot
4. Copilot предложит решение автоматически
```

### Быстрые команды:
```bash
# Реализовать конкретное ТЗ
@workspace implement TZ-001

# Написать тесты для ТЗ
@workspace write tests for TZ-001

# Создать миграцию БД
@workspace create migration for TZ-003

# Добавить документацию
@workspace add docstrings for TZ-004
```

---

## 📝 МЕТРИКИ УСПЕХА

| ТЗ | Функционал | Метрика успеха |
|---|---|---|
| 001 | File Storage | >90% файлов успешно обработано |
| 002 | Batch Processing | Задачи выполняются <5 сек |
| 003 | Vector Search | Релевантность >85% |
| 004 | AI Agents | Точность анализа >80% |
| 005 | Knowledge Graph | >1000 сущностей извлечено |
| 006 | Telegram UI | Время отклика <200ms |
| 007 | Realtime | Задержка синхронизации <1s |
| 008 | Monitoring | Uptime >99.5% |
| 009 | Security | 0 критических уязвимостей |
| 010 | Testing | Покрытие кода >80% |

---

**Версия**: 1.0  
**Дата создания**: 15 декабря 2025  
**Автор**: Victor AI System  
**Лицензия**: MIT
