# pinger: ping the bot every 10 minutes to keep it alive

import requests
import time
from datetime import datetime

# Replace with your Render URL
url = "https://oenomaus.onrender.com"
# Interval in seconds (30 seconds)
interval = 30

def ping_bot():
    try:
        response = requests.get(url)
        print(f"Pinged at {datetime.utcnow().isoformat()}: Status Code {response.status_code}")
    except requests.RequestException as error:
        print(f"Error pinging at {datetime.utcnow().isoformat()}: {error}")

# Run the function at the specified interval
while True:
    ping_bot()
    time.sleep(interval)