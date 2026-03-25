#!/usr/bin/env python3
"""
Django REST Framework API Test Script
Tests all major API endpoints to verify the setup is working correctly
"""

import requests
import sys
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8001"
API_URL = f"{BASE_URL}/api"

class APITester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
        self.session = requests.Session()

    def test_endpoint(self, method, endpoint, name, expected_status=200, data=None):
        """Test a single endpoint"""
        url = f"{API_URL}{endpoint}"

        try:
            if method == "GET":
                response = self.session.get(url, timeout=5)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=5)
            elif method == "PUT":
                response = self.session.put(url, json=data, timeout=5)
            elif method == "PATCH":
                response = self.session.patch(url, json=data, timeout=5)
            elif method == "DELETE":
                response = self.session.delete(url, timeout=5)
            else:
                raise ValueError(f"Unknown HTTP method: {method}")

            status = response.status_code
            passed = status == expected_status

            result = {
                'name': name,
                'method': method,
                'endpoint': endpoint,
                'expected': expected_status,
                'actual': status,
                'passed': passed
            }

            if passed:
                self.passed += 1
                status_text = "✅ PASSED"
            else:
                self.failed += 1
                status_text = "❌ FAILED"

            print(f"{status_text:15} {name:30} (HTTP {status})")
            self.results.append(result)

            return passed

        except requests.exceptions.ConnectionError:
            print(f"❌ ERROR      {name:30} (Connection refused)")
            self.failed += 1
            result = {
                'name': name,
                'method': method,
                'endpoint': endpoint,
                'expected': expected_status,
                'actual': 'Connection Error',
                'passed': False
            }
            self.results.append(result)
            return False
        except Exception as e:
            print(f"❌ ERROR      {name:30} ({str(e)})")
            self.failed += 1
            result = {
                'name': name,
                'method': method,
                'endpoint': endpoint,
                'expected': expected_status,
                'actual': f'Exception: {str(e)}',
                'passed': False
            }
            self.results.append(result)
            return False

    def run_tests(self):
        """Run all tests"""
        print("=" * 80)
        print("Django REST Framework API Test Suite")
        print("=" * 80)
        print()

        print("1. Server Connection Tests")
        print("-" * 80)
        self.test_endpoint("GET", "/", "API Root", 200)
        print()

        print("2. Documentation Endpoints")
        print("-" * 80)
        self.test_endpoint("GET", "/schema/", "OpenAPI Schema", 200)
        self.test_endpoint("GET", "/docs/", "Swagger UI", 200)
        print()

        print("3. Resource List Endpoints")
        print("-" * 80)
        self.test_endpoint("GET", "/workspaces/", "Workspaces List", 200)
        self.test_endpoint("GET", "/projects/", "Projects List", 200)
        self.test_endpoint("GET", "/tasks/", "Tasks List", 200)
        self.test_endpoint("GET", "/events/", "Events List", 200)
        self.test_endpoint("GET", "/reminders/", "Reminders List", 200)
        self.test_endpoint("GET", "/notes/", "Notes List", 200)
        self.test_endpoint("GET", "/quicknotes/", "QuickNotes List", 200)
        print()

        print("4. Filtered/Custom Endpoints")
        print("-" * 80)
        self.test_endpoint("GET", "/tasks/?is_completed=false", "Incomplete Tasks", 200)
        self.test_endpoint("GET", "/tasks/?ordering=due_datetime", "Tasks (Ordered)", 200)
        self.test_endpoint("GET", "/tasks/overdue/", "Overdue Tasks", 200)
        self.test_endpoint("GET", "/reminders/unresolved/", "Unresolved Reminders", 200)
        self.test_endpoint("GET", "/projects/?is_archived=false", "Active Projects", 200)
        print()

        print("5. Error Handling Tests")
        print("-" * 80)
        self.test_endpoint("GET", "/tasks/99999/", "Non-existent Task (404)", 404)
        self.test_endpoint("GET", "/invalid-endpoint/", "Invalid Endpoint (404)", 404)
        print()

        print("=" * 80)
        print("Test Summary")
        print("=" * 80)
        total = self.passed + self.failed
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📊 Total:  {total}")
        print(f"📈 Success Rate: {(self.passed/total*100):.1f}%" if total > 0 else "N/A")
        print()

        if self.failed == 0:
            print("🎉 ALL TESTS PASSED! API is ready for deployment.")
            return True
        else:
            print("⚠️  Some tests failed. Check the output above.")
            return False

    def save_report(self, filename="api_test_report.json"):
        """Save test report to JSON file"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'base_url': BASE_URL,
            'api_url': API_URL,
            'summary': {
                'passed': self.passed,
                'failed': self.failed,
                'total': self.passed + self.failed,
                'success_rate': f"{(self.passed/(self.passed + self.failed)*100):.1f}%" if (self.passed + self.failed) > 0 else "N/A"
            },
            'results': self.results
        }

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"📄 Test report saved to: {filename}")


if __name__ == "__main__":
    tester = APITester()
    success = tester.run_tests()
    tester.save_report()
    sys.exit(0 if success else 1)

