-- 📦 SUPABASE TESTING SCHEMA
-- Testing infrastructure and result tracking
-- Created: Dec 8, 2025

-- ============================================================================
-- 1. CREATE TEST RESULTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.test_results (
  id BIGSERIAL PRIMARY KEY,
  
  -- 📎 Test Identification
  test_id UUID NOT NULL DEFAULT gen_random_uuid(),
  test_name TEXT NOT NULL,
  test_category TEXT NOT NULL CHECK (test_category IN (
    'Infrastructure', 'API', 'Database', 'Services', 'Integration', 
    'Performance', 'Security', 'Documentation'
  )),
  test_type TEXT NOT NULL CHECK (test_type IN (
    'Unit', 'Integration', 'E2E', 'Performance', 'Security', 'Manual'
  )),
  description TEXT,
  
  -- ⏱️ Execution Timing
  started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMP WITH TIME ZONE,
  duration_milliseconds BIGINT,
  
  -- ✅❌ Results
  status TEXT NOT NULL CHECK (status IN ('passed', 'failed', 'skipped', 'pending', 'error')),
  success_count INT DEFAULT 0,
  failure_count INT DEFAULT 0,
  error_message TEXT,
  error_stack_trace TEXT,
  
  -- 🌟 Metrics
  response_time_ms DECIMAL(10, 2),
  memory_used_mb DECIMAL(10, 2),
  cpu_used_percent DECIMAL(5, 2),
  network_latency_ms DECIMAL(10, 2),
  database_query_time_ms DECIMAL(10, 2),
  
  -- 💫 Environment
  environment TEXT NOT NULL CHECK (environment IN ('development', 'staging', 'production')),
  region TEXT,
  kubernetes_version TEXT,
  postgres_version TEXT,
  supabase_version TEXT,
  api_version TEXT,
  node_name TEXT,
  pod_name TEXT,
  
  -- 📌 Assertions
  assertions_total INT DEFAULT 0,
  assertions_passed INT DEFAULT 0,
  assertions_failed INT DEFAULT 0,
  
  -- 🗒️ Metadata
  test_data JSONB,
  tags JSONB DEFAULT '[]'::jsonb,
  notes TEXT,
  created_by TEXT NOT NULL DEFAULT 'system',
  updated_by TEXT,
  
  -- 📄 Timestamps
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  
  -- 🔐 Security
  is_sensitive BOOLEAN DEFAULT FALSE,
  requires_review BOOLEAN DEFAULT FALSE
);

-- Create indexes for fast querying
CREATE INDEX IF NOT EXISTS idx_test_results_status ON public.test_results(status);
CREATE INDEX IF NOT EXISTS idx_test_results_category ON public.test_results(test_category);
CREATE INDEX IF NOT EXISTS idx_test_results_type ON public.test_results(test_type);
CREATE INDEX IF NOT EXISTS idx_test_results_created_at ON public.test_results(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_test_results_environment ON public.test_results(environment);
CREATE INDEX IF NOT EXISTS idx_test_results_test_id ON public.test_results(test_id);

-- Enable RLS
ALTER TABLE public.test_results ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 2. CREATE TEST RUNS TABLE (Session tracking)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.test_runs (
  id BIGSERIAL PRIMARY KEY,
  
  -- 🌟 Session Info
  run_id UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,
  run_name TEXT NOT NULL,
  description TEXT,
  
  -- ⏱️ Timing
  started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMP WITH TIME ZONE,
  duration_seconds DECIMAL,
  
  -- 🌟 Status
  status TEXT NOT NULL CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
  
  -- 💫 Environment
  environment TEXT NOT NULL,
  region TEXT,
  
  -- 📃 Results Summary
  total_tests INT DEFAULT 0,
  passed_tests INT DEFAULT 0,
  failed_tests INT DEFAULT 0,
  skipped_tests INT DEFAULT 0,
  
  -- 📊 Statistics
  pass_rate_percent DECIMAL(5, 2),
  avg_response_time_ms DECIMAL(10, 2),
  max_response_time_ms DECIMAL(10, 2),
  min_response_time_ms DECIMAL(10, 2),
  
  -- 🗒️ Metadata
  triggered_by TEXT NOT NULL,
  trigger_reason TEXT,
  notes TEXT,
  
  -- 📄 Timestamps
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_test_runs_run_id ON public.test_runs(run_id);
CREATE INDEX IF NOT EXISTS idx_test_runs_status ON public.test_runs(status);
CREATE INDEX IF NOT EXISTS idx_test_runs_created_at ON public.test_runs(created_at DESC);

ALTER TABLE public.test_runs ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 3. CREATE TEST SCENARIOS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.test_scenarios (
  id BIGSERIAL PRIMARY KEY,
  
  -- 🌟 Scenario Info
  scenario_id UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,
  scenario_name TEXT NOT NULL UNIQUE,
  description TEXT,
  
  -- 📃 Test Coverage
  test_categories TEXT[] DEFAULT ARRAY[]::TEXT[],
  test_count INT DEFAULT 0,
  
  -- 📄 Configuration
  is_active BOOLEAN DEFAULT TRUE,
  is_scheduled BOOLEAN DEFAULT FALSE,
  schedule_cron TEXT,
  
  -- 🗒️ Configuration
  config JSONB DEFAULT '{}'::jsonb,
  test_data_sample JSONB,
  
  -- 📄 Timestamps
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  created_by TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_test_scenarios_name ON public.test_scenarios(scenario_name);
CREATE INDEX IF NOT EXISTS idx_test_scenarios_active ON public.test_scenarios(is_active);

ALTER TABLE public.test_scenarios ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 4. CREATE TEST METRICS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.test_metrics (
  id BIGSERIAL PRIMARY KEY,
  
  -- 💫 Metric Info
  metric_name TEXT NOT NULL,
  metric_type TEXT NOT NULL CHECK (metric_type IN (
    'response_time', 'cpu', 'memory', 'disk', 'network', 'database',
    'error_rate', 'success_rate', 'throughput', 'custom'
  )),
  
  -- 🗒️ Value & Unit
  metric_value DECIMAL(15, 4),
  unit TEXT,
  threshold_warning DECIMAL(15, 4),
  threshold_critical DECIMAL(15, 4),
  
  -- 🌟 Related Test
  test_result_id BIGINT REFERENCES public.test_results(id) ON DELETE CASCADE,
  test_run_id BIGINT REFERENCES public.test_runs(id) ON DELETE CASCADE,
  
  -- 💫 Environment
  environment TEXT,
  
  -- 📄 Timestamps
  recorded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_test_metrics_test_result ON public.test_metrics(test_result_id);
CREATE INDEX IF NOT EXISTS idx_test_metrics_test_run ON public.test_metrics(test_run_id);
CREATE INDEX IF NOT EXISTS idx_test_metrics_recorded_at ON public.test_metrics(recorded_at DESC);

ALTER TABLE public.test_metrics ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 5. CREATE ALERTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.test_alerts (
  id BIGSERIAL PRIMARY KEY,
  
  -- 📢 Alert Info
  alert_id UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,
  alert_type TEXT NOT NULL CHECK (alert_type IN (
    'test_failed', 'performance_degradation', 'error_rate_high',
    'timeout', 'resource_exhausted', 'configuration_error'
  )),
  severity TEXT NOT NULL CHECK (severity IN ('info', 'warning', 'error', 'critical')),
  
  -- 🗒️ Message & Details
  message TEXT NOT NULL,
  description TEXT,
  
  -- 🌟 Related Test
  test_result_id BIGINT REFERENCES public.test_results(id) ON DELETE SET NULL,
  test_run_id BIGINT REFERENCES public.test_runs(id) ON DELETE SET NULL,
  
  -- ✅❌ Status
  is_resolved BOOLEAN DEFAULT FALSE,
  resolved_at TIMESTAMP WITH TIME ZONE,
  resolution_notes TEXT,
  
  -- 📄 Timestamps
  triggered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_test_alerts_severity ON public.test_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_test_alerts_resolved ON public.test_alerts(is_resolved);
CREATE INDEX IF NOT EXISTS idx_test_alerts_created_at ON public.test_alerts(created_at DESC);

ALTER TABLE public.test_alerts ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 6. VIEWS FOR REPORTING
-- ============================================================================

-- 📋 View: Test Results Summary
CREATE OR REPLACE VIEW public.v_test_summary AS
SELECT 
  DATE(tr.created_at) as test_date,
  tr.test_category,
  tr.environment,
  COUNT(*) as total_tests,
  SUM(CASE WHEN tr.status = 'passed' THEN 1 ELSE 0 END) as passed_count,
  SUM(CASE WHEN tr.status = 'failed' THEN 1 ELSE 0 END) as failed_count,
  SUM(CASE WHEN tr.status = 'skipped' THEN 1 ELSE 0 END) as skipped_count,
  ROUND(100.0 * SUM(CASE WHEN tr.status = 'passed' THEN 1 ELSE 0 END) / COUNT(*), 2) as pass_rate_percent,
  ROUND(AVG(tr.response_time_ms), 2) as avg_response_time_ms,
  MAX(tr.response_time_ms) as max_response_time_ms,
  MIN(tr.response_time_ms) as min_response_time_ms
FROM public.test_results tr
GROUP BY DATE(tr.created_at), tr.test_category, tr.environment;

-- 📋 View: Recent Failed Tests
CREATE OR REPLACE VIEW public.v_failed_tests AS
SELECT 
  tr.id,
  tr.test_name,
  tr.test_category,
  tr.error_message,
  tr.created_at,
  EXTRACT(EPOCH FROM (NOW() - tr.created_at)) / 3600 as hours_ago
FROM public.test_results tr
WHERE tr.status = 'failed'
ORDER BY tr.created_at DESC
LIMIT 100;

-- 📋 View: Performance Trends
CREATE OR REPLACE VIEW public.v_performance_trends AS
SELECT 
  DATE(tr.created_at) as test_date,
  tr.test_category,
  ROUND(AVG(tr.response_time_ms), 2) as avg_response_time_ms,
  ROUND(AVG(tr.memory_used_mb), 2) as avg_memory_mb,
  ROUND(AVG(tr.cpu_used_percent), 2) as avg_cpu_percent,
  COUNT(*) as test_count
FROM public.test_results tr
WHERE tr.status = 'passed'
GROUP BY DATE(tr.created_at), tr.test_category
ORDER BY test_date DESC, test_category;

-- 📋 View: Health Dashboard
CREATE OR REPLACE VIEW public.v_health_dashboard AS
SELECT 
  tr.environment,
  COUNT(*) as total_tests_24h,
  SUM(CASE WHEN tr.status = 'passed' THEN 1 ELSE 0 END) as passed_24h,
  SUM(CASE WHEN tr.status = 'failed' THEN 1 ELSE 0 END) as failed_24h,
  ROUND(100.0 * SUM(CASE WHEN tr.status = 'passed' THEN 1 ELSE 0 END) / COUNT(*), 2) as health_percent,
  COUNT(DISTINCT ta.alert_id) as active_alerts
FROM public.test_results tr
LEFT JOIN public.test_alerts ta ON tr.id = ta.test_result_id AND ta.is_resolved = FALSE
WHERE tr.created_at > NOW() - INTERVAL '24 hours'
GROUP BY tr.environment;

-- ============================================================================
-- 7. FUNCTIONS FOR TEST OPERATIONS
-- ============================================================================

-- 📘 Function: Log Test Result
CREATE OR REPLACE FUNCTION public.fn_log_test_result(
  p_test_name TEXT,
  p_test_category TEXT,
  p_test_type TEXT,
  p_status TEXT,
  p_environment TEXT,
  p_response_time_ms DECIMAL DEFAULT NULL,
  p_error_message TEXT DEFAULT NULL,
  p_test_data JSONB DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
  v_test_id UUID;
BEGIN
  INSERT INTO public.test_results (
    test_name, test_category, test_type, status, environment,
    response_time_ms, error_message, test_data, created_by
  ) VALUES (
    p_test_name, p_test_category, p_test_type, p_status, p_environment,
    p_response_time_ms, p_error_message, p_test_data, current_user
  )
  RETURNING test_id INTO v_test_id;
  
  -- Auto-trigger alert if failed
  IF p_status = 'failed' THEN
    INSERT INTO public.test_alerts (
      alert_type, severity, message, test_result_id
    ) VALUES (
      'test_failed', 'error', p_test_name || ' failed: ' || COALESCE(p_error_message, 'Unknown error'),
      (SELECT id FROM public.test_results WHERE test_id = v_test_id)
    );
  END IF;
  
  RETURN v_test_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 📘 Function: Create Test Run
CREATE OR REPLACE FUNCTION public.fn_create_test_run(
  p_run_name TEXT,
  p_environment TEXT,
  p_triggered_by TEXT
) RETURNS UUID AS $$
DECLARE
  v_run_id UUID;
BEGIN
  INSERT INTO public.test_runs (
    run_name, environment, triggered_by, status
  ) VALUES (
    p_run_name, p_environment, p_triggered_by, 'running'
  )
  RETURNING run_id INTO v_run_id;
  
  RETURN v_run_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 📘 Function: Complete Test Run
CREATE OR REPLACE FUNCTION public.fn_complete_test_run(
  p_run_id UUID
) RETURNS VOID AS $$
DECLARE
  v_total INT;
  v_passed INT;
  v_failed INT;
  v_avg_time DECIMAL;
BEGIN
  -- Calculate statistics
  SELECT 
    COUNT(*),
    SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END),
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END),
    AVG(response_time_ms)
  INTO v_total, v_passed, v_failed, v_avg_time
  FROM public.test_results
  WHERE test_run_id = (SELECT id FROM public.test_runs WHERE run_id = p_run_id);
  
  -- Update test run
  UPDATE public.test_runs
  SET 
    status = 'completed',
    completed_at = NOW(),
    duration_seconds = EXTRACT(EPOCH FROM (NOW() - started_at)),
    total_tests = v_total,
    passed_tests = v_passed,
    failed_tests = v_failed,
    pass_rate_percent = CASE WHEN v_total > 0 THEN ROUND(100.0 * v_passed / v_total, 2) ELSE 0 END,
    avg_response_time_ms = v_avg_time
  WHERE run_id = p_run_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- 8. SAMPLE DATA FOR TESTING
-- ============================================================================

-- Insert sample test scenario
INSERT INTO public.test_scenarios (scenario_name, description, test_count, is_active, created_by)
VALUES (
  'Daily Health Check',
  'Complete daily health check of all services',
  15,
  TRUE,
  'system'
)
ON CONFLICT DO NOTHING;

INSERT INTO public.test_scenarios (scenario_name, description, test_count, is_active, created_by)
VALUES (
  'Performance Baseline',
  'Establish and monitor performance baseline',
  8,
  TRUE,
  'system'
)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 9. SECURITY POLICIES
-- ============================================================================

-- RLS Policy: Test Results (allow read for authenticated users)
CREATE POLICY "Allow read for authenticated users" ON public.test_results
  FOR SELECT TO authenticated
  USING (TRUE);

-- RLS Policy: Test Results (allow insert for testing service)
CREATE POLICY "Allow insert for testing service" ON public.test_results
  FOR INSERT TO authenticated
  WITH CHECK (created_by = current_user OR created_by = 'testing-suite');

-- RLS Policy: Test Alerts (allow read for authenticated users)
CREATE POLICY "Allow read test alerts" ON public.test_alerts
  FOR SELECT TO authenticated
  USING (TRUE);

-- ============================================================================
-- 10. GRANTS & PERMISSIONS
-- ============================================================================

-- Grant execute on functions
GRANT EXECUTE ON FUNCTION public.fn_log_test_result TO authenticated;
GRANT EXECUTE ON FUNCTION public.fn_create_test_run TO authenticated;
GRANT EXECUTE ON FUNCTION public.fn_complete_test_run TO authenticated;

-- Grant view access
GRANT SELECT ON public.v_test_summary TO authenticated;
GRANT SELECT ON public.v_failed_tests TO authenticated;
GRANT SELECT ON public.v_performance_trends TO authenticated;
GRANT SELECT ON public.v_health_dashboard TO authenticated;

-- ============================================================================
-- DONE! ✅
-- ============================================================================

/*
🎆 TESTING SCHEMA SUCCESSFULLY CREATED!

Available:
✅ test_results table
✅ test_runs table
✅ test_scenarios table
✅ test_metrics table
✅ test_alerts table
✅ 4 reporting views
✅ 3 automation functions
✅ Row Level Security
✅ Indexes for performance

 Next: Run TESTING.md commands to execute tests!
*/
