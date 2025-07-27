import numpy as np
import json
import os
import requests

class ChartDataStore:
    def __init__(self, filename=None):
        if filename is None:
            filename = os.path.join(os.path.dirname(__file__), 'data.json')
        self.filename = filename
        

    def load_static_data(self):
        if not os.path.exists(self.filename):
            return {"labels": [], "values": []}
        with open(self.filename, 'r') as f:
            data = json.load(f)
        # 限制最多返回24行（最新的）
        if isinstance(data, list):
            data = sorted(data, key=lambda d: d.get('time', ''), reverse=True)[:24]
        return data

    def save_static_data(self, data):
        with open(self.filename, 'w') as f:
            json.dump(data, f)

    def load_realtime_data(self, url='http://reef.lan:6001/data'):
        try:
            resp = requests.get(url, timeout=10)
            raw = resp.json()
            lines = raw.get('data', '').split('\n')
            cleaned = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    time = obj.get('time')
                    content = obj.get('content', '')
                    vals = {}
                    for entry in content.split('\n'):
                        entry = entry.strip()
                        if entry.startswith('ORP'):
                            vals['ORP'] = float(entry.split()[1])
                        elif entry.startswith('PH'):
                            vals['PH'] = float(entry.split()[1])
                        elif entry.startswith('T'):
                            vals['T'] = float(entry.split()[1])
                    if 'ORP' in vals and 'PH' in vals and 'T' in vals:
                        cleaned.append({
                            'time': time,
                            'ORP': int(round(vals['ORP'])),
                            'PH': round(vals['PH'], 1),
                            'T': vals['T']
                        })
                except Exception:
                    continue

            # 按小时分组（不做时间筛选）
            def get_hour(ts):
                return ts[:13] if ts else ''
            hour_map = {}
            for d in cleaned:
                hour = get_hour(d['time'])
                if hour not in hour_map:
                    hour_map[hour] = []
                hour_map[hour].append(d)

            filtered = []
            for hour, entries in hour_map.items():
                filtered.extend(entries)
            print(f"Filtered {len(cleaned)} entries to {len(filtered)} after hour grouping (no time limit)")

            # 按时间倒序返回所有数据（不限制行数）
            filtered_sorted = sorted(filtered, key=lambda d: d['time'], reverse=True)
            print(f"Processed {len(filtered_sorted)} entries from real-time data after hour grouping")
            return filtered_sorted
        except Exception as e:
            print(f"Error loading real-time data: {e}")
            return []
