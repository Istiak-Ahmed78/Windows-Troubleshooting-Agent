"""
Windows Diagnostics Module
"""
import psutil
import os
import subprocess
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional


class WindowsDiagnostics:
    """System diagnostics and action execution"""
    
    def __init__(self):
        self.diagnostics_cache = {}
        self.last_update = None
    
    def get_system_info(self) -> Dict[str, Any]:
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disk": self.get_disk_info(),
            "processes": self.get_top_processes(),
            "network": self.get_network_info(),
            "battery": self.get_battery_info(),
        }
    
    def get_cpu_info(self) -> Dict[str, Any]:
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            per_cpu = psutil.cpu_percent(percpu=True, interval=1)
            temp = self.get_cpu_temperature()
            return {
                "usage_percent": cpu_percent,
                "count": cpu_count,
                "frequency": {
                    "current": cpu_freq.current if cpu_freq else None,
                    "min": cpu_freq.min if cpu_freq else None,
                    "max": cpu_freq.max if cpu_freq else None,
                },
                "per_cpu_usage": per_cpu,
                "temperature": temp,
                "status": self.analyze_cpu_health(cpu_percent, temp)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_cpu_temperature(self) -> Optional[float]:
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    if entries:
                        return entries[0].current
        except:
            pass
        return None
    
    def analyze_cpu_health(self, usage: float, temp: Optional[float]) -> str:
        status = "Good"
        if usage > 80:
            status = "High Usage"
        elif usage > 60:
            status = "Moderate Usage"
        if temp and temp > 85:
            status = "High Temperature"
        elif temp and temp > 70:
            status = "Elevated Temperature"
        return status
    
    def get_memory_info(self) -> Dict[str, Any]:
        try:
            virtual_memory = psutil.virtual_memory()
            return {
                "total": virtual_memory.total,
                "available": virtual_memory.available,
                "used": virtual_memory.used,
                "percent": virtual_memory.percent,
                "status": self.analyze_memory_health(virtual_memory.percent)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_memory_health(self, usage_percent: float) -> str:
        if usage_percent > 90:
            return "Critical - Low Memory"
        elif usage_percent > 80:
            return "Warning - High Memory Usage"
        elif usage_percent > 60:
            return "Moderate Memory Usage"
        return "Good"
    
    def get_disk_info(self) -> Dict[str, Any]:
        try:
            partitions = psutil.disk_partitions()
            disk_info = []
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent,
                        "status": self.analyze_disk_health(usage.percent)
                    })
                except PermissionError:
                    continue
            return {"partitions": disk_info}
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_disk_health(self, usage_percent: float) -> str:
        if usage_percent > 95:
            return "Critical - Almost Full"
        elif usage_percent > 85:
            return "Warning - Low Space"
        elif usage_percent > 70:
            return "Moderate Usage"
        return "Good"
    
    def get_top_processes(self, top_n: int = 10) -> List[Dict[str, Any]]:
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            cpu_p = sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:5]
            mem_p = sorted(processes, key=lambda x: x.get('memory_percent', 0), reverse=True)[:5]
            return {"top_cpu": cpu_p, "top_memory": mem_p}
        except Exception as e:
            return {"error": str(e)}
    
    def get_network_info(self) -> Dict[str, Any]:
        try:
            interfaces = psutil.net_if_stats()
            net_io = psutil.net_io_counters()
            return {
                "interfaces": {name: {"is_up": stats.isup, "speed": stats.speed, "mtu": stats.mtu} for name, stats in interfaces.items()},
                "io_counters": {"bytes_sent": net_io.bytes_sent, "bytes_recv": net_io.bytes_recv}
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_battery_info(self) -> Dict[str, Any]:
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {"percent": battery.percent, "power_plugged": battery.power_plugged}
            return {"status": "No battery detected"}
        except Exception as e:
            return {"error": str(e)}
    
    # ========== ACTION EXECUTORS ==========
    
    def run_windows_defender_scan(self) -> Dict[str, Any]:
        """Actually run Windows Defender quick scan"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Start-MpScan -ScanType QuickScan"],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                return {"status": "completed", "message": "Windows Defender quick scan completed"}
            return {"status": "error", "message": result.stderr.strip() or "Scan may have failed"}
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Scan timed out"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def run_chkdsk(self, drive: str = "C:") -> Dict[str, Any]:
        """Run chkdsk in read-only mode (no repair)"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", f"chkdsk {drive}"],
                capture_output=True, text=True, timeout=60
            )
            output = result.stdout + result.stderr
            # Extract key info
            errors_found = "No further action" not in output and "no errors" not in output.lower()
            bad_sectors = "bad sectors" in output.lower() or "unrecoverable" in output.lower()
            return {
                "status": "completed" if result.returncode == 0 else "issues_found",
                "output": output[:500],
                "has_errors": errors_found,
                "has_bad_sectors": bad_sectors
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "chkdsk timed out"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def check_file_associations(self) -> Dict[str, Any]:
        """Check default file associations for common extensions"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", 
                 "Get-ChildItem 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty PSChildName"],
                capture_output=True, text=True, timeout=15
            )
            extensions = [e.strip() for e in result.stdout.split('\n') if e.strip()]
            return {"extensions_found": len(extensions), "extensions": extensions[:20]}
        except Exception as e:
            return {"error": str(e)}
    
    def check_specific_app_association(self, extension: str = ".exe") -> Dict[str, Any]:
        """Check what app is associated with a given extension"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", 
                 f"(Get-ItemProperty 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts\\{extension}\\UserChoice' -Name ProgId -ErrorAction SilentlyContinue).ProgId"],
                capture_output=True, text=True, timeout=10
            )
            prog_id = result.stdout.strip()
            if prog_id:
                return {"extension": extension, "associated_app": prog_id}
            return {"extension": extension, "associated_app": None, "note": "No user choice set (using system default)"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_windows_defender_status(self) -> Dict[str, Any]:
        """Get Windows Defender status"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", 
                 "Get-MpComputerStatus | Select-Object AntivirusEnabled,RealTimeProtectionEnabled,AmServiceEnabled,NISEnabled,LastQuickScanDateTime,LastFullScanDateTime | ConvertTo-Json"],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            return {"error": "Could not get Defender status"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_recent_app_crashes(self) -> List[Dict[str, Any]]:
        """Get recent application crash events from Event Log"""
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-WinEvent -FilterHashtable @{LogName='Application'; ProviderName='Application Error'} -MaxEvents 5 -ErrorAction SilentlyContinue | Select-Object TimeCreated, Message | ConvertTo-Json"],
                capture_output=True, text=True, timeout=15
            )
            if result.stdout.strip():
                data = json.loads(result.stdout)
                crashes = data if isinstance(data, list) else [data]
                parsed = []
                for crash in crashes:
                    msg = crash.get('Message', '')
                    app_match = re.search(r'Faulting application name:\s*(.+?)[\r\n]', msg)
                    app_name = app_match.group(1).strip() if app_match else 'Unknown'
                    exe_match = re.search(r'Faulting module name:\s*(.+?)[\r\n]', msg)
                    module = exe_match.group(1).strip() if exe_match else 'Unknown'
                    parsed.append({
                        "time": crash.get('TimeCreated', ''),
                        "application": app_name,
                        "faulting_module": module
                    })
                return parsed
            return []
        except Exception as e:
            return []
    
    def get_system_uptime(self) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "(Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime | Select-Object -ExpandProperty TotalHours"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                uptime_hours = float(result.stdout.strip())
                return {
                    "uptime_hours": round(uptime_hours, 2),
                    "uptime_days": round(uptime_hours / 24, 2),
                    "recommendation": "Restart recommended" if uptime_hours > 168 else "Normal"
                }
            return {"error": "Could not determine"}
        except Exception as e:
            return {"error": str(e)}


class ErrorMessageParser:
    """Parses Windows error messages and returns specific solutions"""
    
    ERROR_PATTERNS = [
        {
            "patterns": [
                r"file does not have an app associated",
                r"does not have an app associated",
                r"create an association in the Default Apps",
                r"default apps settings page",
                r"no app associated"
            ],
            "type": "file_association_broken",
            "title": "File Association Broken",
            "description": "Windows doesn't know which app to use to open this file type.",
            "solutions": [
                "Right-click the file -> 'Open with' -> 'Choose another app' -> Select the correct app -> Check 'Always use this app'",
                "Go to Settings -> Apps -> Default apps -> Choose defaults by file type",
                "Run: 'ms-settings:defaultapps' (Win+R) to open Default Apps settings",
                "Reinstall the application to restore file associations",
                "Check if the shortcut (.lnk) file is corrupted — delete and recreate it"
            ]
        },
        {
            "patterns": [
                r"access is denied",
                r"permission denied",
                r"you don't have permission",
                r"requires administrator",
                r"run as administrator"
            ],
            "type": "permission_denied",
            "title": "Permission Issue",
            "description": "The application doesn't have sufficient permissions to run.",
            "solutions": [
                "Right-click the application -> 'Run as administrator'",
                "Right-click shortcut -> Properties -> Advanced -> Check 'Run as administrator'",
                "Check if your user account has administrator privileges",
                "Disable User Account Control (UAC) temporarily: Move slider to 'Never notify'"
            ]
        },
        {
            "patterns": [
                r"0xc000007b",
                r"application was unable to start correctly",
                r"0xc00000",
                r"0x000000"
            ],
            "type": "dependency_missing",
            "title": "Missing Runtime Library",
            "description": "A required system library (DLL) or runtime is missing or corrupted.",
            "solutions": [
                "Install/repair Microsoft Visual C++ Redistributable (all-in-one: vc_redist.x64.exe)",
                "Install .NET Framework: https://dotnet.microsoft.com/download/dotnet-framework",
                "Run: 'sfc /scannow' in Command Prompt (Admin) to repair system files",
                "Reinstall the application to restore missing files",
                "Check Windows Update for important updates"
            ]
        },
        {
            "patterns": [
                r"dll is missing",
                r"could not be found",
                r"not a valid Win32 application",
                r"module not found",
                r"not found"
            ],
            "type": "missing_file",
            "title": "Missing File or DLL",
            "description": "A required file or DLL is missing from the system.",
            "solutions": [
                "Reinstall the application to restore missing files",
                "Run: 'sfc /scannow' in Command Prompt (Admin)",
                "Run: 'DISM /Online /Cleanup-Image /RestoreHealth' in Command Prompt (Admin)",
                "Check if antivirus quarantined the file — restore if found",
                "Download and reinstall the application from official source"
            ]
        },
        {
            "patterns": [
                r"has stopped working",
                r"stopped responding",
                r"not responding",
                r"hang|freeze|frozen"
            ],
            "type": "app_crash",
            "title": "Application Crash",
            "description": "The application has stopped working unexpectedly.",
            "solutions": [
                "Open Task Manager (Ctrl+Shift+Esc) -> End the application process -> Restart",
                "Update the application to the latest version",
                "Update your graphics drivers",
                "Run: 'eventvwr.msc' -> Windows Logs -> Application -> Find the error",
                "Check for conflicting software (antivirus, other apps)"
            ]
        },
        {
            "patterns": [
                r"virus|malware|trojan|spyware|threat|infected",
                r"windows defender",
                r"scan for virus"
            ],
            "type": "malware_concern",
            "title": "Malware Concern",
            "description": "You're concerned about malware or viruses.",
            "solutions": [
                "Run Windows Defender Quick Scan: Start -> 'Virus & threat protection' -> Quick scan",
                "Run Windows Defender Full Scan for thorough check",
                "Download and run Malwarebytes (free version) for second opinion",
                "Check startup programs: Task Manager -> Startup -> Disable suspicious entries",
                "Check browser extensions for suspicious add-ons"
            ],
            "action": "run_defender_scan"
        }
    ]
    
    @staticmethod
    def parse(text: str) -> Optional[Dict[str, Any]]:
        """Parse error text and return matching error info"""
        text_lower = text.lower()
        for error in ErrorMessageParser.ERROR_PATTERNS:
            for pattern in error["patterns"]:
                if re.search(pattern, text_lower):
                    return error
        return None
    
    @staticmethod
    def extract_app_name(text: str) -> str:
        """Try to extract an application name from user text"""
        # Check for direct mentions: "APP is not opening", "open APP", "APP wont start"
        patterns = [
            r"(\w+)\s+(?:application\s+)?(?:is\s+)?(?:not\s+)?(?:opening|starting|working|launching|crashed|failing)",
            r"(\w+)\s+(?:won't|wont|doesn't|doesnt|isn't|isnt)\s+(?:open|start|work|launch|run)",
            r"(?:open|start|launch|run)\s+(?:the\s+)?(\w+)",
            r"(?:cannot|can't|cant)\s+(?:open|start|launch|run)\s+(\w+)",
        ]
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                name = m.group(1).capitalize()
                # Filter out common words
                if name.lower() not in ["application", "app", "the", "file", "this", "that", "windows"]:
                    return name
        return ""


def format_bytes(bytes_value: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"
