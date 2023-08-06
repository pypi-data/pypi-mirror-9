"""Count the user's Wifi records
 
Type: personal
 
Input:
    wifi : /v1/data/PdsWifi, STREAM
 
Output:
    wifi_count: /v1/data/tc.you.WifiCount, POST
"""
import time


def execute(wifi, *args, **kwargs):
    wifi_count = kwargs['wifi_count']
    count = 0
    now = int((time.time() + 0.5) * 1000)
    for _ in wifi:
        count += 1
    if count > 0:
        wifi_count.write({'count': count, 'timestamp': now})