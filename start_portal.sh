#!/bin/bash
echo "Starting Blackhole SSC CGL Portal..."

# Terminate any old instances
pkill -f "python3 app/server.py" 2>/dev/null
pkill -f "cloudflared tunnel" 2>/dev/null
sleep 1

# Start backend server
nohup python3 app/server.py > /tmp/portal_server.log 2>&1 &
sleep 2

# Start Cloudflare public tunnel
nohup .bin/cloudflared tunnel --url http://127.0.0.1:3000 > /tmp/cloudflared.log 2>&1 &
sleep 3

# Display active URLs
URL=$(cat /tmp/cloudflared.log | grep -o 'https://[-a-z0-9]*\.trycloudflare\.com' | head -n 1)
echo "================================================="
echo "Blackhole Test Portal is LIVE!"
echo "Local Address:  http://localhost:3000"
if [ -n "$URL" ]; then
  echo "Public Address: $URL"
fi
echo "================================================="
