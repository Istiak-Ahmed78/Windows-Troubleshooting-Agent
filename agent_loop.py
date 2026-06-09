"""
Agent Loop - LLM-driven troubleshooting agent with Ollama integration
ReAct pattern: LLM reasons -> picks tool -> tool executes -> LLM evaluates -> repeats or answers
"""
import json
import os
import re
import shutil
import subprocess
import sys
import traceback
import urllib.request
import urllib.error
import time
from typing import Dict, List, Any, Optional, Callable
from diagnostics import WindowsDiagnostics, ErrorMessageParser


# --- Logging ---
_log_file = None

def _log(msg: str):
    global _log_file
    if _log_file is None:
        import tempfile
        _log_file = os.path.join(tempfile.gettempdir(), "ai_troubleshooter_debug.log")
    try:
        with open(_log_file, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    except:
        pass


# --- Exception wrapper ---
class ProviderError(RuntimeError):
    """Wraps any provider call error with the raw response for debugging."""
    def __init__(self, message: str, raw_response: str = "", status_code: int = 0):
        super().__init__(message)
        self.raw_response = raw_response
        self.status_code = status_code


# ============================================================
# Tools the LLM can call
# ============================================================

TOOL_DEFINITIONS = [
    # === Core System ===
    {
        "name": "get_system_info",
        "description": "Get comprehensive system information including CPU, RAM, disk, and network status",
        "args": {}
    },
    {
        "name": "get_cpu_info",
        "description": "Get CPU usage percentage, core count, frequency, and temperature",
        "args": {}
    },
    {
        "name": "get_memory_info",
        "description": "Get RAM usage percentage, total, available, and health status",
        "args": {}
    },
    {
        "name": "get_disk_info",
        "description": "Get disk partition usage including free space and health for all drives",
        "args": {}
    },
    {
        "name": "get_top_processes",
        "description": "Get top CPU-consuming and memory-consuming processes",
        "args": {"top_n": "Number of top processes to show (default 10)"}
    },
    {
        "name": "get_system_uptime",
        "description": "Get how long the system has been running since last boot",
        "args": {}
    },
    {
        "name": "get_performance_summary",
        "description": "Get CPU, memory, disk usage percentages in one call (quick health check)",
        "args": {}
    },
    # === Installed Software & Startup ===
    {
        "name": "get_installed_software",
        "description": "List installed software from Windows Registry (name, version, publisher)",
        "args": {}
    },
    {
        "name": "get_startup_programs",
        "description": "List programs that run at system startup",
        "args": {}
    },
    # === Services & Drivers ===
    {
        "name": "get_running_services",
        "description": "List running Windows services and their status",
        "args": {"name_filter": "Optional filter by service name (e.g. 'defend', 'update')"}
    },
    {
        "name": "get_drivers_summary",
        "description": "Get list of installed drivers, their states, and problem devices",
        "args": {}
    },
    {
        "name": "get_problem_devices",
        "description": "Get devices with issues (yellow exclamation mark in Device Manager)",
        "args": {}
    },
    # === Event Log & Crashes ===
    {
        "name": "get_event_log_crashes",
        "description": "Get recent application crash events from Windows Event Log",
        "args": {}
    },
    {
        "name": "get_critical_events",
        "description": "Get critical system errors from Event Log (BSOD, hardware failures)",
        "args": {"max_events": "Maximum events to return (default 10)"}
    },
    {
        "name": "get_minidump_info",
        "description": "Check for BSOD minidump files and return their details",
        "args": {}
    },
    # === Error Analysis ===
    {
        "name": "parse_error_message",
        "description": "Parse a Windows error message text and identify the specific error type and solutions",
        "args": {"text": "The error message text to analyze"}
    },
    {
        "name": "parse_bsod_error",
        "description": "Analyze a BSOD stop code (e.g. IRQL_NOT_LESS_OR_EQUAL, KMODE_EXCEPTION) and suggest causes",
        "args": {"stop_code": "The BSOD stop code name or bug check string"}
    },
    # === Disk & File System ===
    {
        "name": "get_disk_health",
        "description": "Check disk health using SMART data and file system errors",
        "args": {}
    },
    {
        "name": "check_file_locks",
        "description": "Check which process is locking a specific file (handle.exe or built-in method)",
        "args": {"file_path": "Full path to the file"}
    },
    {
        "name": "get_disk_space_detail",
        "description": "Get detailed disk usage across all drives including temp file sizes",
        "args": {}
    },
    # === Network ===
    {
        "name": "get_network_info",
        "description": "Get network adapter information including IP, DNS, and connection status",
        "args": {}
    },
    {
        "name": "test_network_connectivity",
        "description": "Test network connectivity: ping gateway, DNS resolution, and external host",
        "args": {}
    },
    {
        "name": "get_wifi_info",
        "description": "Get WiFi adapter status, signal strength, and connected SSID",
        "args": {}
    },
    {
        "name": "get_bluetooth_status",
        "description": "Check Bluetooth adapter and paired device status",
        "args": {}
    },
    # === Hardware ===
    {
        "name": "get_usb_devices",
        "description": "List connected USB devices and their status",
        "args": {}
    },
    {
        "name": "get_display_info",
        "description": "Get GPU and display adapter information",
        "args": {}
    },
    {
        "name": "get_audio_devices",
        "description": "Get audio playback and recording devices",
        "args": {}
    },
    {
        "name": "get_printer_info",
        "description": "Get printer status and print spooler status",
        "args": {}
    },
    {
        "name": "get_battery_info",
        "description": "Get battery status and health information",
        "args": {}
    },
    # === Windows Update & System Health ===
    {
        "name": "get_windows_update_status",
        "description": "Get Windows Update status, pending updates, and last check time",
        "args": {}
    },
    {
        "name": "check_system_file_integrity",
        "description": "Run SFC /verifyonly to check system file integrity (read-only, about 2-5 min)",
        "args": {}
    },
    {
        "name": "get_windows_defender_status",
        "description": "Check if Windows Defender is active, real-time protection, and last scan",
        "args": {}
    },
    # === Boot & Recovery ===
    {
        "name": "get_boot_configuration",
        "description": "Get boot configuration data (BCD) and boot manager status",
        "args": {}
    },
    {
        "name": "get_user_profiles",
        "description": "List user profiles on the system and their status",
        "args": {}
    },
]


def _run_powershell(cmd: str, timeout: int = 30) -> str:
    """Run a PowerShell command and return stdout"""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip() or result.stderr.strip()
    except subprocess.TimeoutExpired:
        return "Command timed out"
    except Exception as e:
        return f"Error: {e}"

def _parse_powershell_table(text: str) -> List[Dict[str, str]]:
    """Parse a PowerShell table output into list of dicts"""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if len(lines) < 3:
        return []
    headers = [h.strip().lower().replace(" ", "_") for h in lines[0].split()]
    rows = []
    for line in lines[2:]:
        if "---" in line:
            continue
        parts = line.split()
        if len(parts) >= len(headers):
            rows.append(dict(zip(headers, parts[:len(headers)])))
    return rows

def _run_cmd(cmd: str, timeout: int = 30) -> str:
    """Run a system command and return stdout"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip() or result.stderr.strip()
    except subprocess.TimeoutExpired:
        return "Command timed out"
    except Exception as e:
        return f"Error: {e}"


def _get_tool_implementations() -> Dict[str, Callable]:
    """Map tool names to actual functions"""
    d = WindowsDiagnostics()
    from advanced_diagnostics import AdvancedDiagnostics as AD

    # Helper to run a static method or return error
    def _safe_static(func, *args):
        try:
            return func(*args) if args else func()
        except Exception as e:
            return {"error": str(e)}

    return {
        # === Core System ===
        "get_system_info": lambda args: d.get_system_info(),
        "get_cpu_info": lambda args: d.get_cpu_info(),
        "get_memory_info": lambda args: d.get_memory_info(),
        "get_disk_info": lambda args: d.get_disk_info(),
        "get_top_processes": lambda args: d.get_top_processes(args.get("top_n", 10)),
        "get_system_uptime": lambda args: d.get_system_uptime(),
        "get_performance_summary": lambda args: {
            "cpu": d.get_cpu_info(),
            "memory": d.get_memory_info(),
            "disk": d.get_disk_info()
        },

        # === Installed Software & Startup ===
        "get_installed_software": lambda args: _safe_static(AD.get_installed_software),
        "get_startup_programs": lambda args: _safe_static(AD.get_startup_programs),

        # === Services & Drivers ===
        "get_running_services": lambda args: _safe_static(
            AD.get_running_services, args.get("name_filter", "")
        ),
        "get_drivers_summary": lambda args: _safe_static(AD.get_drivers_summary),
        "get_problem_devices": lambda args: _safe_static(AD.get_problem_devices),

        # === Event Log & Crashes ===
        "get_event_log_crashes": lambda args: d.get_recent_app_crashes(),
        "get_critical_events": lambda args: _safe_static(
            AD.get_critical_events, args.get("max_events", 10)
        ),
        "get_minidump_info": lambda args: _safe_static(AD.get_minidump_info),

        # === Error Analysis ===
        "parse_error_message": lambda args: ErrorMessageParser.parse(args.get("text", "")),
        "parse_bsod_error": lambda args: _safe_static(AD.parse_bsod_error, args.get("stop_code", "")),

        # === Disk & File System ===
        "get_disk_health": lambda args: d.run_chkdsk(args.get("drive", "C:")),
        "check_file_locks": lambda args: _safe_static(AD.check_file_locks, args.get("file_path", "")),
        "get_disk_space_detail": lambda args: {
            "partitions": d.get_disk_info(),
            "temp_files": _safe_static(AD.get_temp_file_size)
        },

        # === Network ===
        "get_network_info": lambda args: d.get_network_info(),
        "test_network_connectivity": lambda args: _safe_static(AD.test_network_connectivity),
        "get_wifi_info": lambda args: _safe_static(AD.get_wifi_info),
        "get_bluetooth_status": lambda args: _safe_static(AD.get_bluetooth_status),

        # === Hardware ===
        "get_usb_devices": lambda args: _safe_static(AD.get_usb_devices),
        "get_display_info": lambda args: _safe_static(AD.get_display_info),
        "get_audio_devices": lambda args: _safe_static(AD.get_audio_devices),
        "get_printer_info": lambda args: _safe_static(AD.get_printer_info),
        "get_battery_info": lambda args: d.get_battery_info(),

        # === Windows Update & System Health ===
        "get_windows_update_status": lambda args: _safe_static(AD.get_windows_update_status),
        "check_system_file_integrity": lambda args: _safe_static(AD.check_system_file_integrity),
        "get_windows_defender_status": lambda args: d.get_windows_defender_status(),

        # === Boot & Recovery ===
        "get_boot_configuration": lambda args: _safe_static(AD.get_boot_configuration),
        "get_user_profiles": lambda args: _safe_static(AD.get_user_profiles),
    }


# ============================================================
# System prompt for the LLM
# ============================================================

SYSTEM_PROMPT_TEMPLATE = """You are an AI PC Troubleshooting Agent running on Windows. You help users diagnose and fix computer problems.

## Your Personality
- Be concise, direct, and helpful
- Explain technical issues in simple terms
- Never make up facts — use your tools to verify
- If a tool returns an error, say so honestly

## How to think and act
You solve problems step by step using the ReAct pattern:
1. THINK about what the user's problem might be
2. DECIDE which tool to use to investigate
3. CALL the tool
4. ANALYZE the result
5. Either call another tool OR give the final answer

## Available Tools
{tool_descriptions}

## Output Format
When you want to call a tool, output EXACTLY this format with nothing else:
```json
{{"tool": "tool_name", "args": {{"arg1": "value1"}}}}
```

When you have enough information to answer the user, output:
```json
{{"answer": "Your response to the user here",
  "findings": ["Finding 1", "Finding 2"],
  "solutions": ["Solution 1", "Solution 2"],
  "todos": [
    {{
      "action": "set_env_var",
      "params": {{"name": "FLUTTER_HOME", "value": "C:\\flutter", "scope": "user"}},
      "description": "Set FLUTTER_HOME environment variable",
      "requires_restart": false
    }},
    {{
      "action": "install_package",
      "params": {{"package": "Git.Git", "tool": "winget"}},
      "description": "Install Git for Windows",
      "requires_restart": false
    }},
    {{
      "action": "restart_pc",
      "params": {{}},
      "description": "Restart your PC to apply changes",
      "requires_restart": true
    }}
  ]}}
```

The "todos" array is OPTIONAL — only include it when there are concrete, actionable steps the user can take to fix the issue. Each todo must have: action, params, description, requires_restart.

Available actions and their params:
- set_env_var: {{"name": "VAR_NAME", "value": "VALUE", "scope": "user|machine"}}
- install_package: {{"package": "PackageId", "tool": "winget|choco|pip"}}
- run_command: {{"command": "cmd.exe /c command"}}
- registry_edit: {{"key": "path", "value_name": "name", "value_data": "data", "hive": "HKCU|HKLM"}}
- service_operation: {{"service": "name", "operation": "start|stop|restart"}}
- restart_pc: {{"": ""}}
- force_delete_file: {{"file_path": "C:\\full\\path\\to\\file"}}
- run_sfc_scan: {{"": ""}}
- run_dism_repair: {{"": ""}}
- clear_temp_files: {{"": ""}}
- reset_network_stack: {{"": ""}}
- disable_startup_item: {{"name": "ItemName", "scope": "user|machine"}}
- run_defender_scan: {{"": ""}}
- run_chkdsk: {{"drive": "C:"}}

## Rules
- Always use tools to investigate — don't guess
- Call one tool at a time (I'll give you the result)
- Stop calling tools once you have enough info to help the user
- If a tool fails, try a different approach
- If the user's issue is unclear, use get_system_info() first to understand their system state
- Never output anything other than the JSON format above

## Handling Complex Issues
- If the issue requires physical hardware repair (e.g., dead hard drive, faulty RAM stick, broken screen), say so clearly and suggest professional repair or replacement
- If the issue is beyond what tools can fix (e.g., motherboard failure, PSU failure), give the user a clear explanation and suggest the next steps
- For hardware issues that have software-based diagnostics (e.g., check disk health, test RAM), use the available tools first before concluding it's a hardware problem
- For network issues, always test connectivity, DNS, and gateway before suggesting router resets
- If you detect malware, suggest running a Defender scan and checking startup programs
- For corrupted files that can't be deleted, use the force_delete_file tool as a last resort"""


# ============================================================
# Model Manager - auto install Ollama and download models
# ============================================================

class ModelManager:
    """Manages Ollama installation and model downloading based on available disk space"""

    # Model preference order (best first)
    MODEL_PREFERENCE = [
        "llama3.1:8b",
        "qwen2.5:7b",
        "mistral:7b",
        "phi3:mini",
    ]

    # Approximate total size in GB (download + extracted)
    MODEL_SIZES = {
        "llama3.1:8b": 4.7,
        "qwen2.5:7b": 4.7,
        "mistral:7b": 4.1,
        "phi3:mini": 2.8,
        "phi3:medium": 5.2,
        "gemma2:9b": 5.5,
    }

    SAFETY_MARGIN_GB = 5.0
    OLLAMA_DOWNLOAD_URL = "https://ollama.com/download/OllamaSetup.exe"
    OLLAMA_INSTALL_DIRS = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Ollama"),
        os.path.join(os.environ.get("ProgramFiles", ""), "Ollama"),
        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Ollama"),
        os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Local", "Ollama"),
        os.path.join(os.environ.get("USERPROFILE", ""), "ollama"),
    ]

    @staticmethod
    def get_ollama_exe_path() -> Optional[str]:
        """Find ollama.exe in common install locations, registry, and via where.exe"""
        import winreg

        # 1. Check known install directories
        for d in ModelManager.OLLAMA_INSTALL_DIRS:
            p = os.path.join(d, "ollama.exe")
            if os.path.exists(p):
                return os.path.abspath(p)

        # 2. Check Windows registry for uninstall path
        try:
            for key_path in [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Ollama",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Ollama",
            ]:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as reg_key:
                        install_loc, _ = winreg.QueryValueEx(reg_key, "InstallLocation")
                        p = os.path.join(install_loc, "ollama.exe")
                        if os.path.exists(p):
                            return os.path.abspath(p)
                except WindowsError:
                    pass
        except Exception:
            pass

        # 3. Check PATH
        for p in os.environ.get("PATH", "").split(";"):
            candidate = os.path.join(p.strip(), "ollama.exe")
            if os.path.exists(candidate):
                return os.path.abspath(candidate)

        # 4. Common default installs (expand env vars)
        fallbacks = [
            os.path.expandvars(r"%USERPROFILE%\AppData\Local\Ollama\ollama.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Ollama\ollama.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Ollama\ollama.exe"),
        ]
        for p in fallbacks:
            if os.path.exists(p):
                return os.path.abspath(p)

        # 5. Try where.exe to locate it in PATH
        try:
            result = subprocess.run(
                ["where.exe", "ollama"],
                capture_output=True, text=True, timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                path = result.stdout.strip().split("\n")[0].strip()
                if os.path.exists(path):
                    return os.path.abspath(path)
        except Exception:
            pass

        # 6. Try PowerShell Get-Command as last resort
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", "(Get-Command ollama).Source"],
                capture_output=True, text=True, timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            path = result.stdout.strip()
            if path and os.path.exists(path):
                return os.path.abspath(path)
        except Exception:
            pass

        return None

    @staticmethod
    def is_ollama_installed() -> bool:
        """Check if Ollama is installed (whether running or not)"""
        return ModelManager.get_ollama_exe_path() is not None

    @staticmethod
    def get_free_space_gb(path: str = None) -> float:
        """Get free disk space in GB"""
        if path is None:
            path = os.path.expanduser("~")
        total, used, free = shutil.disk_usage(path)
        return free / (1024 ** 3)

    @staticmethod
    def recommend_model(preferred_model: str = None) -> Optional[str]:
        """
        Recommend the best model based on available disk space.
        If preferred_model is specified and fits, use it.
        """
        free_gb = ModelManager.get_free_space_gb()
        available_gb = free_gb - ModelManager.SAFETY_MARGIN_GB

        if preferred_model and preferred_model in ModelManager.MODEL_SIZES:
            if ModelManager.MODEL_SIZES[preferred_model] <= available_gb:
                return preferred_model

        for model in ModelManager.MODEL_PREFERENCE:
            if ModelManager.MODEL_SIZES[model] <= available_gb:
                return model
        return None

    @staticmethod
    def download_file(url: str, dest: str, progress_callback=None) -> bool:
        """Download a file with progress reporting"""
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            })
            with urllib.request.urlopen(req, timeout=120) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 8192
                with open(dest, "wb") as f:
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total > 0:
                            pct = int(downloaded * 100 / total)
                            progress_callback(pct, downloaded, total)
            return True
        except Exception as e:
            raise RuntimeError(f"Download failed: {e}")

    @staticmethod
    def install_ollama(installer_path: str, progress_callback=None) -> bool:
        """Install Ollama silently with progress reporting"""
        if progress_callback:
            progress_callback("Launching installer...")
        try:
            proc = subprocess.run(
                [installer_path, "/S"],
                capture_output=True, text=True, timeout=120
            )
            if progress_callback:
                progress_callback("Waiting for installation to complete...")
            time.sleep(2)
            return proc.returncode == 0
        except subprocess.TimeoutExpired:
            raise RuntimeError("Ollama installer timed out")
        except Exception as e:
            raise RuntimeError(f"Installation failed: {e}")

    @staticmethod
    def pull_model(model_name: str, progress_callback=None,
                   ollama_url: str = "http://localhost:11434") -> bool:
        """Pull (download) an Ollama model using CLI or HTTP API fallback"""
        # Strategy 1: Use CLI if executable is found
        ollama_exe = ModelManager.get_ollama_exe_path()
        if ollama_exe:
            try:
                proc = subprocess.Popen(
                    [ollama_exe, "pull", model_name],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, creationflags=subprocess.CREATE_NO_WINDOW
                )
                for line in proc.stdout:
                    line = line.strip()
                    if progress_callback and line:
                        progress_callback(line)
                proc.wait()
                if proc.returncode == 0:
                    return True
            except Exception:
                pass  # Fall through to API

        # Strategy 2: Use HTTP API (works even if EXE not in expected paths)
        try:
            if progress_callback:
                progress_callback("Connecting to Ollama API...")

            payload = json.dumps({
                "name": model_name,
                "stream": True
            }).encode()

            req = urllib.request.Request(
                f"{ollama_url}/api/pull",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=600) as resp:
                buffer = ""
                while True:
                    chunk = resp.read(4096)
                    if not chunk:
                        break
                    buffer += chunk.decode()
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            status = data.get("status", "")
                            if progress_callback and status:
                                # Extract progress info
                                total = data.get("total", 0)
                                completed = data.get("completed", 0)
                                if total > 0:
                                    pct = int(completed * 100 / total)
                                    progress_callback(f"{status} {pct}%")
                                else:
                                    progress_callback(status)
                            if status == "success":
                                return True
                        except json.JSONDecodeError:
                            if progress_callback:
                                progress_callback(line)

            return False
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise RuntimeError(
                    f"Model '{model_name}' not found. Check the name and try again.")
            raise RuntimeError(f"API error ({e.code}): {e.reason}")
        except Exception as e:
            raise RuntimeError(f"Model pull failed: {e}")

    @staticmethod
    def autosetup(progress_callback=None) -> Dict[str, Any]:
        """
        Full auto-setup: ensure Ollama is installed + download best model.
        Returns dict with status info.
        """
        result = {"ollama_installed": False, "model_downloaded": None, "steps": []}

        # Step 1: Check if Ollama is installed
        if ModelManager.is_ollama_installed():
            result["ollama_installed"] = True
            result["steps"].append("ollama_already_installed")
        else:
            if progress_callback:
                progress_callback("Downloading Ollama installer...")

            # Download installer
            installer_dir = os.path.join(os.environ.get("TEMP", os.path.expanduser("~")), "opencode_ollama")
            os.makedirs(installer_dir, exist_ok=True)
            installer_path = os.path.join(installer_dir, "OllamaSetup.exe")

            ModelManager.download_file(ModelManager.OLLAMA_DOWNLOAD_URL, installer_path)
            result["steps"].append("downloaded_installer")

            if progress_callback:
                progress_callback("Installing Ollama... (this may take a minute)")

            ModelManager.install_ollama(installer_path)
            result["ollama_installed"] = True
            result["steps"].append("installed_ollama")

        # Step 2: Recommend and download a model
        free_gb = ModelManager.get_free_space_gb()
        recommended = ModelManager.recommend_model()
        if recommended:
            result["model_downloaded"] = recommended
            result["steps"].append(f"recommended_{recommended}")

            if progress_callback:
                progress_callback(f"Downloading {recommended}... (this may take a while)")

            success = ModelManager.pull_model(recommended, progress_callback)
            if not success:
                result["steps"].append("model_download_failed")
            else:
                result["steps"].append("model_downloaded")
        else:
            result["steps"].append(f"no_model_fits_{free_gb:.1f}gb_free")

        return result


# ============================================================
# LLM Providers - pluggable backends (local Ollama, OpenAI API, etc.)
# ============================================================

class LLMProvider:
    """Base class for LLM providers"""
    name = "base"
    requires_key = False

    def call(self, messages: List[Dict], model: str = None) -> str:
        raise NotImplementedError

    def is_available(self) -> bool:
        return True


class OllamaProvider(LLMProvider):
    """Local Ollama provider"""
    name = "Ollama (Local)"
    requires_key = False

    def __init__(self, url: str = "http://localhost:11434"):
        self.url = url
        self._available = None

    def is_available(self) -> bool:
        if self._available is not None:
            return self._available
        try:
            req = urllib.request.Request(f"{self.url}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                self._available = resp.status == 200
        except:
            self._available = False
        return self._available

    def list_models(self) -> List[str]:
        try:
            req = urllib.request.Request(f"{self.url}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                return [m["name"] for m in data.get("models", [])]
        except:
            return []

    def call(self, messages: List[Dict], model: str = "llama3.1:8b") -> str:
        # ReAct only needs short JSON outputs — limit tokens for speed
        payload = json.dumps({
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 256,
                "num_ctx": 4096
            }
        }).encode()

        req = urllib.request.Request(
            f"{self.url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        # Local models can be slow (CPU inference). 300s = 5 min timeout.
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read().decode())
            return data["message"]["content"]


class OpenAICompatibleProvider(LLMProvider):
    """Provider for OpenAI-compatible APIs (OpenAI, Groq, OpenRouter, Together, etc.)"""
    name = "API (OpenAI-compatible)"
    requires_key = True

    def __init__(self, api_key: str = "", base_url: str = "https://api.openai.com/v1",
                 default_model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    def is_available(self) -> bool:
        return bool(self.api_key)

    def call(self, messages: List[Dict], model: str = None) -> str:
        if not self.api_key:
            _log("OpenAICompatibleProvider: no API key configured")
            raise RuntimeError("API key not configured")

        model = model or self.default_model
        url = f"{self.base_url}/chat/completions"
        _log(f"OpenAICompatibleProvider.call: model={model}, url={url}")

        payload = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 1024,
            "stream": False
        }).encode()

        _log(f"  Authorization: Bearer {self.api_key[:8]}... (full key length={len(self.api_key)})")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "AITroubleshooter/1.0"
            },
            method="POST"
        )

        status_code = 0
        resp_text = ""
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                status_code = resp.status
                resp_text = resp.read().decode(errors="replace")
                _log(f"HTTP {status_code}, body len={len(resp_text)}")
        except urllib.error.HTTPError as e:
            status_code = e.code
            body = e.read().decode(errors="replace")[:500]
            resp_text = body
            _log(f"HTTPError {e.code}: {body[:200]}")
            raise ProviderError(f"API HTTP {e.code}", raw_response=body, status_code=e.code)
        except urllib.error.URLError as e:
            _log(f"URLError: {e.reason}")
            raise ProviderError(f"API connection failed: {e.reason}", status_code=0)

        # Parse response
        try:
            data = json.loads(resp_text)
        except json.JSONDecodeError as e:
            _log(f"JSON decode error: {e}, body={resp_text[:300]}")
            raise ProviderError(f"API returned invalid JSON: {e}", raw_response=resp_text, status_code=status_code)

        # Expected format: {"choices": [{"message": {"content": "..."}}]}
        if isinstance(data, dict):
            if "choices" in data:
                choices = data["choices"]
                if isinstance(choices, list) and len(choices) > 0:
                    choice = choices[0]
                    if isinstance(choice, dict):
                        msg = choice.get("message") or choice.get("delta", {})
                        if isinstance(msg, dict):
                            content = msg.get("content", "")
                            if content is not None:
                                _log(f"Response OK, content len={len(content)}")
                                return content
                            _log(f"content is None in response: {resp_text[:300]}")
                            raise ProviderError("API returned null content", raw_response=resp_text, status_code=status_code)
                        _log(f"choices[0] has no message/delta: {resp_text[:300]}")
                        raise ProviderError(f"Unexpected choice format: keys={list(choice.keys())}", raw_response=resp_text, status_code=status_code)
                    _log(f"choices[0] not a dict: type={type(choice).__name__}")
                    raise ProviderError(f"choices[0] type={type(choice).__name__}", raw_response=resp_text, status_code=status_code)
                _log(f"choices is empty or not a list: type={type(choices).__name__}")
                raise ProviderError(f"Empty/invalid choices", raw_response=resp_text, status_code=status_code)

            if "error" in data:
                err = data["error"]
                err_msg = f"{err}" if isinstance(err, str) else f"{err.get('message', err)}"
                err_name = err.get("name", "") if isinstance(err, dict) else ""
                _log(f"API error: {err_name} - {err_msg}")
                raise ProviderError(f"API error: {err_msg}", raw_response=resp_text, status_code=status_code)

        _log(f"Unexpected response shape: {resp_text[:200]}")
        raise ProviderError(f"Unexpected API response", raw_response=resp_text, status_code=status_code)


# Preset configurations for popular providers
PROVIDER_PRESETS = {
    "OpenAI": {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "description": "Fast, cheap. GPT-4o-mini is ~$0.15/1M tokens"
    },
    "Groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.1-8b-instant",
        "description": "Very fast inference, free tier available"
    },
    "OpenRouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "openai/gpt-4o-mini",
        "description": "Access 200+ models with one API key"
    },
    "Together AI": {
        "base_url": "https://api.together.xyz/v1",
        "default_model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "description": "Good open-source model hosting"
    },
}


# ============================================================
# Agent Loop
# ============================================================

class AgentLoop:
    """LLM-driven agent loop with multiple provider support and rule-based fallback"""

    def __init__(self, provider: LLMProvider = None, model: str = "llama3.1:8b",
                 ollama_url: str = "http://localhost:11434"):
        self.model = model
        self.ollama_url = ollama_url
        self.conversation_history = []
        self.tool_implementations = _get_tool_implementations()
        self._ollama_available = None

        # Provider chain: first available wins
        if provider:
            self.providers = [provider]
        else:
            self.providers = [
                OllamaProvider(url=ollama_url),
            ]
        self._active_provider = None

    @property
    def active_provider(self) -> Optional[LLMProvider]:
        """Get the currently active (available) provider"""
        if self._active_provider:
            return self._active_provider
        for p in self.providers:
            if p.is_available():
                self._active_provider = p
                return p
        return None

    def set_providers(self, providers: List[LLMProvider]):
        """Set the provider chain (tried in order)"""
        self.providers = providers
        self._active_provider = None

    def add_api_provider(self, api_key: str, base_url: str = "https://api.openai.com/v1",
                         model: str = "gpt-4o-mini"):
        """Add an API provider as fallback after local Ollama"""
        api_provider = OpenAICompatibleProvider(api_key, base_url, model)
        self.providers.append(api_provider)
        self._active_provider = None

    def is_ollama_available(self) -> bool:
        """Check if Ollama is running (for backward compatibility)"""
        for p in self.providers:
            if isinstance(p, OllamaProvider) and p.is_available():
                return True
        return False

    def list_available_models(self) -> List[str]:
        """List models in the active Ollama provider"""
        for p in self.providers:
            if isinstance(p, OllamaProvider) and p.is_available():
                return p.list_models()
        return []

    def analyze(self, issue: str, rule_based_engine=None,
                step_callback=None) -> Dict[str, Any]:
        """
        Analyze an issue using the agent loop.
        Tries providers in order, falls back to rule_based_engine if none available.

        step_callback: optional fn(step_type: str, data: Any) called for each step:
            "thinking" -> data = str
            "tool_call" -> data = {"tool": name, "args": ...}
            "tool_result" -> data = {"tool": name, "result": ...}
            "answer" -> data = str
        """
        provider = self.active_provider
        if provider is None:
            if rule_based_engine:
                result = rule_based_engine.analyze_issue(issue, {})
                result["from_rule_engine"] = True
                return result
            return self._fallback_analysis(issue)

        if step_callback:
            step_callback("thinking", f"Using {provider.name}")

        self.conversation_history.append({"role": "user", "content": issue})

        try:
            return self._run_agent_loop(issue, step_callback)
        except Exception as e:
            _log(f"LLM error: {e}\n{traceback.format_exc()}")
            if isinstance(e, ProviderError):
                _log(f"ProviderError details: status={e.status_code}, raw={e.raw_response[:500]}")
            if step_callback:
                step_callback("thinking", f"LLM error: {e}. Falling back to rule engine.")
            if rule_based_engine:
                result = rule_based_engine.analyze_issue(issue, {})
                result["from_rule_engine"] = True
                return result
            return {
                "issue_type": "Analysis Error",
                "findings": [f"Analysis error: {str(e)}"],
                "recommendations": ["Check your API key or Ollama connection"],
                "next_steps": ["1. Verify provider settings", "2. Try again"],
                "severity": "Low",
                "reasoning": [],
                "actions": []
            }
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt with tool descriptions"""
        parts = []
        for t in TOOL_DEFINITIONS:
            name = t.get("name", t.get("nmae", "?"))  # Guard against typo in name
            desc = t.get("description", "?")
            parts.append(f"- {name}: {desc}")
        tool_descriptions = "\n".join(parts)
        return SYSTEM_PROMPT_TEMPLATE.format(tool_descriptions=tool_descriptions)
    
    def _run_agent_loop(self, issue: str, step_callback=None) -> Dict[str, Any]:
        """Run the ReAct agent loop"""
        provider = self.active_provider
        if provider is None:
            return self._fallback_analysis(issue)

        system_prompt = self._build_system_prompt()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": issue}
        ]
        
        max_loops = 8  # safety limit
        tool_results = []
        
        if step_callback:
            step_callback("thinking", "Reading your issue and planning investigation...")
        
        for loop_count in range(max_loops):
            if step_callback:
                provider_name = provider.name
                if "ollama" in provider_name.lower() or "local" in provider_name.lower():
                    step_callback("thinking", f"Waiting for local model to respond... (CPU inference can take 1-5 min)")
                else:
                    step_callback("thinking", f"Querying {provider_name}... (step {loop_count+1}/{max_loops})")
            
            # Get LLM response from the active provider
            _log(f"Loop {loop_count+1}: calling provider...")
            try:
                response = provider.call(messages, self.model)
            except Exception as e:
                _log(f"provider.call failed: {e}\n{traceback.format_exc()}")
                if isinstance(e, ProviderError) and e.raw_response:
                    _log(f"Raw response: {e.raw_response[:500]}")
                raise
            _log(f"Loop {loop_count+1}: got response len={len(response)}")
            content = response.strip()
            
            # Try to parse as JSON
            parsed = self._parse_llm_output(content)
            
            if parsed is None:
                if step_callback:
                    step_callback("thinking", "Asking LLM to use correct format...")
                messages.append({"role": "assistant", "content": content})
                messages.append({
                    "role": "user", 
                    "content": "Please output your response in the valid JSON format: "
                               '{"tool": "name", "args": {...}} or {"answer": "...", "findings": [...], "solutions": [...]}'
                })
                continue
            
            if "answer" in parsed:
                if step_callback:
                    step_callback("answer", parsed.get("answer", ""))
                return self._build_analysis_result(parsed, tool_results)
            
            if "tool" in parsed:
                tool_name = parsed["tool"]
                args = parsed.get("args", {})
                
                if step_callback:
                    step_callback("tool_call", {"tool": tool_name, "args": args})
                
                messages.append({"role": "assistant", "content": content})
                
                # Execute the tool
                if step_callback:
                    step_callback("thinking", f"Running {tool_name}...")
                result = self._execute_tool(tool_name, args)
                tool_results.append({"tool": tool_name, "result": result})
                if step_callback:
                    step_callback("tool_result", {"tool": tool_name, "result": result})
                
                # Feed result back to LLM
                result_str = json.dumps(result, default=str, indent=2)[:2000]
                messages.append({
                    "role": "user",
                    "content": f"Tool '{tool_name}' returned:\n```json\n{result_str}\n```\n\nWhat do you want to do next? Call another tool or give your answer."
                })
                continue
            
            # Unknown format — ask for clarification
            messages.append({"role": "assistant", "content": content})
            messages.append({
                "role": "user",
                "content": "I didn't understand that format. Please use the JSON format specified."
            })
        
        # Max loops reached — build what we have
        return {
            "issue_type": "General (limit reached)",
            "findings": [f"Investigated {len(tool_results)} aspects of the issue"] + 
                       [f"Tool: {r['tool']}" for r in tool_results],
            "recommendations": ["Try restarting your PC", "Run a full diagnostic"],
            "next_steps": ["1. Try the suggestions above", "2. Run a more detailed investigation"],
            "severity": "Low",
            "reasoning": [],
            "actions": []
        }
    
    def _parse_llm_output(self, text: str) -> Optional[Dict]:
        """Parse JSON from LLM output, handling markdown code blocks. Only returns dict or None."""
        candidates = []

        # Try extracting from ```json ... ``` block first
        m = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
        if m:
            candidates.append(m.group(1).strip())

        # Try whole text
        stripped = text.strip()
        if stripped.startswith("{"):
            candidates.append(stripped)

        # Try finding {...} with regex
        m = re.search(r'\{.*\}', text, re.DOTALL)
        if m:
            candidates.append(m.group(0))

        for candidate in candidates:
            try:
                result = json.loads(candidate)
                if isinstance(result, dict):
                    return result
            except json.JSONDecodeError:
                continue

        return None
    
    def _call_ollama(self, messages: List[Dict]) -> str:
        """Call Ollama API"""
        payload = json.dumps({
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": 0.1,
            "max_tokens": 1024
        }).encode()
        
        req = urllib.request.Request(
            f"{self.ollama_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
            return data["message"]["content"]
    
    def _execute_tool(self, name: str, args: Dict) -> Any:
        """Execute a tool by name with args"""
        impl = self.tool_implementations.get(name)
        if impl is None:
            return {"error": f"Unknown tool: {name}"}
        try:
            return impl(args)
        except Exception as e:
            return {"error": str(e)}
    
    def _build_analysis_result(self, parsed: Dict, tool_results: List[Dict]) -> Dict:
        """Build the final analysis result from LLM answer"""
        todos = parsed.get("todos", [])
        return {
            "issue_type": "AI Analysis",
            "findings": parsed.get("findings", []),
            "recommendations": parsed.get("solutions", []),
            "todos": todos,
            "reasoning": [f"Used {len(tool_results)} tool(s) to investigate"],
            "actions": [],
            "next_steps": [
                "1. Try the solutions above",
                "2. Let me know if the issue persists"
            ] if not todos else [
                "1. Review the suggested action steps below",
                "2. Each step requires your permission before execution",
                "3. Follow the prompts to apply fixes"
            ],
            "severity": self._estimate_severity(parsed.get("findings", [])),
            "llm_answer": parsed.get("answer", ""),
            "tools_used": [r["tool"] for r in tool_results]
        }
    
    def _estimate_severity(self, findings: List[str]) -> str:
        findings_text = " ".join(findings).lower()
        if any(w in findings_text for w in ["critical", "danger", "urgent", "bad sector", "corrupt"]):
            return "High"
        if any(w in findings_text for w in ["warning", "error", "fail", "missing"]):
            return "Medium"
        return "Low"
    
    def _fallback_analysis(self, issue: str) -> Dict:
        """Minimal fallback when neither LLM nor engine is available"""
        from diagnostics import ErrorMessageParser
        error_info = ErrorMessageParser.parse(issue)
        if error_info:
            return {
                "issue_type": error_info["title"],
                "findings": [error_info["description"]],
                "recommendations": error_info["solutions"],
                "next_steps": ["1. Try the solutions above"],
                "severity": "Medium",
                "reasoning": [],
                "actions": []
            }
        return {
            "issue_type": "General Issue",
            "findings": ["No specific error pattern detected"],
            "recommendations": [
                "Make sure Ollama is installed and running",
                "Install Ollama from https://ollama.ai",
                "Pull a model: ollama pull llama3.1:8b"
            ],
            "next_steps": ["1. Install Ollama", "2. Try again with LLM-powered analysis"],
            "severity": "Low",
            "reasoning": [],
            "actions": []
        }
