#!/bin/bash
# Test script to verify ChatKit CORS configuration

echo "=== ChatKit CORS Test ==="
echo ""

echo "1. Testing OPTIONS preflight request..."
echo "---"
curl -X OPTIONS http://localhost:8002/api/v1/chatkit \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Authorization,Content-Type" \
  -v \
  2>&1 | grep -E "(< HTTP|< access-control|< content-type|status)"

echo ""
echo "---"
echo ""

echo "Expected:"
echo "  - HTTP status: 200 OK"
echo "  - access-control-allow-origin: http://localhost:3000"
echo "  - access-control-allow-methods: contains POST"
echo "  - access-control-allow-headers: contains Authorization, Content-Type"
echo ""

echo "If you see 200 OK and proper CORS headers, the backend is configured correctly."
echo "If you see 400 or 401, check backend logs for errors."
