#!/bin/sh

echo "⏳ Waiting for Flask app to be ready..."
while ! curl -s http://localhost:8000/ > /dev/null; do
  sleep 1
done
echo "✅ Flask app is ready! Running tests..."

pytest /app/Tests/
