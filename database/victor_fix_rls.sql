-- ============================================================================
-- VICTOR BOT v2.0 - DISABLE RLS (для упрощения доступа)
-- ============================================================================
-- Выполни это в Supabase SQL Editor если видишь ошибки 401

-- Отключить RLS для всех Victor Bot таблиц
ALTER TABLE victor_inbox DISABLE ROW LEVEL SECURITY;
ALTER TABLE victor_files DISABLE ROW LEVEL SECURITY;
ALTER TABLE victor_observations DISABLE ROW LEVEL SECURITY;
ALTER TABLE victor_processing_queue DISABLE ROW LEVEL SECURITY;

-- Удалить старые политики
DROP POLICY IF EXISTS victor_inbox_policy ON victor_inbox;
DROP POLICY IF EXISTS victor_files_policy ON victor_files;
DROP POLICY IF EXISTS victor_observations_policy ON victor_observations;
DROP POLICY IF EXISTS victor_processing_queue_policy ON victor_processing_queue;

-- Создать простые политики для полного доступа
CREATE POLICY victor_inbox_allow_all ON victor_inbox FOR ALL USING (true);
CREATE POLICY victor_files_allow_all ON victor_files FOR ALL USING (true);
CREATE POLICY victor_observations_allow_all ON victor_observations FOR ALL USING (true);
CREATE POLICY victor_processing_queue_allow_all ON victor_processing_queue FOR ALL USING (true);

-- Включить RLS обратно с открытыми политиками
ALTER TABLE victor_inbox ENABLE ROW LEVEL SECURITY;
ALTER TABLE victor_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE victor_observations ENABLE ROW LEVEL SECURITY;
ALTER TABLE victor_processing_queue ENABLE ROW LEVEL SECURITY;

-- Проверка
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE tablename LIKE 'victor_%';
