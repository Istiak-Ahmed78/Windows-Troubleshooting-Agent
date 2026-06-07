"""
Windows Diagnostics Module
Handles system diagnostics and hardware monitoring
"""
import psutil
import os
import subprocess
import json
from datetime import datetime
from typing import Dict, List, Any, Optional


class WindowsDiagnostics:
    """Main diagnostics class for Windows system analysis"""
    
    def __init__(self):
        self.diagnostics_cache = {}
        self.last_update = None
        
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
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
        """Get CPU usage and temperature information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            per_cpu = psutil.cpu_percent(percpu=True, interval=1)
            
            # Try to get temperature
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
        """Attempt to retrieve CPU temperature"""
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
        """Analyze CPU health status"""
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
        """Get RAM and virtual memory information"""
        try:
            virtual_memory = psutil.virtual_memory()
            swap_memory = psutil.swap_memory()
            
            return {
                "total": virtual_memory.total,
                "available": virtual_memory.available,
                "used": virtual_memory.used,
                "percent": virtual_memory.percent,
                "swap": {
                    "total": swap_memory.total,
                    "used": swap_memory.used,
                    "percent": swap_memory.percent,
                },
                "status": self.analyze_memory_health(virtual_memory.percent)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_memory_health(self, usage_percent: float) -> str:
        """Analyze memory health status"""
        if usage_percent > 90:
            return "Critical - Low Memory"
        elif usage_percent > 80:
            return "Warning - High Memory Usage"
        elif usage_percent > 60:
            return "Moderate Memory Usage"
        return "Good"
    
    def get_disk_info(self) -> Dict[str, Any]:
        """Get disk space information for all partitions"""
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
        """Analyze disk health status"""
        if usage_percent > 95:
            return "Critical - Almost Full"
        elif usage_percent > 85:
            return "Warning - Low Space"
        elif usage_percent > 70:
            return "Moderate Usage"
        return "Good"
    
    def get_top_processes(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Get top resource-consuming processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            cpu_processes = sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:5]
            # Sort by Memory usage
            mem_processes = sorted(processes, key=lambda x: x.get('memory_percent', 0), reverse=True)[:5]
            
            return {
                "top_cpu": cpu_processes,
                "top_memory": mem_processes
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network interface information"""
        try:
            interfaces = psutil.net_if_stats()
            net_io = psutil.net_io_counters()
            
            return {
                "interfaces": {name: {
                    "is_up": stats.isup,
                    "speed": stats.speed,
                    "mtu": stats.mtu,
                    "stats": {
                        "packets_sent": stats.packets_sent,
                        "packets_recv": stats.packets_recv,
                        "errin": stats.errin,
                        "errout": stats.errout,
                        "dropin": stats.dropin,
                        "dropout": stats.dropout,
                    }
                } for name, stats in interfaces.items()},
                "io_counters": {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_battery_info(self) -> Dict[str, Any]:
        """Get battery status if available"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    "percent": battery.percent,
                    "secsleft": battery.secsleft,
                    "power_plugged": battery.power_plugged,
                    "status": "Charging" if battery.power_plugged else "Discharging"
                }
            return {"status": "No battery detected"}
        except Exception as e:
            return {"error": str(e)}
    
    def check_autostart_programs(self) -> List[str]:
        """Check programs in Windows autostart"""
        try:
            autostart_path = os.path.expanduser(
                r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
            )
            if os.path.exists(autostart_path):
                return os.listdir(autostart_path)
            return []
        except Exception as e:
            return [f"Error: {str(e)}"]
    
    def check_startup_programs(self) -> List[str]:
        """Check Windows startup programs"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", 
                 "Get-WmiObject -Class Win32_StartupCommand | Select-Object Name, Command | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data if isinstance(data, list) else [data]
            return []
        except Exception as e:
            return [f"Error: {str(e)}"]
    
    def check_services_status(self) -> Dict[str, List[str]]:
        """Check Windows services status"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", 
                 "Get-Service | Where-Object {$_.StartType -eq 'Automatic'} | Select-Object Name, Status | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                services = data if isinstance(data, list) else [data]
                
                running = [s['Name'] for s in services if s.get('Status') == 'Running']
                stopped = [s['Name'] for s in services if s.get('Status') == 'Stopped']
                
                return {"running": running, "stopped": stopped}
            return {"error": "Could not fetch services"}
        except Exception as e:
            return {"error": str(e)}
    
    def diagnose_slow_system(self) -> Dict[str, Any]:
        """Comprehensive slow system diagnosis"""
        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "issues_found": [],
            "recommendations": []
        }
        
        # Check CPU
        cpu_info = self.get_cpu_info()
        if cpu_info.get("status") in ["High Usage", "High Temperature"]:
            diagnosis["issues_found"].append({
                "type": "CPU",
                "status": cpu_info.get("status"),
                "details": f"CPU Usage: {cpu_info.get('usage_percent')}%"
            })
            diagnosis["recommendations"].append(
                "• Check for resource-heavy processes running in background"
            )
        
        # Check Memory
        mem_info = self.get_memory_info()
        if "Critical" in mem_info.get("status", "") or "Warning" in mem_info.get("status", ""):
            diagnosis["issues_found"].append({
                "type": "Memory",
                "status": mem_info.get("status"),
                "details": f"Memory Usage: {mem_info.get('percent')}%"
            })
            diagnosis["recommendations"].append(
                "• Close unused applications and clear memory"
            )
        
        # Check Disk
        disk_info = self.get_disk_info()
        for partition in disk_info.get("partitions", []):
            if "Critical" in partition.get("status", "") or "Warning" in partition.get("status", ""):
                diagnosis["issues_found"].append({
                    "type": "Disk",
                    "device": partition["device"],
                    "status": partition.get("status"),
                    "details": f"Free Space: {partition.get('free') / (1024**3):.2f} GB"
                })
                diagnosis["recommendations"].append(
                    f"• Free up disk space on {partition['device']}"
                )
        
        # Check top processes
        top_proc = self.get_top_processes()
        cpu_hogs = top_proc.get("top_cpu", [])[:3]
        mem_hogs = top_proc.get("top_memory", [])[:3]
        
        if cpu_hogs:
            diagnosis["top_cpu_processes"] = cpu_hogs
        
        if mem_hogs:
            diagnosis["top_memory_processes"] = mem_hogs
        
        return diagnosis
    
    def diagnose_app_failure(self, app_name: str) -> Dict[str, Any]:
        """Diagnose why an application might fail to open"""
        diagnosis = {
            "app_name": app_name,
            "timestamp": datetime.now().isoformat(),
            "possible_causes": [],
            "solutions": []
        }
        
        # Check memory
        mem_info = self.get_memory_info()
        if mem_info.get("percent", 0) > 80:
            diagnosis["possible_causes"].append("Insufficient memory available")
            diagnosis["solutions"].append("• Close other applications to free up memory")
        
        # Check disk
        disk_info = self.get_disk_info()
        for partition in disk_info.get("partitions", []):
            if partition.get("percent", 0) > 90:
                diagnosis["possible_causes"].append(f"Low disk space on {partition['device']}")
                diagnosis["solutions"].append(f"• Free up space on {partition['device']}")
        
        # Generic solutions
        diagnosis["solutions"].extend([
            "• Restart the application",
            "• Check if the application has updates available",
            "• Run the application as Administrator",
            "• Check Windows Event Viewer for error logs",
            "• Reinstall the application if problem persists"
        ])
        
        return diagnosis


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"
