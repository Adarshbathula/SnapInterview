"""Render only measurements that exist; no sample or placeholder scores are fabricated."""
import json
from pathlib import Path
import sys

files=[Path(p) for p in sys.argv[1:]]
if not files:
    print("Snapdragon benchmark: Not yet measured\nNo benchmark result files were supplied.")
    raise SystemExit(0)
for path in files:
    data=json.loads(path.read_text(encoding="utf-8"))
    print(f"Model: {data.get('model','unspecified')} | Backend: {data.get('backend','unspecified')} | Device: {data.get('device') or 'not recorded'}")
    print(f"Median latency: {data['latency_ms_median']} ms | p90: {data['latency_ms_p90']} ms | RSS delta: {data['process_rss_delta_mb']} MB")
    print("CPU/GPU/NPU utilization: " + ", ".join(f"{k}={data.get(k) if data.get(k) is not None else 'not measured'}" for k in ["cpu_utilization_percent","gpu_utilization_percent","npu_utilization_percent"]))
