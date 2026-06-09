"""
Advanced Diagnostics Module
Additional system analysis and optimization utilities
"""
import subprocess
import json
import re
import os
import shutil
import winreg
import tempfile
from typing import Dict, List, Any, Optional
from datetime import datetime


def _run_cmd(cmd: str, timeout: int = 30) -> str:
    """Run a system command and return stdout"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip() or result.stderr.strip()
    except subprocess.TimeoutExpired:
        return "Command timed out"
    except Exception as e:
        return f"Error: {e}"


class AdvancedDiagnostics:
    """Advanced system diagnostics and analysis"""
    
    @staticmethod
    def get_windows_updates_status() -> Dict[str, Any]:
        """Check Windows Update status"""
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 5 | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout) if result.stdout.strip() else []
                return {
                    "recent_updates": data if isinstance(data, list) else [data],
                    "status": "Updates found" if data else "No recent updates"
                }
            return {"error": "Could not fetch updates"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def check_antivirus_status() -> Dict[str, Any]:
        """Check Windows Defender status"""
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-MpComputerStatus | Select-Object AntivirusEnabled,RealTimeProtectionEnabled,FullScanAge | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "antivirus_enabled": data.get("AntivirusEnabled"),
                    "realtime_protection": data.get("RealTimeProtectionEnabled"),
                    "last_scan": data.get("FullScanAge"),
                    "status": "Protected" if data.get("AntivirusEnabled") else "Not Protected"
                }
            return {"status": "Could not determine"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def analyze_boot_time() -> Dict[str, Any]:
        """Analyze system boot time"""
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                boot_time = result.stdout.strip()
                return {
                    "last_boot": boot_time,
                    "analysis": "System recently booted" if boot_time else "Unknown"
                }
            return {"error": "Could not determine boot time"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def check_disk_errors() -> Dict[str, Any]:
        """Check for disk errors"""
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-Volume | Where-Object {$_.DriveLetter} | Select-Object DriveLetter,FileSystem,Size,SizeRemaining | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                volumes = json.loads(result.stdout)
                return {
                    "volumes": volumes if isinstance(volumes, list) else [volumes],
                    "status": "Volumes scanned"
                }
            return {"error": "Could not scan volumes"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def analyze_running_services() -> Dict[str, Any]:
        """Analyze critical Windows services"""
        critical_services = [
            "wuauserv",  # Windows Update
            "WinDefend",  # Windows Defender
            "Bits",  # Background Intelligent Transfer Service
            "eventlog",  # Event Log
            "NlaSvc",  # Network Location Awareness
        ]
        
        try:
            service_info = {}
            for service in critical_services:
                result = subprocess.run(
                    ["powershell", "-Command",
                     f"Get-Service -Name {service} | Select-Object Name,Status,StartType | ConvertTo-Json"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    service_info[service] = data
            
            return {
                "services": service_info,
                "status": "Services analyzed"
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def check_system_drivers() -> Dict[str, Any]:
        """Check for outdated drivers"""
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-WmiObject Win32_SystemDriver | Select-Object Name,State,StartMode | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                drivers = json.loads(result.stdout)
                driver_list = drivers if isinstance(drivers, list) else [drivers]
                
                # Count drivers by state
                running = sum(1 for d in driver_list if d.get("State") == "Running")
                stopped = sum(1 for d in driver_list if d.get("State") == "Stopped")
                
                return {
                    "total_drivers": len(driver_list),
                    "running": running,
                    "stopped": stopped,
                    "status": "Drivers analyzed"
                }
            return {"error": "Could not analyze drivers"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def get_system_uptime() -> Dict[str, Any]:
        """Get system uptime information"""
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "[math]::Round((Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime).TotalHours"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                uptime_hours = float(result.stdout.strip())
                uptime_days = uptime_hours / 24
                
                status = "Good - System stable"
                if uptime_days > 30:
                    status = "Consider restarting system"
                elif uptime_days > 7:
                    status = "System running long - restart recommended"
                
                return {
                    "uptime_hours": round(uptime_hours, 2),
                    "uptime_days": round(uptime_days, 2),
                    "recommendation": status
                }
            return {"error": "Could not determine uptime"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def analyze_event_log(event_type: str = "Error", max_events: int = 5) -> Dict[str, Any]:
        """Analyze Windows Event Log"""
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 f"Get-EventLog -LogName System -EntryType {event_type} -Newest {max_events} | Select-Object TimeGenerated,Source,Message | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                events = json.loads(result.stdout)
                return {
                    f"{event_type.lower()}_events": events if isinstance(events, list) else [events],
                    "count": len(events) if isinstance(events, list) else 1
                }
            return {"error": "Could not read event log"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def get_detailed_crash_report() -> Dict[str, Any]:
        """Get system crash/issue reports"""
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-EventLog -LogName System -EntryType Error -Newest 10 | Group-Object -Property Source | Select-Object Name,Count | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                errors = json.loads(result.stdout)
                return {
                    "error_sources": errors if isinstance(errors, list) else [errors],
                    "status": "Error analysis complete"
                }
            return {"error": "Could not analyze errors"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    # ================================================================
    # New investigation tools added from the expanded tool set
    # ================================================================

    @staticmethod
    def get_installed_software() -> List[Dict[str, str]]:
        """List installed software from registry"""
        result = []
        paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
        ]
        for path in paths:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as sk:
                                try:
                                    name, _ = winreg.QueryValueEx(sk, "DisplayName")
                                    version, _ = winreg.QueryValueEx(sk, "DisplayVersion")
                                    publisher, _ = winreg.QueryValueEx(sk, "Publisher")
                                    result.append({
                                        "name": name,
                                        "version": version,
                                        "publisher": publisher
                                    })
                                except (FileNotFoundError, OSError):
                                    pass
                            i += 1
                        except OSError:
                            break
            except Exception:
                pass
        return sorted(result, key=lambda x: x["name"].lower())[:100]

    @staticmethod
    def get_startup_programs() -> List[Dict[str, str]]:
        """List startup programs from registry and startup folder"""
        entries = []
        paths = [
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        ]
        for hive, path in paths:
            try:
                with winreg.OpenKey(hive, path) as key:
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            entries.append({"name": name, "command": value, "scope": "user" if hive == winreg.HKEY_CURRENT_USER else "machine"})
                            i += 1
                        except OSError:
                            break
            except Exception:
                pass
        return entries

    @staticmethod
    def get_running_services(name_filter: str = "") -> Dict[str, Any]:
        """Get running services, optionally filtered by name"""
        cmd = 'powershell -NoProfile -Command "Get-Service | Select-Object Name, DisplayName, Status, StartType | ConvertTo-Json"'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            services = json.loads(result.stdout) if result.stdout.strip() else []
            if isinstance(services, dict):
                services = [services]
            if name_filter:
                services = [s for s in services if name_filter.lower() in s.get("Name", "").lower()]
            return {
                "total": len(services),
                "running": len([s for s in services if s.get("Status") == "Running"]),
                "services": services[:30]
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_drivers_summary() -> Dict[str, Any]:
        """Get installed driver summary and problem devices"""
        cmd = 'powershell -NoProfile -Command "Get-WmiObject Win32_SystemDriver | Select-Object Name, State, StartMode | ConvertTo-Json"'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            drivers = json.loads(result.stdout) if result.stdout.strip() else []
            if isinstance(drivers, dict):
                drivers = [drivers]
            running = len([d for d in drivers if d.get("State") == "Running"])
            stopped = len([d for d in drivers if d.get("State") == "Stopped"])
            return {
                "total": len(drivers),
                "running": running,
                "stopped": stopped,
                "problem_devices": AdvancedDiagnostics.get_problem_devices()
            }
        except Exception as e:
            return {"error": str(e), "problem_devices": AdvancedDiagnostics.get_problem_devices()}

    @staticmethod
    def get_problem_devices() -> List[Dict[str, str]]:
        """Get devices with problems from Device Manager"""
        cmd = 'powershell -NoProfile -Command "Get-WmiObject Win32_PnPEntity | Where-Object { $_.ConfigManagerErrorCode -ne 0 } | Select-Object Name, DeviceID, ConfigManagerErrorCode, Status | ConvertTo-Json"'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            devices = json.loads(result.stdout) if result.stdout.strip() else []
            if isinstance(devices, dict):
                devices = [devices]
            error_codes = {
                1: "Device not configured", 3: "Driver corrupted", 10: "Device cannot start",
                12: "Resource conflict", 14: "Cannot start (need restart)", 18: "Reinstall driver",
                19: "Registry corrupted", 22: "Device disabled", 28: "Driver not installed",
                31: "Driver failed", 32: "Driver disabled", 33: "Driver error",
                39: "Driver corrupted", 41: "Driver loaded but no device", 43: "Driver reported problem"
            }
            for d in devices:
                code = d.get("ConfigManagerErrorCode", 0)
                d["error_description"] = error_codes.get(code, f"Error code {code}")
            return devices
        except Exception as e:
            return [{"error": str(e)}]

    @staticmethod
    def get_critical_events(max_events: int = 10) -> List[Dict[str, str]]:
        """Get critical system errors from Event Log"""
        cmd = f'powershell -NoProfile -Command "Get-WinEvent -FilterHashtable @{{LogName=\'System\'; Level=1}} -MaxEvents {max_events} | Select-Object TimeCreated, Id, ProviderName, Message | ConvertTo-Json"'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            events = json.loads(result.stdout) if result.stdout.strip() else []
            if isinstance(events, dict):
                events = [events]
            for e in events:
                msg = e.get("Message", "")
                e["Message"] = msg[:200] if len(msg) > 200 else msg
            return events
        except Exception as e:
            return [{"error": str(e)}]

    @staticmethod
    def get_minidump_info() -> Dict[str, Any]:
        """Check for BSOD minidump files"""
        dump_dir = r"C:\Windows\Minidump"
        if not os.path.exists(dump_dir):
            return {"minidumps": [], "message": "No minidump directory found (no BSODs recorded)"}
        try:
            files = sorted(os.listdir(dump_dir), reverse=True)
            dumps = []
            for f in files[:10]:
                fp = os.path.join(dump_dir, f)
                size = os.path.getsize(fp)
                mtime = datetime.fromtimestamp(os.path.getmtime(fp)).isoformat()
                dumps.append({"file": f, "size_kb": round(size / 1024, 1), "created": mtime})
            return {
                "minidumps": dumps,
                "count": len(dumps),
                "message": f"Found {len(files)} minidump(s)" if files else "No minidumps present"
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def parse_bsod_error(stop_code: str) -> Dict[str, Any]:
        """Analyze a BSOD stop code"""
        known_codes = {
            "IRQL_NOT_LESS_OR_EQUAL": {"cause": "Faulty driver, usually network or storage", "fix": "Update or rollback driver, check RAM"},
            "KMODE_EXCEPTION_NOT_HANDLED": {"cause": "Faulty driver or incompatible hardware", "fix": "Update driver, remove recently added hardware"},
            "PAGE_FAULT_IN_NONPAGED_AREA": {"cause": "Faulty RAM, corrupted driver, or antivirus conflict", "fix": "Run Windows Memory Diagnostic, update drivers"},
            "SYSTEM_SERVICE_EXCEPTION": {"cause": "Driver or corrupted system file", "fix": "Run SFC /scannow, update drivers"},
            "CRITICAL_PROCESS_DIED": {"cause": "Critical system process crashed", "fix": "Run SFC /scannow, DISM /RestoreHealth"},
            "DPC_WATCHDOG_VIOLATION": {"cause": "Faulty SSD/NVMe driver or storage controller", "fix": "Update storage driver, check SSD health"},
            "MEMORY_MANAGEMENT": {"cause": "Faulty RAM", "fix": "Run Windows Memory Diagnostic, reseat RAM modules"},
            "BAD_SYSTEM_CONFIG_INFO": {"cause": "Corrupted registry hive", "fix": "Run System Restore, use last known good config"},
            "DRIVER_IRQL_NOT_LESS_OR_EQUAL": {"cause": "Network or storage driver fault", "fix": "Update or rollback driver"},
            "NTFS_FILE_SYSTEM": {"cause": "Corrupted file system or failing hard drive", "fix": "Run chkdsk /f, check disk health"},
            "KERNEL_DATA_INPAGE_ERROR": {"cause": "Failing RAM or hard drive", "fix": "Run memory diagnostic, check disk for bad sectors"},
        }
        code_upper = stop_code.upper().strip()
        for key, info in known_codes.items():
            if key in code_upper or code_upper in key:
                return {"stop_code": stop_code, "matched": key, "cause": info["cause"], "suggested_fix": info["fix"]}
        return {"stop_code": stop_code, "matched": None, "cause": "Unknown or generic stop code", "suggested_fix": "Search the stop code online, check Event Viewer for details"}

    @staticmethod
    def check_file_locks(file_path: str) -> Dict[str, Any]:
        """Check what process is locking a file using handle.exe or PowerShell"""
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}", "locked": False}
        cmd = f'powershell -NoProfile -Command "$file = \'{file_path}\'; try {{ $process = Get-Process | Where-Object {{ $_.Modules.FileName -eq $file -or (($_.Modules | ForEach-Object {{ $_.FileName }}) -contains $file) }}; if ($process) {{ $process | Select-Object Name, Id, StartTime | ConvertTo-Json }} else {{ \'No locking process found\' }} }} catch {{ \'Error checking locks\' }}"'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            output = result.stdout.strip()
            if "No locking process" in output:
                return {"file": file_path, "locked": False, "processes": []}
            try:
                procs = json.loads(output)
                if isinstance(procs, dict):
                    procs = [procs]
                return {"file": file_path, "locked": True, "processes": procs}
            except json.JSONDecodeError:
                return {"file": file_path, "locked": False, "processes": []}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_temp_file_size() -> Dict[str, Any]:
        """Get total size of temp files"""
        total_size = 0
        temp_dirs = [
            tempfile.gettempdir(),
            os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Temp"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp"),
        ]
        details = []
        for d in temp_dirs:
            if not d or not os.path.exists(d):
                continue
            try:
                size = sum(f.stat().st_size for f in os.scandir(d) if f.is_file()) / (1024 * 1024)
                total_size += size
                details.append({"path": d, "size_mb": round(size, 1)})
            except Exception:
                pass
        return {"total_mb": round(total_size, 1), "directories": details}

    @staticmethod
    def test_network_connectivity() -> Dict[str, Any]:
        """Test ping, DNS, and gateway"""
        results = {}
        # Ping Google DNS
        ping = _run_cmd("ping -n 2 8.8.8.8", timeout=10)
        results["ping_external"] = "Succeeded" if "Reply from" in ping else "Failed"
        # DNS resolution
        nslookup = _run_cmd("nslookup google.com 8.8.8.8", timeout=10)
        results["dns_resolution"] = "Succeeded" if "Address:" in nslookup else "Failed"
        # Gateway
        ipconfig = _run_cmd("ipconfig", timeout=10)
        gateway_line = [l for l in ipconfig.split("\n") if "Default Gateway" in l]
        results["gateway"] = gateway_line[0].split(":")[-1].strip() if gateway_line else "Not found"
        return results

    @staticmethod
    def get_wifi_info() -> Dict[str, Any]:
        """Get WiFi adapter info"""
        cmd = 'powershell -NoProfile -Command "Get-NetAdapter -Name \'Wi-Fi\' -ErrorAction SilentlyContinue | Select-Object Name, Status, LinkSpeed, MacAddress | ConvertTo-Json"'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            adapter = json.loads(result.stdout) if result.stdout.strip() else {}
        except Exception:
            adapter = {}
        # Also get signal strength via netsh
        netsh = _run_cmd("netsh wlan show interfaces", timeout=10)
        signal = ""
        for line in netsh.split("\n"):
            if "Signal" in line:
                signal = line.split(":")[-1].strip()
                break
        return {"adapter": adapter, "signal": signal}

    @staticmethod
    def get_bluetooth_status() -> Dict[str, Any]:
        """Get Bluetooth status"""
        cmd = 'powershell -NoProfile -Command "Get-PnpDevice -Class Bluetooth -ErrorAction SilentlyContinue | Select-Object FriendlyName, Status, InstanceId | ConvertTo-Json"'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            devices = json.loads(result.stdout) if result.stdout.strip() else []
            if isinstance(devices, dict):
                devices = [devices]
            return {"devices": devices, "count": len(devices)}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_usb_devices() -> Dict[str, Any]:
        """Get connected USB devices"""
        cmd = 'powershell -NoProfile -Command "Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue | Where-Object { $_.Class -eq \'USB\' -or $_.Class -eq \'HIDClass\' -or $_.Class -eq \'Camera\' } | Select-Object FriendlyName, Class, Status, InstanceId | ConvertTo-Json"'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            devices = json.loads(result.stdout) if result.stdout.strip() else []
            if isinstance(devices, dict):
                devices = [devices]
            return {"devices": devices, "count": len(devices)}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_display_info() -> Dict[str, Any]:
        """Get GPU/display information"""
        cmd = 'powershell -NoProfile -Command "Get-WmiObject Win32_VideoController | Select-Object Name, AdapterRAM, DriverVersion, DriverDate, VideoModeDescription, Status | ConvertTo-Json"'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            gpus = json.loads(result.stdout) if result.stdout.strip() else []
            if isinstance(gpus, dict):
                gpus = [gpus]
            for g in gpus:
                if "AdapterRAM" in g and g["AdapterRAM"]:
                    g["AdapterRAM_gb"] = round(int(g["AdapterRAM"]) / (1024**3), 2)
            return {"gpus": gpus}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_audio_devices() -> Dict[str, Any]:
        """Get audio device information"""
        cmd = 'powershell -NoProfile -Command "Get-WmiObject Win32_SoundDevice | Select-Object Name, Status, Manufacturer | ConvertTo-Json"'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            devices = json.loads(result.stdout) if result.stdout.strip() else []
            if isinstance(devices, dict):
                devices = [devices]
            return {"devices": devices}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_printer_info() -> Dict[str, Any]:
        """Get printer and print spooler status"""
        cmd = 'powershell -NoProfile -Command "$spooler = Get-Service -Name Spooler -ErrorAction SilentlyContinue; $printers = Get-WmiObject Win32_Printer -ErrorAction SilentlyContinue | Select-Object Name, Status, DriverName, PortName, PrinterStatus | ConvertTo-Json; Write-Output \\"SPOOLER_STATUS: $($spooler.Status)\\"; Write-Output $printers"'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            out = result.stdout.strip()
            spooler_status = "Unknown"
            printers = []
            for line in out.split("\n"):
                if line.startswith("SPOOLER_STATUS:"):
                    spooler_status = line.split(":")[-1].strip()
            try:
                printers = json.loads(out.split("SPOOLER_STATUS:")[-1].strip()) if out.strip() else []
                if isinstance(printers, dict):
                    printers = [printers]
            except Exception:
                pass
            return {"spooler": spooler_status, "printers": printers}
        except Exception as e:
            return {"spooler": "Error", "printers": [], "error": str(e)}

    @staticmethod
    def get_windows_update_status() -> Dict[str, Any]:
        """Get Windows Update status"""
        cmd = 'powershell -NoProfile -Command "$session = New-Object -ComObject Microsoft.Update.Session; $searcher = $session.CreateUpdateSearcher(); try { $count = $searcher.GetTotalHistoryCount(); $history = $searcher.QueryHistory(0, $count) | Select-Object -Last 5 Date, Title, ResultCode, Description | ConvertTo-Json; Write-Output \\"PENDING: $count\\"; Write-Output $history } catch { Write-Output \\"ERROR: Update service not available\\" }"'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            out = result.stdout.strip()
            if "ERROR" in out:
                return {"status": "Service unavailable", "error": out}
            pending = 0
            history = []
            for line in out.split("\n"):
                if line.startswith("PENDING:"):
                    try:
                        pending = int(line.split(":")[-1].strip())
                    except:
                        pass
            try:
                history = json.loads(out.split("PENDING:")[-1].strip()) if out.strip() else []
                if isinstance(history, dict):
                    history = [history]
            except Exception:
                pass
            return {"pending_updates": pending, "recent_history": history}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def check_system_file_integrity() -> Dict[str, Any]:
        """Run SFC /verifyonly to check system files (read-only)"""
        try:
            result = subprocess.run(["sfc", "/verifyonly"], capture_output=True, text=True, timeout=300)
            out = result.stdout + result.stderr
            corrupted = "found" if "found corrupt" in out.lower() or "did not find" not in out.lower() else "none"
            return {
                "status": "Completed",
                "corrupted_files": corrupted,
                "details": out[:500],
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"status": "Timed out (5 min max)", "corrupted_files": "unknown"}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_boot_configuration() -> Dict[str, Any]:
        """Get boot configuration data"""
        bcdedit = _run_cmd("bcdedit /enum", timeout=10)
        systeminfo = _run_cmd("systeminfo | findstr /B /C:\"OS Name\" /C:\"OS Version\" /C:\"System Boot Time\"", timeout=10)
        return {
            "bcdedit": bcdedit[:1000],
            "system_info": systeminfo[:500]
        }

    @staticmethod
    def get_user_profiles() -> Dict[str, Any]:
        """Get user profile information"""
        cmd = 'powershell -NoProfile -Command "Get-WmiObject Win32_UserProfile | Where-Object { $_.Special -eq $false } | Select-Object LocalPath, LastUseTime, Loaded, Status | ConvertTo-Json"'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            profiles = json.loads(result.stdout) if result.stdout.strip() else []
            if isinstance(profiles, dict):
                profiles = [profiles]
            return {"profiles": profiles, "count": len(profiles)}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def generate_comprehensive_report() -> Dict[str, Any]:
        """Generate comprehensive system health report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "sections": {}
        }
        
        # Gather all diagnostics
        report["sections"]["windows_updates"] = AdvancedDiagnostics.get_windows_updates_status()
        report["sections"]["antivirus"] = AdvancedDiagnostics.check_antivirus_status()
        report["sections"]["boot_time"] = AdvancedDiagnostics.analyze_boot_time()
        report["sections"]["uptime"] = AdvancedDiagnostics.get_system_uptime()
        report["sections"]["services"] = AdvancedDiagnostics.analyze_running_services()
        report["sections"]["drivers"] = AdvancedDiagnostics.check_system_drivers()
        report["sections"]["recent_errors"] = AdvancedDiagnostics.analyze_event_log("Error", 3)
        report["sections"]["crash_summary"] = AdvancedDiagnostics.get_detailed_crash_report()
        
        return report


def generate_optimization_recommendations(diagnostics: Dict[str, Any]) -> List[str]:
    """Generate optimization recommendations based on diagnostics"""
    recommendations = []
    
    # Check uptime
    if "uptime" in diagnostics.get("sections", {}):
        uptime = diagnostics["sections"]["uptime"]
        if uptime.get("uptime_days", 0) > 30:
            recommendations.append("Restart your system to clear memory and caches")
    
    # Check antivirus
    if "antivirus" in diagnostics.get("sections", {}):
        antivirus = diagnostics["sections"]["antivirus"]
        if not antivirus.get("antivirus_enabled"):
            recommendations.append("Enable Windows Defender or install third-party antivirus")
        if not antivirus.get("realtime_protection"):
            recommendations.append("Enable real-time protection in Windows Defender")
    
    # Check Windows Updates
    if "windows_updates" in diagnostics.get("sections", {}):
        updates = diagnostics["sections"]["windows_updates"]
        if "error" in updates:
            recommendations.append("Check for Windows Updates manually")
    
    # Check services
    if "services" in diagnostics.get("sections", {}):
        services = diagnostics["sections"]["services"]
        if services.get("services", {}).get("wuauserv", {}).get("Status") == "Stopped":
            recommendations.append("Enable Windows Update service")
    
    return recommendations
