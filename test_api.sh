#!/bin/bash

# Django API Test Script
# Tests all major API endpoints

echo "======================================"
echo "Django REST Framework API Test Suite"
echo "======================================"
echo ""

# Configuration
BASE_URL="http://localhost:8001"
API_URL="$BASE_URL/api"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local name=$3
    local expected_code=$4

    echo -n "Testing $name... "

    response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" = "$expected_code" ]; then
        echo -e "${GREEN}✅ PASSED${NC} (HTTP $http_code)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC} (Expected $expected_code, got $http_code)"
        echo "Response: $body"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

echo "1. Testing API Root"
echo "===================="
test_endpoint "GET" "/" "API Root" "200"
echo ""

echo "2. Testing Documentation Endpoints"
echo "===================================="
test_endpoint "GET" "/schema/" "OpenAPI Schema" "200"
test_endpoint "GET" "/docs/" "Swagger UI" "200"
echo ""

echo "3. Testing Resource Endpoints (List)"
echo "====================================="
test_endpoint "GET" "/workspaces/" "Workspaces List" "200"
test_endpoint "GET" "/projects/" "Projects List" "200"
test_endpoint "GET" "/tasks/" "Tasks List" "200"
test_endpoint "GET" "/events/" "Events List" "200"
test_endpoint "GET" "/reminders/" "Reminders List" "200"
test_endpoint "GET" "/notes/" "Notes List" "200"
test_endpoint "GET" "/quicknotes/" "QuickNotes List" "200"
echo ""

echo "4. Testing Filtered Endpoints"
echo "=============================="
test_endpoint "GET" "/tasks/?is_completed=false" "Incomplete Tasks Filter" "200"
test_endpoint "GET" "/tasks/overdue/" "Overdue Tasks" "200"
test_endpoint "GET" "/reminders/unresolved/" "Unresolved Reminders" "200"
echo ""

echo "5. Testing Non-existent Endpoint"
echo "================================="
test_endpoint "GET" "/tasks/99999/" "Non-existent Task (404)" "404"
echo ""

echo "======================================"
echo "Test Results Summary"
echo "======================================"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    exit 1
fi

