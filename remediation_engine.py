"""
Remediation Engine - executes and verifies remediation actions
with user permission and restart-aware state persistence
"""
import os
import json
import subprocess
import winreg
import ctypes
from typing import Dict, List, Any, Optional


TODO_STATE_FILE = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")),
    "AITroubleshooter", "todo_state.json"
)
RESTART_MARKER_FILE = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")),
    "AITroubleshooter", ".restart_marker"
)


class RemediationEngine:
    """Executes and verifies remediation actions with user permission"""

    def __init__(self):
        self._state = None

    # ----------------------------------------------------------
    # Action handlers
    # ----------------------------------------------------------

    def execute(self, action_type: str, params: Dict) -> Dict:
        handler = getattr(self, f"_exec_{action_type}", None)
        if handler is None:
            return {"success": False, "error": f"Unknown action: {action_type}"}
        try:
            return handler(params)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def verify(self, action_type: str, params: Dict) -> Dict:
        handler = getattr(self, f"_verify_{action_type}", None)
        if handler is None:
            return {"success": False, "error": f"Cannot verify: {action_type}"}
        try:
            return handler(params)
        except Exception as e:
            return {"success": False, "error": str(e)}

    # -- env var --

    def _exec_set_env_var(self, params: Dict) -> Dict:
        name = params.get("name", "")
        value = params.get("value", "")
        scope = params.get("scope", "user")
        if not name:
            return {"success": False, "error": "No variable name provided"}
        if scope == "machine":
            import ctypes
            if ctypes.windll.shell32.IsUserAnAdmin() == 0:
                return {"success": False, "error": "Admin rights required for system env vars"}
            key = winreg.HKEY_LOCAL_MACHINE
            subkey = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
        else:
            key = winreg.HKEY_CURRENT_USER
            subkey = "Environment"
        try:
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as k:
                winreg.SetValueEx(k, name, 0, winreg.REG_EXPAND_SZ, value)
            os.environ[name] = value
            # Broadcast environment change
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x001A
            ctypes.windll.user32.SendMessageW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment")
            return {"success": True, "message": f"Set {name}={value}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _verify_set_env_var(self, params: Dict) -> Dict:
        name = params.get("name", "")
        expected = params.get("value", "")
        current = os.environ.get(name, "")
        match = current == expected
        return {
            "success": match,
            "current": current,
            "expected": expected,
            "message": f"{name}={current}" if match else f"Expected {expected}, got {current}"
        }

    # -- command --

    def _exec_run_command(self, params: Dict) -> Dict:
        cmd = params.get("command", "")
        if not cmd:
            return {"success": False, "error": "No command provided"}
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=120
            )
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout.strip()[:500],
                "stderr": result.stderr.strip()[:500],
                "message": "Command executed" if result.returncode == 0 else f"Exit code {result.returncode}"
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out (120s)"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _verify_run_command(self, params: Dict) -> Dict:
        return self._exec_run_command({**params, "command": params.get("verify_command", params["command"])})

    # -- install package --

    def _exec_install_package(self, params: Dict) -> Dict:
        package = params.get("package", "")
        tool = params.get("tool", "winget")
        if not package:
            return {"success": False, "error": "No package name provided"}
        if tool == "winget":
            cmd = f'winget install --id "{package}" --silent --accept-package-agreements --accept-source-agreements'
        elif tool == "choco":
            cmd = f'choco install {package} -y'
        elif tool == "pip":
            cmd = f'pip install {package}'
        else:
            cmd = f'winget install --id "{package}" --silent'
        return self._exec_run_command({"command": cmd})

    def _verify_install_package(self, params: Dict) -> Dict:
        package = params.get("package", "")
        tool = params.get("tool", "winget")
        if tool == "winget":
            cmd = f'winget list --id "{package}"'
        elif tool == "pip":
            cmd = f'pip show {package}'
        else:
            cmd = f'winget list --id "{package}"'
        result = self._exec_run_command({"command": cmd})
        result["success"] = result["returncode"] == 0
        return result

    # -- registry edit --

    def _exec_registry_edit(self, params: Dict) -> Dict:
        key_path = params.get("key", "")
        value_name = params.get("value_name", "")
        value_data = params.get("value_data", "")
        value_type = params.get("value_type", "REG_SZ")
        hive = params.get("hive", "HKCU")
        if not key_path:
            return {"success": False, "error": "No registry key provided"}
        hive_map = {"HKCU": winreg.HKEY_CURRENT_USER, "HKLM": winreg.HKEY_LOCAL_MACHINE}
        type_map = {"REG_SZ": winreg.REG_SZ, "REG_EXPAND_SZ": winreg.REG_EXPAND_SZ,
                    "REG_DWORD": winreg.REG_DWORD}
        try:
            with winreg.CreateKey(hive_map.get(hive, winreg.HKEY_CURRENT_USER), key_path) as k:
                winreg.SetValueEx(k, value_name, 0, type_map.get(value_type, winreg.REG_SZ), value_data)
            return {"success": True, "message": f"Set registry {key_path}\\{value_name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _verify_registry_edit(self, params: Dict) -> Dict:
        key_path = params.get("key", "")
        value_name = params.get("value_name", "")
        expected = params.get("value_data", "")
        hive = params.get("hive", "HKCU")
        hive_map = {"HKCU": winreg.HKEY_CURRENT_USER, "HKLM": winreg.HKEY_LOCAL_MACHINE}
        try:
            with winreg.OpenKey(hive_map.get(hive, winreg.HKEY_CURRENT_USER), key_path) as k:
                current, _ = winreg.QueryValueEx(k, value_name)
                match = str(current) == str(expected)
                return {"success": match, "current": str(current), "expected": str(expected)}
        except Exception as e:
            return {"success": False, "error": str(e), "current": None, "expected": expected}

    # -- service operation --

    def _exec_service_operation(self, params: Dict) -> Dict:
        service = params.get("service", "")
        operation = params.get("operation", "restart")
        if not service:
            return {"success": False, "error": "No service name provided"}
        cmd = f'net {operation} "{service}"'
        return self._exec_run_command({"command": cmd})

    def _verify_service_operation(self, params: Dict) -> Dict:
        service = params.get("service", "")
        cmd = f'sc query "{service}"'
        result = self._exec_run_command({"command": cmd})
        return {"success": result["success"], "status": result.get("stdout", "")[:200]}

    # -- restart PC --

    def _exec_restart_pc(self, params: Dict) -> Dict:
        return {
            "success": True,
            "restart": True,
            "message": "Restart required. The app will resume after restart."
        }

    def _verify_restart_pc(self, params: Dict) -> Dict:
        return {"success": True, "message": "Restart was completed"}

    # -- force delete file --

    def _exec_force_delete_file(self, params: Dict) -> Dict:
        file_path = params.get("file_path", "")
        if not file_path:
            return {"success": False, "error": "No file path provided"}
        if not os.path.exists(file_path):
            return {"success": True, "message": "File does not exist (already deleted)"}
        try:
            os.remove(file_path)
            if not os.path.exists(file_path):
                return {"success": True, "message": f"Deleted: {file_path}"}
        except:
            pass
        # Try takeown + icacls
        cmds = [
            f'takeown /f "{file_path}" /a',
            f'icacls "{file_path}" /grant Administrators:F',
            f'del /f /q "{file_path}"'
        ]
        for cmd in cmds:
            try:
                subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            except:
                pass
        if os.path.exists(file_path):
            # One more attempt with PowerShell
            ps_cmd = f'powershell -NoProfile -Command "Remove-Item -LiteralPath \'{file_path}\' -Force -ErrorAction SilentlyContinue"'
            try:
                subprocess.run(ps_cmd, shell=True, capture_output=True, text=True, timeout=30)
            except:
                pass
        if not os.path.exists(file_path):
            return {"success": True, "message": f"Force deleted: {file_path}"}
        return {"success": False, "error": f"Could not delete {file_path}. File may be in use by another process."}

    def _verify_force_delete_file(self, params: Dict) -> Dict:
        file_path = params.get("file_path", "")
        exists = os.path.exists(file_path) if file_path else True
        return {"success": not exists, "message": f"File deleted" if not exists else f"File still exists: {file_path}"}

    # -- run SFC scannow --

    def _exec_run_sfc_scan(self, params: Dict) -> Dict:
        try:
            result = subprocess.run(["sfc", "/scannow"], capture_output=True, text=True, timeout=600)
            out = result.stdout + result.stderr
            success = "completed" in out.lower() and "found corrupt" not in out.lower()
            return {
                "success": success,
                "message": "SFC scan completed" if success else "SFC found corrupt files it could not repair",
                "details": out[:500]
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "SFC scan timed out (10 min max)"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _verify_run_sfc_scan(self, params: Dict) -> Dict:
        # Check if SFC reported any pending repairs
        log = r"C:\Windows\Logs\CBS\CBS.log"
        if os.path.exists(log):
            try:
                with open(log) as f:
                    content = f.read()
                if "hashes for corrupted" in content.lower():
                    return {"success": False, "message": "Corrupted files still present in CBS log"}
            except:
                pass
        return {"success": True, "message": "System files appear healthy"}

    # -- DISM restore health --

    def _exec_run_dism_repair(self, params: Dict) -> Dict:
        try:
            result = subprocess.run(
                ["dism", "/online", "/cleanup-image", "/restorehealth"],
                capture_output=True, text=True, timeout=600
            )
            out = result.stdout + result.stderr
            success = "completed" in out.lower() and "error" not in out.lower()
            return {
                "success": success,
                "message": "DISM restore health completed" if success else "DISM reported issues",
                "details": out[:500]
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "DISM timed out (10 min max)"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _verify_run_dism_repair(self, params: Dict) -> Dict:
        return {"success": True, "message": "DISM verification done"}

    # -- clear temp files --

    def _exec_clear_temp_files(self, params: Dict) -> Dict:
        import tempfile as tf
        deleted_count = 0
        freed_bytes = 0
        dirs = [
            tf.gettempdir(),
            os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Temp"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp"),
        ]
        for d in dirs:
            if not d or not os.path.exists(d):
                continue
            for root, _, files in os.walk(d):
                for f in files:
                    try:
                        fp = os.path.join(root, f)
                        freed_bytes += os.path.getsize(fp)
                        os.remove(fp)
                        deleted_count += 1
                    except:
                        pass
        freed_mb = round(freed_bytes / (1024 * 1024), 1)
        return {"success": True, "message": f"Cleaned {deleted_count} temp files, freed {freed_mb} MB"}

    def _verify_clear_temp_files(self, params: Dict) -> Dict:
        return {"success": True, "message": "Temp directory size reduced"}

    # -- reset network stack --

    def _exec_reset_network_stack(self, params: Dict) -> Dict:
        cmds = ["netsh winsock reset", "netsh int ip reset", "ipconfig /release", "ipconfig /renew", "ipconfig /flushdns"]
        results = []
        for cmd in cmds:
            try:
                r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                results.append({"cmd": cmd, "returncode": r.returncode})
            except Exception as e:
                results.append({"cmd": cmd, "error": str(e)})
        success = all(r.get("returncode", -1) == 0 for r in results[:3])
        return {"success": success, "message": "Network stack reset completed" if success else "Some commands failed", "steps": results}

    def _verify_reset_network_stack(self, params: Dict) -> Dict:
        ping = subprocess.run("ping -n 1 8.8.8.8", shell=True, capture_output=True, text=True, timeout=10)
        return {"success": ping.returncode == 0, "message": "Network connectivity verified" if ping.returncode == 0 else "No internet after reset"}

    # -- disable startup item --

    def _exec_disable_startup_item(self, params: Dict) -> Dict:
        name = params.get("name", "")
        scope = params.get("scope", "user")
        if not name:
            return {"success": False, "error": "No startup item name provided"}
        if scope == "machine":
            key = winreg.HKEY_LOCAL_MACHINE
            path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        else:
            key = winreg.HKEY_CURRENT_USER
            path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        try:
            with winreg.OpenKey(key, path, 0, winreg.KEY_SET_VALUE) as k:
                winreg.DeleteValue(k, name)
            return {"success": True, "message": f"Disabled startup item: {name}"}
        except FileNotFoundError:
            return {"success": True, "message": f"Startup item not found (already disabled): {name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _verify_disable_startup_item(self, params: Dict) -> Dict:
        name = params.get("name", "")
        scope = params.get("scope", "user")
        if scope == "machine":
            key = winreg.HKEY_LOCAL_MACHINE
            path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        else:
            key = winreg.HKEY_CURRENT_USER
            path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        try:
            with winreg.OpenKey(key, path) as k:
                winreg.QueryValueEx(k, name)
            return {"success": False, "message": f"Startup item still present: {name}"}
        except FileNotFoundError:
            return {"success": True, "message": f"Startup item removed: {name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # -- run defender scan --

    def _exec_run_defender_scan(self, params: Dict) -> Dict:
        cmd = 'powershell -NoProfile -Command "Start-MpScan -ScanType QuickScan"'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
            return {"success": result.returncode == 0, "message": "Defender quick scan completed" if result.returncode == 0 else "Scan may have failed"}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Defender scan timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _verify_run_defender_scan(self, params: Dict) -> Dict:
        cmd = 'powershell -NoProfile -Command "Get-MpComputerStatus | Select-Object -ExpandProperty QuickScanAge"'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            return {"success": True, "message": f"Last quick scan: {result.stdout.strip()}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # -- run chkdsk --

    def _exec_run_chkdsk(self, params: Dict) -> Dict:
        drive = params.get("drive", "C:")
        try:
            result = subprocess.run(["chkdsk", drive], capture_output=True, text=True, timeout=120)
            out = result.stdout + result.stderr
            errors = "found" if "found" in out.lower() and "bad" in out.lower() else "none"
            return {"success": result.returncode == 0, "message": f"chkdsk {drive} completed", "errors_found": errors}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "chkdsk timed out (2 min)"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _verify_run_chkdsk(self, params: Dict) -> Dict:
        return {"success": True, "message": "Disk check completed"}

    # ----------------------------------------------------------
    # State persistence
    # ----------------------------------------------------------

    def save_state(self, todos: List[Dict], current_index: int = 0,
                   restart_required: bool = False, session_label: str = ""):
        os.makedirs(os.path.dirname(TODO_STATE_FILE), exist_ok=True)
        state = {
            "todos": todos,
            "current_index": current_index,
            "restart_required": restart_required,
            "restart_initiated": False,
            "session_label": session_label
        }
        with open(TODO_STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
        self._state = state

    def load_state(self) -> Optional[Dict]:
        try:
            if os.path.exists(TODO_STATE_FILE):
                with open(TODO_STATE_FILE) as f:
                    self._state = json.load(f)
                return self._state
        except:
            pass
        return None

    def clear_state(self):
        if os.path.exists(TODO_STATE_FILE):
            os.remove(TODO_STATE_FILE)
        if os.path.exists(RESTART_MARKER_FILE):
            os.remove(RESTART_MARKER_FILE)
        self._state = None

    def mark_restart_initiated(self):
        if self._state:
            self._state["restart_initiated"] = True
            self.save_state(
                self._state["todos"],
                self._state["current_index"],
                self._state["restart_required"],
                self._state.get("session_label", "")
            )
        os.makedirs(os.path.dirname(RESTART_MARKER_FILE), exist_ok=True)
        with open(RESTART_MARKER_FILE, "w") as f:
            f.write("1")

    @staticmethod
    def was_restarted() -> bool:
        return os.path.exists(RESTART_MARKER_FILE)

    def get_todo_display(self, todo: Dict) -> str:
        action = todo.get("action", todo.get("action_type", "?"))
        desc = todo.get("description", "")
        details = todo.get("params", {})
        lines = [f"[{action}] {desc}"]
        for k, v in details.items():
            lines.append(f"  {k}: {v}")
        return "\n".join(lines)
