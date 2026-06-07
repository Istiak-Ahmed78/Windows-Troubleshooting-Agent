"""
Advanced Diagnostics Module
Additional system analysis and optimization utilities
"""
import subprocess
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime


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
