"""
Agent Loop - LLM-driven troubleshooting agent with Ollama integration
ReAct pattern: LLM reasons -> picks tool -> tool executes -> LLM evaluates -> repeats or answers
"""
import json
import os
import re
import shutil
import subprocess
import urllib.request
import urllib.error
import time
from typing import Dict, List, Any, Optional, Callable
from diagnostics import WindowsDiagnostics, ErrorMessageParser


# ============================================================
# Tools the LLM can call
# ============================================================

TOOL_DEFINITIONS = [
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
        "description": "Get top 5 CPU-consuming and top 5 memory-consuming processes",
        "args": {}
    },
    {
        "name": "parse_error_message",
        "description": "Parse a Windows error message text and identify the specific error type and solutions",
        "args": {"text": "The error message text to analyze"}
    },
    {
        "name": "run_defender_scan",
        "description": "Run a Windows Defender quick scan to check for malware (takes 1-5 minutes)",
        "args": {}
    },
    {
        "name": "run_chkdsk",
        "description": "Run chkdsk in read-only mode to check disk for errors and bad sectors",
        "args": {"drive": "Drive letter to check (default: C:)"}
    },
    {
        "name": "get_event_log_crashes",
        "description": "Get recent application crash events from Windows Event Log",
        "args": {}
    },
    {
        "name": "get_system_uptime",
        "description": "Get how long the system has been running since last boot",
        "args": {}
    },
    {
        "name": "get_windows_defender_status",
        "description": "Check if Windows Defender is active and when it last scanned",
        "args": {}
    },
]


def _get_tool_implementations() -> Dict[str, Callable]:
    """Map tool names to actual functions"""
    d = WindowsDiagnostics()
    return {
        "get_system_info": lambda args: d.get_system_info(),
        "get_cpu_info": lambda args: d.get_cpu_info(),
        "get_memory_info": lambda args: d.get_memory_info(),
        "get_disk_info": lambda args: d.get_disk_info(),
        "get_top_processes": lambda args: d.get_top_processes(),
        "parse_error_message": lambda args: ErrorMessageParser.parse(args.get("text", "")),
        "run_defender_scan": lambda args: d.run_windows_defender_scan(),
        "run_chkdsk": lambda args: d.run_chkdsk(args.get("drive", "C:")),
        "get_event_log_crashes": lambda args: d.get_recent_app_crashes(),
        "get_system_uptime": lambda args: d.get_system_uptime(),
        "get_windows_defender_status": lambda args: d.get_windows_defender_status(),
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
  "solutions": ["Solution 1", "Solution 2"]}}
```

## Rules
- Always use tools to investigate — don't guess
- Call one tool at a time (I'll give you the result)
- Stop calling tools once you have enough info to help the user
- If a tool fails, try a different approach
- If the user's issue is unclear, use get_system_info() first to understand their system state
- Never output anything other than the JSON format above"""


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
            raise RuntimeError("API key not configured")

        model = model or self.default_model
        payload = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 1024,
            "stream": False
        }).encode()

        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "AITroubleshooter/1.0"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())
            return data["choices"][0]["message"]["content"]


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
        tool_descriptions = "\n".join(
            f"- {t['name']}: {t['description']}" 
            for t in TOOL_DEFINITIONS
        )
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
            response = provider.call(messages, self.model)
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
        """Parse JSON from LLM output, handling markdown code blocks"""
        # Try extracting from ```json ... ``` block first
        m = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1).strip())
            except json.JSONDecodeError:
                pass
        
        # Try parsing whole text as JSON
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        
        # Try finding {...} with regex
        m = re.search(r'\{.*\}', text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
        
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
        return {
            "issue_type": "AI Analysis",
            "findings": parsed.get("findings", []),
            "recommendations": parsed.get("solutions", []),
            "reasoning": [f"Used {len(tool_results)} tool(s) to investigate"],
            "actions": [],
            "next_steps": [
                "1. Try the solutions above",
                "2. Let me know if the issue persists"
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
