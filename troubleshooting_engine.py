"""
Troubleshooting Engine
"""
from typing import Dict, List, Any, Optional
import re
from datetime import datetime
from diagnostics import ErrorMessageParser


class TroubleshootingEngine:
    """Troubleshooting engine with error analysis"""
    
    def __init__(self):
        self.conversation_history = []
    
    def analyze_issue(self, issue_description: str, diagnostics: Dict[str, Any]) -> Dict[str, Any]:
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "issue": issue_description,
            "severity": self.determine_severity(diagnostics),
            "reasoning": [],
            "findings": [],
            "recommendations": [],
            "next_steps": [],
            "actions": []
        }
        
        metrics = self.extract_metrics(diagnostics)
        
        # First: try to parse any Windows error messages in the text
        error_info = ErrorMessageParser.parse(issue_description)
        
        if error_info:
            # Error-specific analysis
            analysis["issue_type"] = error_info["title"]
            analysis["findings"].append(f"Detected: {error_info['description']}")
            analysis["reasoning"].append(
                f"Your description matches a known Windows error pattern: {error_info['title']}. "
                f"I have specific solutions for this."
            )
            analysis["recommendations"] = error_info["solutions"]
            
            if error_info.get("action") == "run_defender_scan":
                analysis["actions"].append({
                    "type": "run_defender_scan",
                    "label": "Run Windows Defender Scan"
                })
            
            analysis["next_steps"] = [
                "1. Try the recommended solutions above",
                "2. Apply the fix that matches your situation",
                "3. Try opening the application again",
                "4. If it still fails, reinstall the application"
            ]
        else:
            # Fall back to keyword-based classification
            analysis.update(self._classify_by_keywords(issue_description, metrics, diagnostics))
        
        # Add system resource findings
        self._add_resource_findings(analysis, metrics)
        
        # Add app crash history if relevant
        self._add_crash_history(analysis, diagnostics)
        
        self.conversation_history.append({
            "issue": issue_description,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        })
        
        return analysis
    
    def _classify_by_keywords(self, issue: str, metrics: Dict, diagnostics: Dict) -> Dict:
        if self._match_keywords(issue, ["slow", "sluggish", "lag", "unresponsive", "freeze", "hang"]):
            return self._analyze_slow_system(metrics)
        elif self._match_keywords(issue, ["crash", "open", "start", "launch", "fail", "error", "work"]):
            return self._analyze_app_failure(issue, metrics)
        elif self._match_keywords(issue, ["startup", "boot", "start"]):
            return self._analyze_startup(metrics)
        elif self._match_keywords(issue, ["disk", "storage", "space", "drive", "full", "ssd"]):
            return self._analyze_disk(metrics)
        elif self._match_keywords(issue, ["network", "internet", "wifi", "connection", "ethernet"]):
            return self._analyze_network(diagnostics)
        elif self._match_keywords(issue, ["virus", "malware", "trojan", "scan", "defender"]):
            return self._analyze_security(diagnostics)
        else:
            return self._analyze_general(metrics)
    
    def _match_keywords(self, text: str, keywords: List[str]) -> bool:
        text_lower = text.lower()
        return any(kw in text_lower for kw in keywords)
    
    def extract_metrics(self, diagnostics: Dict) -> Dict:
        metrics = {}
        if "cpu" in diagnostics:
            metrics["cpu_usage"] = diagnostics["cpu"].get("usage_percent", 0)
            metrics["cpu_temp"] = diagnostics["cpu"].get("temperature")
        if "memory" in diagnostics:
            metrics["memory_usage"] = diagnostics["memory"].get("percent", 0)
            metrics["available_memory"] = diagnostics["memory"].get("available", 0)
        if "disk" in diagnostics:
            partitions = diagnostics["disk"].get("partitions", [])
            if partitions:
                metrics["disk_usage"] = [p.get("percent", 0) for p in partitions]
                metrics["free_space"] = [p.get("free", 0) for p in partitions]
        if "processes" in diagnostics:
            metrics["top_cpu_processes"] = diagnostics["processes"].get("top_cpu", [])
            metrics["top_memory_processes"] = diagnostics["processes"].get("top_memory", [])
        return metrics
    
    def determine_severity(self, diagnostics: Dict) -> str:
        score = 0
        if diagnostics.get("cpu", {}).get("usage_percent", 0) > 90:
            score += 3
        elif diagnostics.get("cpu", {}).get("usage_percent", 0) > 70:
            score += 1
        if diagnostics.get("memory", {}).get("percent", 0) > 95:
            score += 3
        elif diagnostics.get("memory", {}).get("percent", 0) > 85:
            score += 2
        for p in diagnostics.get("disk", {}).get("partitions", []):
            if p.get("percent", 0) > 95:
                score += 3
            elif p.get("percent", 0) > 85:
                score += 2
        if score >= 6:
            return "Critical"
        elif score >= 4:
            return "High"
        elif score >= 2:
            return "Medium"
        return "Low"
    
    def _analyze_slow_system(self, metrics: Dict) -> Dict:
        analysis = {"issue_type": "System Slowness", "reasoning": [], "findings": [], "recommendations": [], "next_steps": []}
        
        cpu = metrics.get("cpu_usage", 0)
        memory = metrics.get("memory_usage", 0)
        
        if cpu > 80:
            analysis["findings"].append(f"High CPU usage detected: {cpu}% — programs are competing for processor time")
            analysis["reasoning"].append("High CPU usage makes the system feel sluggish because the processor is overloaded.")
            top_cpu = metrics.get("top_cpu_processes", [])
            if top_cpu:
                names = [p.get('name', '?') for p in top_cpu[:3]]
                analysis["findings"].append(f"Top CPU consumers: {', '.join(names)}")
            analysis["recommendations"] = [
                "Open Task Manager (Ctrl+Shift+Esc) -> Sort by CPU -> End high-consuming processes",
                "Check for malware: Windows Security -> Virus & threat protection -> Scan options -> Full scan",
                "Disable startup programs: Task Manager -> Startup -> Disable unneeded items",
                "Update drivers: Windows Update -> Check for updates"
            ]
        elif cpu > 50:
            analysis["findings"].append(f"Moderate CPU usage: {cpu}%")
            analysis["recommendations"] = ["Close unused browser tabs and background apps"]
        
        if memory > 85:
            analysis["findings"].append(f"High memory usage: {memory}% — RAM is nearly full")
            analysis["reasoning"].append("When RAM is full, Windows uses your hard drive as 'virtual memory', which is much slower.")
            analysis["recommendations"].extend([
                "Close memory-heavy apps: Task Manager -> Memory tab -> End tasks",
                "Restart your PC to clear memory leaks",
                "Consider upgrading RAM if this happens often"
            ])
        
        if not analysis["findings"]:
            analysis["reasoning"].append("Your system resources look normal. The slowness might be caused by software issues.")
            analysis["recommendations"] = [
                "Run Windows Update to get latest patches",
                "Run 'sfc /scannow' in Command Prompt (Admin) to check system files",
                "Check if a specific app is causing the problem (try booting in Safe Mode)",
                "Scan for malware with Windows Defender"
            ]
        
        analysis["next_steps"] = [
            "1. Check Task Manager for resource hogs", "2. Close unneeded programs",
            "3. Restart your PC", "4. Run antivirus scan", "5. Update drivers and Windows"
        ]
        return analysis
    
    def _analyze_app_failure(self, issue: str, metrics: Dict) -> Dict:
        analysis = {"issue_type": "Application Failure", "reasoning": [], "findings": [], "recommendations": [], "next_steps": [], "actions": []}
        
        # Extract app name
        app_name = ErrorMessageParser.extract_app_name(issue)
        
        memory = metrics.get("memory_usage", 0)
        
        if memory > 80:
            analysis["findings"].append(f"Memory is at {memory}% — not enough free RAM to launch new apps reliably")
            analysis["recommendations"].append("Close applications to free memory before trying again")
        
        # General app failure solutions
        analysis["reasoning"].append("Applications fail to open due to: corrupted files, missing runtimes, permissions, or file association issues.")
        analysis["findings"].append("Checking common causes for application launch failures")
        
        analysis["recommendations"] = [
            "Right-click the shortcut -> 'Open file location' -> run the .exe directly (bypass shortcut)",
            "Right-click -> 'Run as administrator' to test for permission issues",
            "Restart your PC — clears temporary glitches",
            "Reinstall the application — fixes corrupted files",
            "Check Windows Event Viewer: Win+R -> 'eventvwr.msc' -> Windows Logs -> Application -> look for errors",
            "Run 'sfc /scannow' in Admin Command Prompt to repair system files",
            "Check if antivirus is blocking it: temporarily disable real-time protection"
        ]
        
        if app_name:
            analysis["findings"].append(f"Application detected: '{app_name}' — checking common issues")
            analysis["recommendations"].insert(0, f"Search for '{app_name}' in Windows Event Viewer for specific error details")
        
        analysis["actions"].append({"type": "check_shortcut", "label": "Check if shortcut (.lnk) is valid"})
        
        analysis["next_steps"] = [
            "1. Try running the .exe file directly (not the shortcut)",
            "2. Run as Administrator",
            "3. Restart your PC",
            "4. Reinstall the application",
            "5. Check Event Viewer for specific error codes"
        ]
        return analysis
    
    def _analyze_startup(self, metrics: Dict) -> Dict:
        analysis = {"issue_type": "Slow Startup", "reasoning": [], "findings": [], "recommendations": [], "next_steps": []}
        analysis["reasoning"].append("Slow startup is usually caused by too many programs loading at boot.")
        analysis["recommendations"] = [
            "Open Task Manager (Ctrl+Shift+Esc) -> Startup tab",
            "Disable programs you don't need at startup (Spotify, Adobe updater, etc.)",
            "Check for malware: Windows Security -> Scan options -> Full scan",
            "Enable 'Fast Startup' in Power Options (Control Panel -> Power Options -> Choose what power buttons do)",
            "Update BIOS/drivers from your PC manufacturer's website",
            "If using HDD, consider upgrading to SSD for dramatic improvement"
        ]
        analysis["next_steps"] = [
            "1. Open Task Manager -> Startup -> Disable unnecessary items",
            "2. Restart and check if boot time improved",
            "3. Run malware scan if still slow"
        ]
        return analysis
    
    def _analyze_disk(self, metrics: Dict) -> Dict:
        analysis = {"issue_type": "Disk Space / Health", "reasoning": [], "findings": [], "recommendations": [], "next_steps": [], "actions": []}
        
        disk_usage = metrics.get("disk_usage", [0])[0] if metrics.get("disk_usage") else 0
        
        if disk_usage > 90:
            analysis["findings"].append(f"CRITICAL: Disk is {disk_usage}% full — this WILL cause problems")
            analysis["reasoning"].append("Windows needs free space for updates, temp files, and virtual memory. Below 10% free space causes crashes and slowdowns.")
            analysis["recommendations"] = [
                "Run Disk Cleanup: Win+R -> 'cleanmgr.exe' -> Select drive -> Delete temp files",
                "Empty Recycle Bin",
                "Uninstall unused programs: Settings -> Apps -> Installed apps -> Sort by size -> Remove large unused ones",
                "Move large files (videos, backups) to external drive",
                "Run 'dir C:\\ /a /s /q | sort /R /O N' in CMD to find largest folders"
            ]
            analysis["actions"].append({"type": "run_disk_cleanup", "label": "Run Disk Cleanup"})
        elif disk_usage > 80:
            analysis["findings"].append(f"Warning: Disk is {disk_usage}% full")
            analysis["reasoning"].append("Disk space is running low. Consider cleaning up soon.")
            analysis["recommendations"] = [
                "Run Disk Cleanup to free temporary files",
                "Uninstall apps you no longer use",
                "Check for old Windows Update files: cleanmgr.exe -> 'Windows Update Cleanup'"
            ]
        else:
            analysis["findings"].append(f"Disk usage: {disk_usage}% — within normal range")
            analysis["reasoning"].append("Your disk space looks healthy.")
        
        analysis["next_steps"] = [
            "1. Run Disk Cleanup", "2. Delete unnecessary files", "3. Uninstall unused apps"
        ]
        return analysis
    
    def _analyze_network(self, diagnostics: Dict) -> Dict:
        analysis = {"issue_type": "Network Issue", "reasoning": [], "findings": [], "recommendations": [], "next_steps": []}
        network = diagnostics.get("network", {})
        interfaces = network.get("interfaces", {})
        active = [n for n, s in interfaces.items() if s.get("is_up")]
        
        if not active:
            analysis["findings"].append("No active network connections detected")
        else:
            analysis["findings"].append(f"Active connections: {', '.join(active)}")
        
        analysis["reasoning"].append("Network problems are often caused by router issues, driver problems, or ISP outages.")
        analysis["recommendations"] = [
            "Restart your router: unplug for 30 seconds, plug back in, wait 2 minutes",
            "Restart your PC to clear network cache",
            "Run Windows Network Troubleshooter: Settings -> Network & Internet -> Troubleshoot",
            "Update network drivers: Device Manager -> Network adapters -> Update driver",
            "Release/renew IP: Open CMD as Admin -> 'ipconfig /release' -> 'ipconfig /renew'",
            "Flush DNS: Open CMD as Admin -> 'ipconfig /flushdns'"
        ]
        analysis["next_steps"] = [
            "1. Restart router", "2. Restart PC", "3. Run network troubleshooter",
            "4. Update network drivers", "5. Contact ISP if still down"
        ]
        return analysis
    
    def _analyze_security(self, diagnostics: Dict) -> Dict:
        analysis = {"issue_type": "Security / Malware Check", "reasoning": [], "findings": [], "recommendations": [], "next_steps": [], "actions": []}
        analysis["reasoning"].append("I'll help you scan for malware and secure your system.")
        defender = diagnostics.get("defender_status", {})
        if defender:
            protected = defender.get("AntivirusEnabled")
            analysis["findings"].append(f"Windows Defender active: {'Yes' if protected else 'No'}")
        
        analysis["findings"].append("Running security diagnostics...")
        analysis["recommendations"] = [
            "Windows Defender Quick Scan: Settings -> Privacy & Security -> Windows Security -> Virus & threat protection -> Quick scan",
            "Windows Defender Full Scan: Same page -> Scan options -> Full scan (takes 1-2 hours)",
            "Run offline Microsoft Safety Scanner: download from Microsoft.com",
            "Check startup programs: Task Manager -> Startup -> Disable suspicious entries",
            "Check browser for unwanted extensions or toolbars",
            "Update Windows and all software to patch security holes"
        ]
        analysis["actions"].append({"type": "run_defender_scan", "label": "Run Windows Defender Quick Scan"})
        analysis["next_steps"] = [
            "1. Run Windows Defender Quick Scan",
            "2. Check startup programs for suspicious entries",
            "3. Keep Windows updated"
        ]
        return analysis
    
    def _analyze_general(self, metrics: Dict) -> Dict:
        analysis = {"issue_type": "General System Check", "reasoning": [], "findings": [], "recommendations": [], "next_steps": []}
        analysis["reasoning"].append("Running a general health check on your system.")
        
        if metrics.get("cpu_usage", 0) < 50 and metrics.get("memory_usage", 0) < 70:
            analysis["findings"].append("System resources appear normal")
            analysis["recommendations"] = [
                "Check for Windows Updates: Settings -> Windows Update -> Check for updates",
                "Run 'sfc /scannow' in Command Prompt (Admin) to verify system files",
                "Check Event Viewer for errors: Win+R -> 'eventvwr.msc' -> Windows Logs -> System",
                "Run Windows Memory Diagnostic: Win+R -> 'mdsched.exe' -> Restart now"
            ]
        else:
            analysis["findings"].append("System resources are elevated — see diagnostics panel")
        
        analysis["next_steps"] = [
            "1. Run Windows Update",
            "2. Check for malware",
            "3. Update drivers",
            "4. Check Event Viewer for errors"
        ]
        return analysis
    
    def _add_resource_findings(self, analysis: Dict, metrics: Dict):
        """Add system resource context to any analysis"""
        cpu = metrics.get("cpu_usage", 0)
        memory = metrics.get("memory_usage", 0)
        
        # Only add if not already there and if resources are high
        has_cpu_finding = any("CPU" in f or "cpu" in f for f in analysis.get("findings", []))
        has_mem_finding = any("memory" in f or "RAM" in f or "Memory" in f for f in analysis.get("findings", []))
        
        if cpu > 80 and not has_cpu_finding:
            analysis["findings"].insert(0, f"Background: CPU at {cpu}% — this may be contributing to the issue")
        if memory > 85 and not has_mem_finding:
            analysis["findings"].insert(0, f"Background: RAM at {memory}% — low memory can cause apps to fail")
    
    def _add_crash_history(self, analysis: Dict, diagnostics: Dict):
        """Add recent crash history if relevant"""
        if "issue_type" in analysis and "Failure" in analysis.get("issue_type", ""):
            try:
                from diagnostics import WindowsDiagnostics
                d = WindowsDiagnostics()
                crashes = d.get_recent_app_crashes()
                if crashes:
                    crash_names = [c["application"] for c in crashes[:3]]
                    analysis["findings"].append(
                        f"Recent crashes found in Event Log: {', '.join(crash_names)}"
                    )
            except:
                pass
