#!/bin/bash

# Stop Job Search Automation Servers

echo "🛑 Stopping Job Search Automation System..."

if [ -f .server_pids ]; then
    while read pid; do
        if ps -p $pid > /dev/null; then
            kill $pid
            echo "   Stopped process $pid"
        fi
    done < .server_pids
    rm .server_pids
    echo "✅ All servers stopped"
else
    echo "⚠️  No server PIDs found. Servers may not be running."
fi