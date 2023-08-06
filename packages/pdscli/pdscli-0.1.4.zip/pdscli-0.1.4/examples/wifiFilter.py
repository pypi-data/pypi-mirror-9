"""Duplicate a sub-set of the user's Wifi records
 
Type: personal
 
Input:
    wifi : /v1/data/PdsWifi, STREAM
 
Output:
    wifi_filter: /v1/data/tc.you.WifiFilter, POST
"""

def execute(wifi, *args, **kwargs):
    wifi_filter = kwargs['wifi_filter']
    count = 0
    for entry in wifi:
        if count % 10 == 0:
            # Create filtered view of the wifi record
            filtered = {}
            for prop in ['deviceId', 'BSSID', 'SSID', 'timestamp']:
                value = entry.pop(prop, None)
                if not value is None:
                    filtered[prop] = value
            wifi_filter.write(filtered)
        count += 1
