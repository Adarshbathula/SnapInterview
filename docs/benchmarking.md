# Benchmarking

No Snapdragon performance numbers are present. The runtime UI labels Snapdragon benchmark status **Not yet measured**.

For each actual model/provider run, record:

- Machine/SoC, OS/build, memory, thermals/power mode, runtime/provider and version.
- Model identifier, license, quantization/precision, input dimensions and output length.
- Cold-start/load time separately from warm request latency.
- At least 30 warm runs where practical: median, p90, and run-to-run variability.
- Peak process memory; CPU utilization; GPU/NPU utilization only if supported instrumentation exposes it.
- Correctness/quality checks on the same sample set.
- Whether the test is local/offline, and whether any compilation was hosted.

Do not compare unlike models or claim speedup from non-equivalent inputs. Keep raw results with environment metadata and scripts. The generic benchmark harness does not itself constitute a model benchmark.
