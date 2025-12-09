#!/usr/bin/env python3
"""
🧪 AUTOMATED TESTING SUITE
Complete test execution and result tracking

Usage:
  python3 run_tests.py --all
  python3 run_tests.py --infrastructure
  python3 run_tests.py --api
  python3 run_tests.py --database
  python3 run_tests.py --services

ℹ️ SUPABASE PROJECT: Knowledge_DBnanoAWS (lvixtpatqrtuwhygtpjx) - 97v.ru
ℹ️ For more info: See SUPABASE_PROJECTS_CLARITY.md
"""

import os
import json
import time
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import argparse
import logging
from pathlib import Path

try:
    import requests
    from supabase import create_client, Client
except ImportError:
    print("❌ Missing dependencies. Run: pip install -r requirements.test.txt")
    sys.exit(1)

# ============================================================================
# CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ✅ CORRECT Supabase Project: Knowledge_DBnanoAWS (lvixtpatqrtuwhygtpjx)
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://lvixtpatqrtuwhygtpjx.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
API_URL = os.getenv('API_URL', 'http://97v.ru')
API_TOKEN = os.getenv('API_TOKEN')

# ============================================================================
# ENUMS
# ============================================================================

class TestStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

class TestCategory(Enum):
    INFRASTRUCTURE = "Infrastructure"
    API = "API"
    DATABASE = "Database"
    SERVICES = "Services"
    INTEGRATION = "Integration"

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class TestResult:
    test_name: str
    test_category: str
    test_type: str
    status: str
    environment: str = "production"
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    test_data: Optional[Dict] = None
    assertions_passed: int = 0
    assertions_total: int = 0
    memory_used_mb: Optional[float] = None
    cpu_used_percent: Optional[float] = None
    kubernetes_version: Optional[str] = None
    api_version: Optional[str] = None
    created_by: str = "automated-testing-suite"
    started_at: datetime = None
    completed_at: datetime = None
    
    def __post_init__(self):
        if self.started_at is None:
            self.started_at = datetime.now()
        if self.completed_at is None:
            self.completed_at = datetime.now()

# ============================================================================
# TEST SUITE
# ============================================================================

class TestSuite:
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.results: List[TestResult] = []
        self.run_id: Optional[str] = None
        self._initialize_supabase()
    
    def _initialize_supabase(self):
        """Initialize Supabase connection"""
        try:
            if SUPABASE_URL and SUPABASE_KEY:
                self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                logger.info("✅ Supabase connected (Project: lvixtpatqrtuwhygtpjx)")
            else:
                logger.warning("⚠️ Supabase credentials not found")
        except Exception as e:
            logger.error(f"❌ Supabase connection failed: {e}")
    
    def create_test_run(self, run_name: str):
        """Create new test run session"""
        try:
            if not self.supabase:
                return
            
            response = self.supabase.rpc(
                'fn_create_test_run',
                {
                    'p_run_name': run_name,
                    'p_environment': 'production',
                    'p_triggered_by': 'CLI'
                }
            ).execute()
            
            self.run_id = response.data
            logger.info(f"🌟 Test run created: {self.run_id}")
        except Exception as e:
            logger.error(f"❌ Failed to create test run: {e}")
    
    def log_test_result(self, result: TestResult) -> bool:
        """Log test result to Supabase"""
        try:
            if not self.supabase:
                logger.warning("⚠️ Skipping Supabase logging (not connected)")
                return True
            
            result_dict = asdict(result)
            result_dict['started_at'] = result.started_at.isoformat()
            result_dict['completed_at'] = result.completed_at.isoformat()
            result_dict['duration_milliseconds'] = int(
                (result.completed_at - result.started_at).total_seconds() * 1000
            )
            
            response = self.supabase.table('test_results').insert(result_dict).execute()
            self.results.append(result)
            
            status_emoji = "✅" if result.status == "passed" else "❌"
            logger.info(f"{status_emoji} {result.test_name}: {result.status.upper()}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Failed to log test result: {e}")
            return False
    
    # ========================================================================
    # INFRASTRUCTURE TESTS
    # ========================================================================
    
    def test_kubernetes_health(self) -> TestResult:
        """Test Kubernetes cluster health"""
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                ['kubectl', 'get', 'pods', '-A'],
                capture_output=True,
                timeout=10
            )
            
            success = result.returncode == 0 and b'Running' in result.stdout
            
            return TestResult(
                test_name="Kubernetes Pod Status",
                test_category="Infrastructure",
                test_type="Integration",
                status="passed" if success else "failed",
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                error_message=result.stderr.decode() if result.returncode != 0 else None,
                test_data={"command": "kubectl get pods -A"},
                completed_at=datetime.now()
            )
        except Exception as e:
            return TestResult(
                test_name="Kubernetes Pod Status",
                test_category="Infrastructure",
                test_type="Integration",
                status="error",
                error_message=str(e),
                completed_at=datetime.now()
            )
    
    def test_api_health(self) -> TestResult:
        """Test API health endpoint"""
        start_time = datetime.now()
        
        try:
            response = requests.get(
                f"{API_URL}/health",
                timeout=5
            )
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            success = response.status_code == 200
            
            return TestResult(
                test_name="API Health Check",
                test_category="API",
                test_type="Unit",
                status="passed" if success else "failed",
                response_time_ms=response_time,
                error_message=f"Status: {response.status_code}" if not success else None,
                test_data={"url": f"{API_URL}/health", "status_code": response.status_code},
                assertions_passed=1 if success else 0,
                assertions_total=1,
                completed_at=datetime.now()
            )
        except Exception as e:
            return TestResult(
                test_name="API Health Check",
                test_category="API",
                test_type="Unit",
                status="error",
                error_message=str(e),
                completed_at=datetime.now()
            )
    
    def test_dns_resolution(self) -> TestResult:
        """Test DNS resolution for domain"""
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                ['nslookup', '97v.ru', '8.8.8.8'],
                capture_output=True,
                timeout=5
            )
            
            success = result.returncode == 0 and b'138.197.254.53' in result.stdout
            
            return TestResult(
                test_name="DNS Resolution (97v.ru)",
                test_category="Infrastructure",
                test_type="Integration",
                status="passed" if success else "failed",
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                error_message="Failed to resolve or wrong IP" if not success else None,
                test_data={"domain": "97v.ru", "expected_ip": "138.197.254.53"},
                completed_at=datetime.now()
            )
        except Exception as e:
            return TestResult(
                test_name="DNS Resolution (97v.ru)",
                test_category="Infrastructure",
                test_type="Integration",
                status="error",
                error_message=str(e),
                completed_at=datetime.now()
            )
    
    # ========================================================================
    # API TESTS
    # ========================================================================
    
    def test_api_analysis_endpoint(self) -> TestResult:
        """Test GET /api/v1/analysis/{id} endpoint"""
        start_time = datetime.now()
        
        try:
            headers = {}
            if API_TOKEN:
                headers['Authorization'] = f"Bearer {API_TOKEN}"
            
            response = requests.get(
                f"{API_URL}/api/v1/analysis/test-id",
                headers=headers,
                timeout=5
            )
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            # 404 is OK for test-id
            success = response.status_code in [200, 404]
            
            return TestResult(
                test_name="GET /api/v1/analysis/{id}",
                test_category="API",
                test_type="Unit",
                status="passed" if success else "failed",
                response_time_ms=response_time,
                test_data={"endpoint": "/api/v1/analysis/{id}", "status_code": response.status_code},
                assertions_passed=1 if success else 0,
                assertions_total=1,
                completed_at=datetime.now()
            )
        except Exception as e:
            return TestResult(
                test_name="GET /api/v1/analysis/{id}",
                test_category="API",
                test_type="Unit",
                status="error",
                error_message=str(e),
                completed_at=datetime.now()
            )
    
    def test_api_metrics_endpoint(self) -> TestResult:
        """Test GET /api/v1/metrics endpoint"""
        start_time = datetime.now()
        
        try:
            headers = {}
            if API_TOKEN:
                headers['Authorization'] = f"Bearer {API_TOKEN}"
            
            response = requests.get(
                f"{API_URL}/api/v1/metrics",
                headers=headers,
                timeout=5
            )
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            success = response.status_code in [200, 401]  # 401 OK if no token
            
            return TestResult(
                test_name="GET /api/v1/metrics",
                test_category="API",
                test_type="Unit",
                status="passed" if success else "failed",
                response_time_ms=response_time,
                test_data={"endpoint": "/api/v1/metrics", "status_code": response.status_code},
                assertions_passed=1 if success else 0,
                assertions_total=1,
                completed_at=datetime.now()
            )
        except Exception as e:
            return TestResult(
                test_name="GET /api/v1/metrics",
                test_category="API",
                test_type="Unit",
                status="error",
                error_message=str(e),
                completed_at=datetime.now()
            )
    
    # ========================================================================
    # DATABASE TESTS
    # ========================================================================
    
    def test_database_connection(self) -> TestResult:
        """Test Supabase database connection (Project: lvixtpatqrtuwhygtpjx)"""
        start_time = datetime.now()
        
        try:
            if not self.supabase:
                return TestResult(
                    test_name="Database Connection",
                    test_category="Database",
                    test_type="Unit",
                    status="skipped",
                    error_message="Supabase not initialized",
                    completed_at=datetime.now()
                )
            
            # Try to fetch from a simple table
            response = self.supabase.table('test_results').select('COUNT(*)').execute()
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            success = response.data is not None
            
            return TestResult(
                test_name="Database Connection",
                test_category="Database",
                test_type="Unit",
                status="passed" if success else "failed",
                response_time_ms=response_time,
                test_data={"database": "supabase", "project_id": "lvixtpatqrtuwhygtpjx"},
                assertions_passed=1 if success else 0,
                assertions_total=1,
                completed_at=datetime.now()
            )
        except Exception as e:
            return TestResult(
                test_name="Database Connection",
                test_category="Database",
                test_type="Unit",
                status="error",
                error_message=str(e),
                completed_at=datetime.now()
            )
    
    # ========================================================================
    # RUN ALL TESTS
    # ========================================================================
    
    def run_infrastructure_tests(self):
        """Run all infrastructure tests"""
        logger.info("🔧 Running Infrastructure Tests...")
        self.log_test_result(self.test_kubernetes_health())
        self.log_test_result(self.test_dns_resolution())
    
    def run_api_tests(self):
        """Run all API tests"""
        logger.info("🌐 Running API Tests...")
        self.log_test_result(self.test_api_health())
        self.log_test_result(self.test_api_analysis_endpoint())
        self.log_test_result(self.test_api_metrics_endpoint())
    
    def run_database_tests(self):
        """Run all database tests"""
        logger.info("💾 Running Database Tests...")
        self.log_test_result(self.test_database_connection())
    
    def run_all_tests(self):
        """Run all test suites"""
        self.run_infrastructure_tests()
        self.run_api_tests()
        self.run_database_tests()
    
    def print_summary(self):
        """Print test execution summary"""
        if not self.results:
            logger.info("📄 No tests were executed")
            return
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == "passed")
        failed = sum(1 for r in self.results if r.status == "failed")
        errors = sum(1 for r in self.results if r.status == "error")
        skipped = sum(1 for r in self.results if r.status == "skipped")
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        avg_response_time = (
            sum(r.response_time_ms or 0 for r in self.results) / total
            if total > 0 else 0
        )
        
        print("\n" + "="*70)
        print("📈 TEST EXECUTION SUMMARY")
        print("="*70)
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Errors: {errors}")
        print(f"⏳ Skipped: {skipped}")
        print(f"\nPass Rate: {pass_rate:.1f}%")
        print(f"Avg Response Time: {avg_response_time:.2f}ms")
        print("="*70 + "\n")

# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Run automated test suite")
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all tests'
    )
    parser.add_argument(
        '--infrastructure',
        action='store_true',
        help='Run infrastructure tests'
    )
    parser.add_argument(
        '--api',
        action='store_true',
        help='Run API tests'
    )
    parser.add_argument(
        '--database',
        action='store_true',
        help='Run database tests'
    )
    
    args = parser.parse_args()
    
    # Default to all if nothing specified
    if not any([args.all, args.infrastructure, args.api, args.database]):
        args.all = True
    
    suite = TestSuite()
    suite.create_test_run(f"Test Run - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        if args.all:
            suite.run_all_tests()
        else:
            if args.infrastructure:
                suite.run_infrastructure_tests()
            if args.api:
                suite.run_api_tests()
            if args.database:
                suite.run_database_tests()
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
    finally:
        suite.print_summary()

if __name__ == "__main__":
    main()
