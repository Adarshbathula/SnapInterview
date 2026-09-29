"""Generic, plugin-driven benchmark harness; it never invents a provider or a result."""
import argparse, importlib, json, statistics, time
from pathlib import Path
import psutil


def load_callable(spec):
    module, name = spec.split(":", 1)
    return getattr(importlib.import_module(module), name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--factory", required=True, help="Python factory as package.module:callable; must return (provider, infer_callable)")
    parser.add_argument("--input-json", required=True, help="JSON input passed to the provider inference callable")
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--output", default="benchmark-result.json")
    args = parser.parse_args()
    factory = load_callable(args.factory)
    provider, infer = factory()
    sample = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
    for _ in range(max(0,args.warmup)): infer(provider, sample)
    process = psutil.Process()
    rss_before = process.memory_info().rss
    timings=[]
    for _ in range(max(1,args.runs)):
        start=time.perf_counter(); infer(provider, sample); timings.append((time.perf_counter()-start)*1000)
    rss_after = process.memory_info().rss
    timings.sort()
    result={"model": getattr(provider,"model_id","unspecified"), "backend": getattr(provider,"backend_name","unspecified"), "provider": provider.__class__.__name__, "runs":len(timings), "warmup_runs":max(0,args.warmup), "latency_ms_median":round(statistics.median(timings),2), "latency_ms_p90":round(timings[min(len(timings)-1,int(.9*len(timings)))],2), "process_rss_delta_mb":round((rss_after-rss_before)/1024/1024,2), "memory_note":"Process RSS delta; not peak accelerator memory.", "cpu_utilization_percent":None, "gpu_utilization_percent":None, "npu_utilization_percent":None, "device":None, "measured_at":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}
    Path(args.output).write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__ == "__main__": main()
