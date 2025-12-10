-- ====================================================================
-- SECURE_SCHEMA_V3.sql
-- Дата: 10 декабря 2025
-- Обновление: Добавлены таблицы для RAW DATA STORAGE + BATCH ANALYZER
-- ====================================================================

-- 🔴 КРИТИЧЕСКОЕ ПРАВИЛО: НЕ УДАЛЯТЬ СУЩЕСТВУЮЩИЕ ТАБЛИЦЫ!
-- Это дополнение к текущей схеме, НЕ замена!


-- ====================================================================
-- 📦 НОВЫЕ ТАБЛИЦЫ ДЛЯ RAW DATA STORAGE
-- ====================================================================

-- 1. raw_messages - Сырые сообщения от пользователей
CREATE TABLE IF NOT EXISTS raw_messages (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    message_id BIGINT UNIQUE NOT NULL,
    chat_id BIGINT NOT NULL,
    
    -- Текстовое содержимое
    message_text TEXT,
    message_type TEXT NOT NULL, -- text, voice, document, photo, etc.
    
    -- Ответ на сообщение (reply chain)
    reply_to_message_id BIGINT,
    
    -- JSON со всеми деталями
    raw_telegram_json JSONB NOT NULL,
    
    -- Метаданные
    received_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    is_processed BOOLEAN DEFAULT FALSE,
    
    -- Индексы для быстрого поиска
    CONSTRAINT fk_reply FOREIGN KEY (reply_to_message_id) 
        REFERENCES raw_messages(message_id) ON DELETE SET NULL
);

CREATE INDEX idx_raw_messages_user ON raw_messages(user_id);
CREATE INDEX idx_raw_messages_processed ON raw_messages(is_processed, received_at);
CREATE INDEX idx_raw_messages_reply ON raw_messages(reply_to_message_id);


-- 2. bot_responses - Ответы бота
CREATE TABLE IF NOT EXISTS bot_responses (
    id BIGSERIAL PRIMARY KEY,
    
    -- Связь с исходным сообщением
    reply_to_message_id BIGINT NOT NULL,
    
    -- Текст ответа
    response_text TEXT NOT NULL,
    bot_message_id BIGINT UNIQUE,
    
    -- Связь с классификацией (если есть)
    classification_result_id BIGINT,
    
    -- Метаданные
    sent_at TIMESTAMP DEFAULT NOW(),
    is_error BOOLEAN DEFAULT FALSE,
    error_details TEXT,
    
    CONSTRAINT fk_original_message FOREIGN KEY (reply_to_message_id) 
        REFERENCES raw_messages(message_id) ON DELETE CASCADE
);

CREATE INDEX idx_bot_responses_reply ON bot_responses(reply_to_message_id);


-- 3. raw_files - Файлы от пользователей
CREATE TABLE IF NOT EXISTS raw_files (
    id BIGSERIAL PRIMARY KEY,
    
    -- Связь с сообщением
    message_id BIGINT NOT NULL,
    
    -- Telegram file info
    file_id TEXT UNIQUE NOT NULL,
    file_type TEXT NOT NULL, -- document, photo, voice, video, audio
    file_name TEXT,
    file_size BIGINT,
    mime_type TEXT,
    
    -- Загруженный контент (опционально)
    file_url TEXT,
    local_path TEXT,
    
    -- Метаданные
    uploaded_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT fk_message FOREIGN KEY (message_id) 
        REFERENCES raw_messages(message_id) ON DELETE CASCADE
);

CREATE INDEX idx_raw_files_message ON raw_files(message_id);


-- 4. message_chains - Цепочки сообщений (reply threads)
CREATE TABLE IF NOT EXISTS message_chains (
    id BIGSERIAL PRIMARY KEY,
    
    -- Корневое сообщение цепочки
    root_message_id BIGINT NOT NULL,
    
    -- Все сообщения в цепочке (упорядоченный массив ID)
    chain_message_ids BIGINT[] NOT NULL,
    
    -- Метаданные
    chain_length INT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Флаг для batch analyzer
    is_analyzed BOOLEAN DEFAULT FALSE,
    analysis_result JSONB,
    
    CONSTRAINT fk_root_message FOREIGN KEY (root_message_id) 
        REFERENCES raw_messages(message_id) ON DELETE CASCADE
);

CREATE INDEX idx_message_chains_root ON message_chains(root_message_id);
CREATE INDEX idx_message_chains_analysis ON message_chains(is_analyzed, updated_at);


-- ====================================================================
-- 📊 СУЩЕСТВУЮЩИЕ ТАБЛИЦЫ (НЕ ТРОГАТЬ!)
-- ====================================================================
-- Эти таблицы уже существуют в базе:
-- - users (из CONTACT_INTELLIGENCE_SECURE_TZ.md)
-- - classification_results (из текущей схемы)
-- Batch analyzer будет переносить данные из RAW таблиц в эти таблицы.


-- ====================================================================
-- 🔐 RLS ПОЛИТИКИ (Row Level Security)
-- ====================================================================

-- Включаем RLS на новых таблицах
ALTER TABLE raw_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE bot_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE raw_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE message_chains ENABLE ROW LEVEL SECURITY;

-- Политики доступа (service_role имеет полный доступ)
CREATE POLICY "Service role full access" ON raw_messages
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access" ON bot_responses
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access" ON raw_files
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access" ON message_chains
    FOR ALL USING (auth.role() = 'service_role');


-- ====================================================================
-- ✅ ГОТОВО!
-- ====================================================================
-- Инструкция для применения:
-- 1. Открыть Supabase Dashboard → SQL Editor
-- 2. Скопировать и вставить этот SQL
-- 3. Выполнить (Run)
-- 4. Проверить что все 4 таблицы созданы успешно
-- ====================================================================
