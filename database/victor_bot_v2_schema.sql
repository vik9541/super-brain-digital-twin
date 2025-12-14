-- ============================================================================
-- VICTOR BOT v2.0 - UNIVERSAL SENSOR DATABASE SCHEMA
-- Version: 2.0.0
-- Date: 14 декабря 2025
-- Purpose: Универсальный приём данных от Виктора через Telegram
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- 1. VICTOR_INBOX - Главное хранилище входящих данных
-- ============================================================================
CREATE TABLE IF NOT EXISTS victor_inbox (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL DEFAULT 'victor-system',
  
  -- Контент
  content_type TEXT NOT NULL CHECK (content_type IN (
    'text', 'file', 'contact', 'location', 'link', 'unknown'
  )),
  content TEXT, -- для текста
  file_id UUID, -- reference to victor_files
  
  -- Контекст Telegram
  telegram_message_id BIGINT UNIQUE,
  telegram_chat_id BIGINT,
  timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  user_question TEXT, -- "Что это?", "Описи"
  
  -- Обработка
  is_processed BOOLEAN NOT NULL DEFAULT FALSE,
  processing_status TEXT NOT NULL DEFAULT 'raw' CHECK (processing_status IN (
    'raw', 'pending_clarification', 'processing', 'done', 'failed'
  )),
  assigned_agent TEXT, -- "PRIMARY_ANALYZER", "ORGANIZER", etc.
  
  -- Результат обработки
  linked_observation_id UUID, -- reference to victor_observations
  linked_file_id UUID, -- reference to victor_files
  linked_contact_id BIGINT,
  linked_project_id BIGINT,
  
  -- Метаданные
  metadata JSONB DEFAULT '{}',
  error_message TEXT,
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_victor_inbox_user_id ON victor_inbox(user_id);
CREATE INDEX IF NOT EXISTS idx_victor_inbox_content_type ON victor_inbox(content_type);
CREATE INDEX IF NOT EXISTS idx_victor_inbox_processing_status ON victor_inbox(processing_status);
CREATE INDEX IF NOT EXISTS idx_victor_inbox_timestamp ON victor_inbox(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_victor_inbox_telegram_message_id ON victor_inbox(telegram_message_id);
CREATE INDEX IF NOT EXISTS idx_victor_inbox_is_processed ON victor_inbox(is_processed) WHERE is_processed = FALSE;

-- ============================================================================
-- 2. VICTOR_FILES - Хранение всех файлов
-- ============================================================================
CREATE TABLE IF NOT EXISTS victor_files (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL DEFAULT 'victor-system',
  
  -- Файл
  original_file_name TEXT NOT NULL,
  file_type TEXT NOT NULL, -- "image/jpeg", "application/pdf", "video/mp4"
  file_size BIGINT NOT NULL, -- bytes
  file_url TEXT NOT NULL, -- S3/Supabase Storage URL
  file_path TEXT NOT NULL, -- /files/2025-12/victor-file-123.jpg
  
  -- Telegram metadata
  telegram_file_id TEXT, -- Telegram file_id
  telegram_file_unique_id TEXT UNIQUE,
  
  -- Категория (если определена)
  category TEXT, -- "receipt", "contract", "photo_person", "voice_memo", "document"
  user_description TEXT, -- Что пишет пользователь
  
  -- Обработка
  processing_queue TEXT, -- "pending_ocr", "pending_transcription", "pending_analysis"
  is_processed BOOLEAN NOT NULL DEFAULT FALSE,
  extracted_data JSONB, -- результат OCR/речи/анализа
  
  -- Метаданные файла
  metadata JSONB DEFAULT '{}', -- {width, height, duration, encoding}
  tags TEXT[] DEFAULT '{}',
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_victor_files_user_id ON victor_files(user_id);
CREATE INDEX IF NOT EXISTS idx_victor_files_category ON victor_files(category);
CREATE INDEX IF NOT EXISTS idx_victor_files_processing_queue ON victor_files(processing_queue);
CREATE INDEX IF NOT EXISTS idx_victor_files_is_processed ON victor_files(is_processed) WHERE is_processed = FALSE;
CREATE INDEX IF NOT EXISTS idx_victor_files_created_at ON victor_files(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_victor_files_file_type ON victor_files(file_type);
CREATE INDEX IF NOT EXISTS idx_victor_files_telegram_file_unique_id ON victor_files(telegram_file_unique_id);

-- ============================================================================
-- 3. VICTOR_OBSERVATIONS - Обработанные наблюдения
-- ============================================================================
CREATE TABLE IF NOT EXISTS victor_observations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL DEFAULT 'victor-system',
  
  -- Содержание
  type TEXT NOT NULL CHECK (type IN (
    'meeting', 'task', 'idea', 'note', 'decision', 'expense', 
    'location', 'contact_interaction', 'phone_call', 'email'
  )),
  content TEXT NOT NULL,
  
  -- Контекст
  timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
  location JSONB, -- {latitude, longitude, address}
  related_contacts BIGINT[] DEFAULT '{}',
  related_files UUID[] DEFAULT '{}',
  related_projects BIGINT[] DEFAULT '{}',
  
  -- Обработка AI
  ai_processed BOOLEAN NOT NULL DEFAULT FALSE,
  ai_summary TEXT,
  ai_actions JSONB, -- [{action, priority, assignee, due_date}]
  sentiment TEXT CHECK (sentiment IN ('positive', 'neutral', 'negative')),
  confidence_score DECIMAL(3, 2), -- 0.00 - 1.00
  tags TEXT[] DEFAULT '{}',
  
  -- Метаданные
  source TEXT NOT NULL DEFAULT 'telegram' CHECK (source IN (
    'telegram', 'icloud', 'email', 'whatsapp', 'manual', 'api'
  )),
  source_inbox_id UUID, -- reference к victor_inbox
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_victor_observations_user_id ON victor_observations(user_id);
CREATE INDEX IF NOT EXISTS idx_victor_observations_type ON victor_observations(type);
CREATE INDEX IF NOT EXISTS idx_victor_observations_ai_processed ON victor_observations(ai_processed) WHERE ai_processed = FALSE;
CREATE INDEX IF NOT EXISTS idx_victor_observations_timestamp ON victor_observations(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_victor_observations_sentiment ON victor_observations(sentiment);
CREATE INDEX IF NOT EXISTS idx_victor_observations_source ON victor_observations(source);
CREATE INDEX IF NOT EXISTS idx_victor_observations_tags ON victor_observations USING GIN(tags);

-- ============================================================================
-- 4. VICTOR_PROCESSING_QUEUE - Очередь фоновой обработки
-- ============================================================================
CREATE TABLE IF NOT EXISTS victor_processing_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL DEFAULT 'victor-system',
  
  -- Задача
  inbox_id UUID, -- reference to victor_inbox
  file_id UUID, -- reference to victor_files
  
  -- Тип обработки
  processing_type TEXT NOT NULL CHECK (processing_type IN (
    'ocr_russian', 'ocr_english', 'ocr_chinese', 
    'transcribe_audio', 'transcribe_voice',
    'identify_face', 'extract_table', 'analyze_image',
    'sentiment_analysis', 'entity_extraction', 'summarization'
  )),
  priority INT NOT NULL DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
  
  -- Статус
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
    'pending', 'processing', 'done', 'failed', 'cancelled'
  )),
  retry_count INT NOT NULL DEFAULT 0,
  max_retries INT NOT NULL DEFAULT 3,
  
  -- Результаты
  result JSONB, -- {text, confidence, data, entities, summary}
  error_message TEXT,
  error_stack_trace TEXT,
  
  -- Время
  started_at TIMESTAMP WITH TIME ZONE,
  completed_at TIMESTAMP WITH TIME ZONE,
  duration_ms BIGINT,
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_victor_processing_queue_user_id ON victor_processing_queue(user_id);
CREATE INDEX IF NOT EXISTS idx_victor_processing_queue_processing_type ON victor_processing_queue(processing_type);
CREATE INDEX IF NOT EXISTS idx_victor_processing_queue_status ON victor_processing_queue(status);
CREATE INDEX IF NOT EXISTS idx_victor_processing_queue_priority ON victor_processing_queue(priority DESC);
CREATE INDEX IF NOT EXISTS idx_victor_processing_queue_pending ON victor_processing_queue(priority DESC, created_at ASC) 
  WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_victor_processing_queue_file_id ON victor_processing_queue(file_id);
CREATE INDEX IF NOT EXISTS idx_victor_processing_queue_inbox_id ON victor_processing_queue(inbox_id);

-- ============================================================================
-- 5. FOREIGN KEY CONSTRAINTS
-- ============================================================================

-- victor_inbox → victor_files
ALTER TABLE victor_inbox 
  DROP CONSTRAINT IF EXISTS fk_victor_inbox_file_id;
ALTER TABLE victor_inbox 
  ADD CONSTRAINT fk_victor_inbox_file_id 
  FOREIGN KEY (file_id) REFERENCES victor_files(id) ON DELETE SET NULL;

-- victor_inbox → victor_observations
ALTER TABLE victor_inbox 
  DROP CONSTRAINT IF EXISTS fk_victor_inbox_observation_id;
ALTER TABLE victor_inbox 
  ADD CONSTRAINT fk_victor_inbox_observation_id 
  FOREIGN KEY (linked_observation_id) REFERENCES victor_observations(id) ON DELETE SET NULL;

-- victor_observations → victor_inbox
ALTER TABLE victor_observations 
  DROP CONSTRAINT IF EXISTS fk_victor_observations_inbox_id;
ALTER TABLE victor_observations 
  ADD CONSTRAINT fk_victor_observations_inbox_id 
  FOREIGN KEY (source_inbox_id) REFERENCES victor_inbox(id) ON DELETE SET NULL;

-- victor_processing_queue → victor_inbox
ALTER TABLE victor_processing_queue 
  DROP CONSTRAINT IF EXISTS fk_victor_processing_queue_inbox_id;
ALTER TABLE victor_processing_queue 
  ADD CONSTRAINT fk_victor_processing_queue_inbox_id 
  FOREIGN KEY (inbox_id) REFERENCES victor_inbox(id) ON DELETE CASCADE;

-- victor_processing_queue → victor_files
ALTER TABLE victor_processing_queue 
  DROP CONSTRAINT IF EXISTS fk_victor_processing_queue_file_id;
ALTER TABLE victor_processing_queue 
  ADD CONSTRAINT fk_victor_processing_queue_file_id 
  FOREIGN KEY (file_id) REFERENCES victor_files(id) ON DELETE CASCADE;

-- ============================================================================
-- 6. FUNCTIONS & TRIGGERS
-- ============================================================================

-- Функция обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггеры для автоматического обновления updated_at
DROP TRIGGER IF EXISTS tr_victor_inbox_updated_at ON victor_inbox;
CREATE TRIGGER tr_victor_inbox_updated_at
  BEFORE UPDATE ON victor_inbox
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS tr_victor_files_updated_at ON victor_files;
CREATE TRIGGER tr_victor_files_updated_at
  BEFORE UPDATE ON victor_files
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS tr_victor_observations_updated_at ON victor_observations;
CREATE TRIGGER tr_victor_observations_updated_at
  BEFORE UPDATE ON victor_observations
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS tr_victor_processing_queue_updated_at ON victor_processing_queue;
CREATE TRIGGER tr_victor_processing_queue_updated_at
  BEFORE UPDATE ON victor_processing_queue
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 7. ROW LEVEL SECURITY (опционально)
-- ============================================================================

-- Включить RLS для всех таблиц
ALTER TABLE victor_inbox ENABLE ROW LEVEL SECURITY;
ALTER TABLE victor_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE victor_observations ENABLE ROW LEVEL SECURITY;
ALTER TABLE victor_processing_queue ENABLE ROW LEVEL SECURITY;

-- Политики доступа (все данные доступны только для victor-system)
CREATE POLICY victor_inbox_policy ON victor_inbox
  FOR ALL
  USING (user_id = current_setting('app.current_user_id', true));

CREATE POLICY victor_files_policy ON victor_files
  FOR ALL
  USING (user_id = current_setting('app.current_user_id', true));

CREATE POLICY victor_observations_policy ON victor_observations
  FOR ALL
  USING (user_id = current_setting('app.current_user_id', true));

CREATE POLICY victor_processing_queue_policy ON victor_processing_queue
  FOR ALL
  USING (user_id = current_setting('app.current_user_id', true));

-- ============================================================================
-- 8. VIEWS ДЛЯ АНАЛИТИКИ
-- ============================================================================

-- Сводка по inbox статусам
CREATE OR REPLACE VIEW victor_inbox_summary AS
SELECT 
  processing_status,
  content_type,
  COUNT(*) as count,
  COUNT(*) FILTER (WHERE is_processed = TRUE) as processed_count,
  COUNT(*) FILTER (WHERE is_processed = FALSE) as pending_count,
  MIN(created_at) as oldest_item,
  MAX(created_at) as newest_item
FROM victor_inbox
GROUP BY processing_status, content_type
ORDER BY processing_status, content_type;

-- Сводка по очереди обработки
CREATE OR REPLACE VIEW victor_queue_summary AS
SELECT 
  processing_type,
  status,
  priority,
  COUNT(*) as count,
  AVG(duration_ms) as avg_duration_ms,
  MAX(retry_count) as max_retries,
  MIN(created_at) as oldest_task,
  MAX(created_at) as newest_task
FROM victor_processing_queue
GROUP BY processing_type, status, priority
ORDER BY priority DESC, processing_type;

-- Сводка по файлам
CREATE OR REPLACE VIEW victor_files_summary AS
SELECT 
  category,
  file_type,
  processing_queue,
  COUNT(*) as count,
  SUM(file_size) as total_size_bytes,
  AVG(file_size) as avg_size_bytes,
  COUNT(*) FILTER (WHERE is_processed = TRUE) as processed_count,
  COUNT(*) FILTER (WHERE is_processed = FALSE) as pending_count
FROM victor_files
GROUP BY category, file_type, processing_queue
ORDER BY count DESC;

-- ============================================================================
-- 9. SAMPLE DATA (для тестирования)
-- ============================================================================

-- Пример текстового наблюдения
INSERT INTO victor_observations (type, content, timestamp, source)
VALUES (
  'meeting',
  'Встреча с Петровым по проекту MOS-001. Обсудили бюджет 5 млн руб.',
  NOW(),
  'telegram'
) ON CONFLICT DO NOTHING;

-- Пример inbox записи
INSERT INTO victor_inbox (
  content_type, 
  content, 
  processing_status, 
  telegram_message_id,
  telegram_chat_id
)
VALUES (
  'text',
  'Тестовое сообщение от Виктора',
  'raw',
  123456789,
  987654321
) ON CONFLICT (telegram_message_id) DO NOTHING;

-- ============================================================================
-- SCHEMA DEPLOYMENT COMPLETE ✅
-- ============================================================================

-- Verification queries
SELECT 'victor_inbox' as table_name, COUNT(*) as row_count FROM victor_inbox
UNION ALL
SELECT 'victor_files', COUNT(*) FROM victor_files
UNION ALL
SELECT 'victor_observations', COUNT(*) FROM victor_observations
UNION ALL
SELECT 'victor_processing_queue', COUNT(*) FROM victor_processing_queue
ORDER BY table_name;

-- Summary
DO $$
BEGIN
  RAISE NOTICE '✅ Victor Bot v2.0 Schema Deployed Successfully';
  RAISE NOTICE '📦 Tables created: victor_inbox, victor_files, victor_observations, victor_processing_queue';
  RAISE NOTICE '🔗 Foreign keys configured';
  RAISE NOTICE '⚡ Indexes optimized';
  RAISE NOTICE '🔒 RLS policies enabled';
  RAISE NOTICE '📊 Analytics views created';
END $$;
