# AI runtime and provider contracts

## Contracts

`backend/app/ai/interfaces/contracts.py` defines app-owned protocols and evaluation input/output dataclasses. Business rules should depend only on those contracts. `backend/app/ai/runtime/backend_selector.py` is the single selection point for the implemented development evaluator.

Current status:

| Capability | Current implementation | Limitation |
|---|---|---|
| Answer evaluation | Deterministic keyword rubric | Not an LLM; not validated grading |
| Speech recognition | Optional `faster-whisper` local CPU adapter | Model weights are not bundled; install/setup required |
| Embeddings | Interface only | No vector model/store |
| Vision | Browser-local MediaPipe Face Landmarker | Webcam consent required; reports approximate face-in-frame, centering and head-position stability only |
| Hardware | Host metadata and installed ONNX provider discovery | Does not prove a specific model runs on an accelerator |

If `AI_BACKEND` requests an unavailable specialized implementation, the service reports a fallback rather than claiming that implementation is active.

## Result format

LLM adapters should validate structured output against app-owned schemas. Use bounded scores, arrays of evidence and missing concepts, plus a follow-up string. Validate the output and never rely on free-form text parsing. Preserve an evaluator/model identifier and the transcript evidence used for feedback.

## Qualcomm path

Use Qualcomm AI Hub and Qualcomm developer documentation as primary sources when the target PC is selected. Qualcomm AI Hub describes model optimization/compilation and profiling for target devices. Its current guidance recommends considering ONNX Runtime for Windows/laptop deployments; target-specific support and performance still require verification. An NPU execution-provider listing does not prove every model runs on the NPU. Keep Qualcomm runtime imports inside the Snapdragon provider package, which should remain optional for Intel development.
