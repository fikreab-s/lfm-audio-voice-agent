"""Voice agent pipeline latency simulation."""
import json, numpy as np, argparse
from pathlib import Path
np.random.seed(42)

STAGES = [("VAD", 20, 5), ("ASR", 150, 30), ("LFM_TTFT", 65, 15), ("TTS_start", 180, 40)]

def main():
    p = argparse.ArgumentParser(); p.add_argument("--n_utterances", type=int, default=100)
    p.add_argument("--output_dir", default="outputs"); a = p.parse_args()
    out = Path(a.output_dir); out.mkdir(parents=True, exist_ok=True)
    results = []
    for i in range(a.n_utterances):
        stages = {}; total = 0
        for name, mean, std in STAGES:
            lat = max(5, np.random.normal(mean, std))
            stages[name] = round(lat, 1); total += lat
        results.append({"utterance_id": i, "stages": stages, "total_ms": round(total, 1),
                        "sla_met": total < 500})
    sla_met = sum(1 for r in results if r["sla_met"])
    with open(out / "latency_log.json", "w") as f: json.dump(results[:10], f, indent=2)
    print(f"\u2705 Voice Pipeline ({a.n_utterances} utterances)")
    print(f"   SLA (<500ms): {sla_met}/{a.n_utterances} ({sla_met/a.n_utterances*100:.1f}%)")
    print(f"   Avg total: {np.mean([r['total_ms'] for r in results]):.0f}ms")
    print(f"   p99 total: {np.percentile([r['total_ms'] for r in results], 99):.0f}ms")
    for name, _, _ in STAGES:
        vals = [r["stages"][name] for r in results]
        print(f"   {name}: {np.mean(vals):.0f}ms avg, {np.percentile(vals,99):.0f}ms p99")

if __name__ == "__main__": main()
