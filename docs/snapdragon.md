# Snapdragon deployment plan

**Status: requires verification on Snapdragon hardware.** No Snapdragon provider, device detection result, model installation, or benchmark is included in the current prototype.

## Procedure

1. Identify the exact HP product, Snapdragon SoC, Windows build, memory capacity, and target application packaging.
2. Re-check official Qualcomm AI Hub model pages and runtime documentation for that precise target and supported model variants.
3. Select a candidate based on task quality, model license, memory footprint, language support, and target compilation/inference support.
4. Compile or obtain target assets using the supported Qualcomm workflow; retain model manifests, checksums, and source/license attribution.
5. Implement a provider adapter behind the existing app interface. Avoid Qualcomm-specific types in the API and interview engine.
6. Run shared correctness tests and structured-output validation on the real PC.
7. Profile cold-start and warm inference latency, memory, CPU utilization, and NPU utilization if official tooling exposes it. Repeat on identical inputs and document methodology.
8. Compare only measurements made on recorded devices and software versions. If not measured, write **Not yet measured**.

Qualcomm AI Hub documentation identifies Windows ONNX Runtime as a recommended path to evaluate, and describes QNN/ONNX deployment options. The correct option depends on the exact target model, runtime support, and target device. Do not assume a package/API or that a device-specific compiled artifact is portable.

Official references to re-check at implementation time:

- [Qualcomm AI Hub documentation](https://workbench.aihub.qualcomm.com/docs/)
- [Qualcomm model compilation examples](https://workbench.aihub.qualcomm.com/docs/hub/compile_examples.html)
- [Qualcomm runtime/model-format FAQ](https://workbench.aihub.qualcomm.com/docs/hub/faq.html)
- [Whisper-Base AI Hub model page](https://aihub.qualcomm.com/models/whisper_base)
- [Whisper-Small-Quantized AI Hub model page](https://aihub.qualcomm.com/models/whisper_small_quantized)
