"""Best-effort host detection. Accelerator claims require an installed, usable runtime."""
import os
import platform
import subprocess
import shlex


def _memory_gb() -> float | None:
    try:
        import psutil
        return round(psutil.virtual_memory().total / (1024 ** 3), 1)
    except Exception:
        pass
    if platform.system() == "Linux":
        try:
            with open("/proc/meminfo", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        return round(int(line.split()[1]) / 1024 / 1024, 1)
        except OSError:
            return None
    return None


def _host_names(command: list[str], timeout: float = 3) -> list[str]:
    try:
        output = subprocess.check_output(command, text=True, stderr=subprocess.DEVNULL, timeout=timeout)
        return [line.strip() for line in output.splitlines() if line.strip()]
    except Exception:
        return []


def _processor_name() -> str:
    system = platform.system()
    if system == "Linux":
        try:
            with open("/proc/cpuinfo", encoding="utf-8") as f:
                for line in f:
                    if line.lower().startswith(("model name", "hardware")) and ":" in line:
                        value = line.split(":", 1)[1].strip()
                        if value:
                            return value
        except OSError:
            pass
    elif system == "Windows":
        found = _host_names(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_Processor | Select-Object -First 1 -ExpandProperty Name)"])
        if found:
            return found[0]
    return platform.processor() or platform.machine() or "Unknown processor"


def _gpu_names() -> list[str]:
    system = platform.system()
    if system == "Windows":
        return _host_names(["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_VideoController | ForEach-Object { $_.Name }"])
    if system == "Linux":
        lines = _host_names(["lspci", "-mm"])
        devices=[]
        for line in lines:
            if '"VGA compatible controller"' in line or '"3D controller"' in line or '"Display controller"' in line:
                parts=shlex.split(line)
                devices.append(parts[3] if len(parts)>3 else line)
        return devices
    if system == "Darwin":
        lines = _host_names(["system_profiler", "SPDisplaysDataType"])
        return [line.split(":", 1)[1].strip() for line in lines if line.strip().startswith("Chipset Model:")]
    return []


def detect_hardware() -> dict:
    processor = _processor_name()
    gpu_devices = _gpu_names()
    providers = ["CPUExecutionProvider"]
    try:
        import onnxruntime as ort
        providers = list(ort.get_available_providers())
    except Exception:
        pass
    qnn_present = any("QNN" in p.upper() for p in providers)
    dml_present = any("DML" in p.upper() for p in providers)
    # Do not infer that an NPU exists from a chipset name. Runtime presence alone also
    # does not guarantee a selected model will execute on it; show this as runtime detected.
    return {
        "device": platform.node() or "Local device",
        "processor": processor,
        "operating_system": f"{platform.system()} {platform.release()}",
        "architecture": platform.machine(),
        "memory_gb": _memory_gb(),
        "gpu_devices": gpu_devices,
        "gpu_available": bool(gpu_devices),
        "backend": "Local CPU (development rubric)",
        "available_runtime_backend": "Qualcomm QNN available" if qnn_present else ("DirectML available" if dml_present else "CPU provider only"),
        "execution_providers": providers,
        "npu_runtime_detected": qnn_present,
        "gpu_runtime_detected": dml_present,
        "offline_mode": os.getenv("OFFLINE_MODE", "true").lower() == "true",
        "detection_note": "Provider availability is detected from installed ONNX Runtime providers when available. Model-level acceleration still requires validation.",
    }
