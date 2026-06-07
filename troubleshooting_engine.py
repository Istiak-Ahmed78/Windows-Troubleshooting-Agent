"""
AI Troubleshooting Engine
Provides intelligent reasoning and recommendations based on diagnostics
"""
from typing import Dict, List, Any, Tuple
import json
from datetime import datetime


class TroubleshootingEngine:
    """AI engine for intelligent troubleshooting"""
    
    def __init__(self):
        self.conversation_history = []
        self.diagnostics_history = []
        self.current_issue = None
        
    def analyze_issue(self, issue_description: str, diagnostics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze user's issue description and diagnostics data
        Returns analysis with reasoning and recommendations
        """
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "issue": issue_description,
            "severity": self.determine_severity(diagnostics),
            "reasoning": [],
            "findings": [],
            "recommendations": [],
            "next_steps": []
        }
        
        # Extract key metrics
        metrics = self.extract_metrics(diagnostics)
        
        # Analyze based on issue type
        if self.is_slow_system_issue(issue_description):
            analysis.update(self._analyze_slow_system(metrics, diagnostics))
        elif self.is_app_failure_issue(issue_description):
            analysis.update(self._analyze_app_failure(issue_description, metrics, diagnostics))
        elif self.is_startup_issue(issue_description):
            analysis.update(self._analyze_startup_issue(metrics, diagnostics))
        elif self.is_disk_issue(issue_description):
            analysis.update(self._analyze_disk_issue(metrics, diagnostics))
        elif self.is_network_issue(issue_description):
            analysis.update(self._analyze_network_issue(diagnostics))
        else:
            analysis.update(self._analyze_general_issue(metrics, diagnostics))
        
        self.conversation_history.append({
            "issue": issue_description,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        })
        
        return analysis
    
    def extract_metrics(self, diagnostics: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from diagnostics"""
        metrics = {}
        
        if "cpu" in diagnostics:
            metrics["cpu_usage"] = diagnostics["cpu"].get("usage_percent", 0)
            metrics["cpu_temp"] = diagnostics["cpu"].get("temperature", None)
        
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
    
    def determine_severity(self, diagnostics: Dict[str, Any]) -> str:
        """Determine issue severity"""
        severity_score = 0
        
        # CPU check
        if diagnostics.get("cpu", {}).get("usage_percent", 0) > 90:
            severity_score += 3
        elif diagnostics.get("cpu", {}).get("usage_percent", 0) > 70:
            severity_score += 1
        
        # Memory check
        if diagnostics.get("memory", {}).get("percent", 0) > 95:
            severity_score += 3
        elif diagnostics.get("memory", {}).get("percent", 0) > 85:
            severity_score += 2
        
        # Disk check
        for partition in diagnostics.get("disk", {}).get("partitions", []):
            if partition.get("percent", 0) > 95:
                severity_score += 3
            elif partition.get("percent", 0) > 85:
                severity_score += 2
        
        if severity_score >= 6:
            return "Critical"
        elif severity_score >= 4:
            return "High"
        elif severity_score >= 2:
            return "Medium"
        return "Low"
    
    def is_slow_system_issue(self, issue: str) -> bool:
        """Check if issue is about slow system"""
        keywords = ["slow", "sluggish", "lag", "unresponsive", "freeze", "hang"]
        return any(keyword in issue.lower() for keyword in keywords)
    
    def is_app_failure_issue(self, issue: str) -> bool:
        """Check if issue is about app failure"""
        keywords = ["crash", "won't open", "not opening", "fails", "error", "doesn't work", "fail to open"]
        return any(keyword in issue.lower() for keyword in keywords)
    
    def is_startup_issue(self, issue: str) -> bool:
        """Check if issue is about startup"""
        keywords = ["startup", "boot", "start", "won't boot", "slow startup"]
        return any(keyword in issue.lower() for keyword in keywords)
    
    def is_disk_issue(self, issue: str) -> bool:
        """Check if issue is about disk"""
        keywords = ["disk", "storage", "space", "drive", "full"]
        return any(keyword in issue.lower() for keyword in keywords)
    
    def is_network_issue(self, issue: str) -> bool:
        """Check if issue is about network"""
        keywords = ["network", "internet", "wifi", "connection", "ethernet", "slow download"]
        return any(keyword in issue.lower() for keyword in keywords)
    
    def _analyze_slow_system(self, metrics: Dict, diagnostics: Dict) -> Dict[str, Any]:
        """Analyze slow system issue"""
        analysis = {
            "issue_type": "System Slowness",
            "reasoning": [],
            "findings": [],
            "recommendations": [],
            "next_steps": []
        }
        
        cpu = metrics.get("cpu_usage", 0)
        memory = metrics.get("memory_usage", 0)
        disk = metrics.get("disk_usage", [0])[0] if metrics.get("disk_usage") else 0
        
        # CPU Analysis
        if cpu > 80:
            analysis["findings"].append(f"⚠️ High CPU usage detected: {cpu}%")
            analysis["reasoning"].append(
                "High CPU usage indicates your processor is working at maximum capacity, "
                "causing slowness and lag."
            )
            top_cpu = metrics.get("top_cpu_processes", [])
            if top_cpu:
                analysis["findings"].append(
                    f"Top CPU consumer: {top_cpu[0].get('name', 'Unknown')} "
                    f"({top_cpu[0].get('cpu_percent', 0):.1f}%)"
                )
            analysis["recommendations"].extend([
                "• Close unnecessary background applications",
                "• Check for malware using Windows Defender or third-party antivirus",
                "• Disable unnecessary startup programs",
                "• Update drivers and Windows"
            ])
        
        # Memory Analysis
        if memory > 85:
            analysis["findings"].append(f"⚠️ High memory usage detected: {memory}%")
            analysis["reasoning"].append(
                "Your RAM is nearly full. When memory is exhausted, the system uses slower "
                "disk storage as virtual memory, causing significant slowdown."
            )
            top_mem = metrics.get("top_memory_processes", [])
            if top_mem:
                analysis["findings"].append(
                    f"Top memory consumer: {top_mem[0].get('name', 'Unknown')} "
                    f"({top_mem[0].get('memory_percent', 0):.1f}%)"
                )
            analysis["recommendations"].extend([
                "• Close memory-intensive applications",
                "• Restart your computer to clear memory cache",
                "• Consider upgrading RAM if this is a recurring issue",
                "• Check for memory leaks in running applications"
            ])
        
        # Disk Analysis
        if disk > 85:
            analysis["findings"].append(f"⚠️ Low disk space: {disk}% full")
            analysis["reasoning"].append(
                "When disk space is low, your system cannot create temporary files "
                "and cache efficiently, causing slowdown."
            )
            analysis["recommendations"].extend([
                "• Delete unnecessary files and folders",
                "• Empty the Recycle Bin",
                "• Use Disk Cleanup tool (cleanmgr.exe)",
                "• Uninstall unused applications",
                "• Consider archiving old files"
            ])
        
        if cpu < 50 and memory < 70 and disk < 80:
            analysis["reasoning"].append(
                "System resources appear normal. Slowness may be caused by "
                "network issues, driver problems, or malware."
            )
            analysis["recommendations"].extend([
                "• Run Windows Update to ensure all drivers are current",
                "• Scan for malware with Windows Defender",
                "• Check for network connectivity issues",
                "• Review Event Viewer for error messages"
            ])
        
        analysis["next_steps"] = [
            "1. Monitor resource usage over time",
            "2. Close resource-heavy applications",
            "3. Run system maintenance tools",
            "4. Restart the system if issues persist",
            "5. Check again for performance improvement"
        ]
        
        return analysis
    
    def _analyze_app_failure(self, app_name: str, metrics: Dict, diagnostics: Dict) -> Dict[str, Any]:
        """Analyze application failure"""
        analysis = {
            "issue_type": "Application Failure",
            "reasoning": [],
            "findings": [],
            "recommendations": [],
            "next_steps": []
        }
        
        memory = metrics.get("memory_usage", 0)
        disk = metrics.get("disk_usage", [0])[0] if metrics.get("disk_usage") else 0
        
        # Resource checks
        if memory > 80:
            analysis["findings"].append("Insufficient available memory")
            analysis["reasoning"].append(
                f"Memory usage is at {memory}%. Many applications require enough free memory to start."
            )
            analysis["recommendations"].append("• Close other applications to free up memory")
        
        if disk > 90:
            analysis["findings"].append("Critical disk space shortage")
            analysis["reasoning"].append(
                "Applications often fail to launch when disk space is critically low."
            )
            analysis["recommendations"].append("• Free up disk space immediately")
        
        # Generic solutions
        analysis["recommendations"].extend([
            "• Run the application as Administrator (right-click → Run as Administrator)",
            "• Restart the application",
            "• Restart your computer",
            "• Check for application updates",
            "• Disable antivirus temporarily to see if it's blocking the app",
            "• Reinstall the application",
            "• Check Windows Event Viewer > Windows Logs > Application for error details"
        ])
        
        analysis["findings"].append(
            f"Application '{app_name}' may have dependency or compatibility issues"
        )
        
        analysis["next_steps"] = [
            "1. Free up system resources",
            "2. Try running as Administrator",
            "3. Check application logs",
            "4. Verify application files integrity",
            "5. Reinstall if other steps fail"
        ]
        
        return analysis
    
    def _analyze_startup_issue(self, metrics: Dict, diagnostics: Dict) -> Dict[str, Any]:
        """Analyze startup issue"""
        analysis = {
            "issue_type": "Startup Performance",
            "reasoning": [],
            "findings": [],
            "recommendations": [],
            "next_steps": []
        }
        
        analysis["reasoning"].append(
            "Slow startup is usually caused by too many background programs starting with Windows."
        )
        
        analysis["findings"].append("Analyzing startup configuration...")
        
        analysis["recommendations"].extend([
            "• Open Task Manager (Ctrl+Shift+Esc)",
            "• Go to Startup tab",
            "• Disable unnecessary startup programs",
            "• Check Windows Services for unnecessary auto-start services",
            "• Update BIOS if available",
            "• Ensure antivirus isn't scanning at startup",
            "• Disable unnecessary startup items in Services"
        ])
        
        analysis["next_steps"] = [
            "1. Identify programs starting at boot",
            "2. Disable non-essential startup items",
            "3. Restart computer",
            "4. Measure startup time improvement",
            "5. Fine-tune further if needed"
        ]
        
        return analysis
    
    def _analyze_disk_issue(self, metrics: Dict, diagnostics: Dict) -> Dict[str, Any]:
        """Analyze disk issue"""
        analysis = {
            "issue_type": "Disk Problem",
            "reasoning": [],
            "findings": [],
            "recommendations": [],
            "next_steps": []
        }
        
        disk = metrics.get("disk_usage", [0])[0] if metrics.get("disk_usage") else 0
        
        if disk > 95:
            analysis["findings"].append(f"⚠️ Critical: Disk is {disk}% full")
            analysis["reasoning"].append(
                "Your disk is critically full. This will severely impact system performance "
                "and may cause application failures."
            )
        elif disk > 85:
            analysis["findings"].append(f"⚠️ Warning: Disk is {disk}% full")
            analysis["reasoning"].append(
                "Disk is nearly full. This impacts system performance and available space for updates."
            )
        
        analysis["recommendations"].extend([
            "• Delete temporary files: Run cleanmgr.exe",
            "• Remove unnecessary applications via Control Panel > Programs",
            "• Delete old downloads and documents",
            "• Empty Recycle Bin completely",
            "• Move files to external storage",
            "• Disable System Restore if disk space is critical",
            "• Compress old files",
            "• Consider adding more storage (SSD/HDD)"
        ])
        
        analysis["next_steps"] = [
            "1. Run Disk Cleanup utility",
            "2. Identify and delete large unnecessary files",
            "3. Uninstall unused programs",
            "4. Monitor disk space regularly",
            "5. Plan for additional storage if needed"
        ]
        
        return analysis
    
    def _analyze_network_issue(self, diagnostics: Dict) -> Dict[str, Any]:
        """Analyze network issue"""
        analysis = {
            "issue_type": "Network Problem",
            "reasoning": [],
            "findings": [],
            "recommendations": [],
            "next_steps": []
        }
        
        network = diagnostics.get("network", {})
        interfaces = network.get("interfaces", {})
        
        active_interfaces = [name for name, stats in interfaces.items() if stats.get("is_up")]
        
        if not active_interfaces:
            analysis["findings"].append("⚠️ No active network interfaces detected")
            analysis["reasoning"].append(
                "Your network adapters are not active or may have driver issues."
            )
        else:
            analysis["findings"].append(f"Active network interfaces: {', '.join(active_interfaces)}")
        
        analysis["recommendations"].extend([
            "• Check if network cable is properly connected",
            "• Restart your router/modem",
            "• Restart your network adapter",
            "• Update network drivers",
            "• Run Windows Network Troubleshooter",
            "• Check router configuration",
            "• Move closer to WiFi router if using wireless",
            "• Check for interference if using WiFi"
        ])
        
        analysis["next_steps"] = [
            "1. Check physical connections",
            "2. Restart network equipment",
            "3. Update network drivers",
            "4. Test connection",
            "5. Contact ISP if problem persists"
        ]
        
        return analysis
    
    def _analyze_general_issue(self, metrics: Dict, diagnostics: Dict) -> Dict[str, Any]:
        """Analyze general issue"""
        analysis = {
            "issue_type": "General System Issue",
            "reasoning": [],
            "findings": [],
            "recommendations": [],
            "next_steps": []
        }
        
        analysis["reasoning"].append(
            "I've analyzed your system. Running comprehensive diagnostics..."
        )
        
        # Check overall health
        cpu = metrics.get("cpu_usage", 0)
        memory = metrics.get("memory_usage", 0)
        
        if cpu < 50 and memory < 70:
            analysis["findings"].append("✓ System resources appear normal")
            analysis["recommendations"].extend([
                "• Perform a full Windows Update",
                "• Run System File Checker: sfc /scannow (run Command Prompt as Admin)",
                "• Check Event Viewer for errors",
                "• Scan for malware",
                "• Check driver updates"
            ])
        
        analysis["next_steps"] = [
            "1. Run Windows Update",
            "2. Scan for malware",
            "3. Update drivers",
            "4. Check system logs",
            "5. Perform clean boot if issues persist"
        ]
        
        return analysis
    
    def get_summary(self) -> str:
        """Get summary of analysis"""
        if not self.conversation_history:
            return "No analysis performed yet."
        
        latest = self.conversation_history[-1]
        analysis = latest["analysis"]
        
        summary = f"Issue: {analysis['issue']}\n"
        summary += f"Severity: {analysis['severity']}\n"
        summary += f"Type: {analysis.get('issue_type', 'Unknown')}\n\n"
        
        if analysis.get("findings"):
            summary += "Findings:\n"
            for finding in analysis["findings"]:
                summary += f"  {finding}\n"
        
        return summary
