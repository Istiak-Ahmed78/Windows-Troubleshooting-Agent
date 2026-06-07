"""
Configuration file for the AI Troubleshooting Agent
"""

# GUI Configuration
GUI_CONFIG = {
    "window_title": "🤖 AI PC Troubleshooting Agent",
    "window_size": "1200x800",
    "theme": "dark",
    "color_theme": "blue",
    
    # Colors
    "header_color": "#1a1a2e",
    "primary_color": "#00d4ff",
    "success_color": "#00ff88",
    "warning_color": "#ffaa00",
    "error_color": "#ff6b6b",
    "info_color": "#4ecdc4",
    "background_color": "#0f0f1e",
    "text_color": "#e0e0e0",
}

# Diagnostics Thresholds
DIAGNOSTICS_THRESHOLDS = {
    "cpu": {
        "high": 80,
        "moderate": 50,
        "unit": "%"
    },
    "memory": {
        "critical": 95,
        "high": 85,
        "moderate": 70,
        "unit": "%"
    },
    "disk": {
        "critical": 95,
        "high": 85,
        "moderate": 70,
        "unit": "%"
    },
    "cpu_temperature": {
        "high": 85,
        "moderate": 70,
        "unit": "°C"
    },
    "swap_memory": {
        "high": 80,
        "moderate": 50,
        "unit": "%"
    }
}

# Severity Scoring
SEVERITY_SCORES = {
    "critical_cpu": 3,
    "high_cpu": 1,
    "critical_memory": 3,
    "high_memory": 2,
    "moderate_memory": 1,
    "critical_disk": 3,
    "high_disk": 2,
    "moderate_disk": 1,
}

# Process Monitoring
PROCESS_CONFIG = {
    "top_n_processes": 10,
    "cpu_threshold": 10,  # % - only show if above this
    "memory_threshold": 5,  # % - only show if above this
}

# Issue Keywords
ISSUE_KEYWORDS = {
    "slow_system": ["slow", "sluggish", "lag", "unresponsive", "freeze", "hang", "stuck"],
    "app_failure": ["crash", "won't open", "not opening", "fails", "error", "doesn't work", "fail to open"],
    "startup": ["startup", "boot", "start", "won't boot", "slow startup"],
    "disk": ["disk", "storage", "space", "drive", "full"],
    "network": ["network", "internet", "wifi", "connection", "ethernet", "slow download"],
    "battery": ["battery", "power", "charging"],
    "temperature": ["hot", "temperature", "overheating", "thermal"],
}

# Critical Services to Monitor
CRITICAL_SERVICES = [
    "wuauserv",      # Windows Update
    "WinDefend",     # Windows Defender
    "Bits",          # Background Intelligent Transfer Service
    "eventlog",      # Event Log
    "NlaSvc",        # Network Location Awareness
    "AudioSrv",      # Audio Service
    "dnscache",      # DNS Client
    "Dhcp",          # DHCP Client
]

# Recommendations Database
RECOMMENDATIONS = {
    "high_cpu": [
        "• Close unnecessary background applications",
        "• Check for malware using Windows Defender",
        "• Disable unnecessary startup programs",
        "• Update drivers and Windows",
        "• Check Task Manager for resource-heavy processes",
    ],
    "high_memory": [
        "• Close memory-intensive applications",
        "• Restart your computer to clear memory cache",
        "• Check for memory leaks in running applications",
        "• Disable unnecessary browser extensions",
        "• Consider upgrading RAM for better performance",
    ],
    "low_disk": [
        "• Delete temporary files (run cleanmgr.exe)",
        "• Remove unnecessary applications",
        "• Delete old downloads and documents",
        "• Empty Recycle Bin completely",
        "• Move files to external storage",
        "• Uninstall unused programs",
    ],
    "app_failure": [
        "• Run the application as Administrator",
        "• Restart the application and system",
        "• Check for application updates",
        "• Disable antivirus temporarily to check if it's blocking",
        "• Reinstall the application",
        "• Check Event Viewer for error details",
    ],
    "slow_startup": [
        "• Open Task Manager (Ctrl+Shift+Esc)",
        "• Disable unnecessary startup programs",
        "• Update BIOS if available",
        "• Ensure antivirus isn't scanning at startup",
        "• Disable unnecessary services",
        "• Check for malware",
    ],
    "network_issues": [
        "• Check if network cable is properly connected",
        "• Restart your router/modem",
        "• Update network drivers",
        "• Run Windows Network Troubleshooter",
        "• Disable WiFi and use Ethernet if possible",
        "• Check router configuration",
    ],
}

# Feature Flags
FEATURES = {
    "enable_advanced_diagnostics": True,
    "enable_event_log_analysis": True,
    "enable_antivirus_check": True,
    "enable_windows_update_check": True,
    "enable_driver_analysis": True,
    "enable_boot_time_analysis": True,
    "enable_service_monitoring": True,
    "enable_temperature_monitoring": True,
}

# Logging
LOGGING_CONFIG = {
    "enabled": True,
    "log_file": "troubleshooting_agent.log",
    "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    "max_log_size": 5 * 1024 * 1024,  # 5MB
    "backup_count": 3,
}

# Chat Configuration
CHAT_CONFIG = {
    "max_history": 100,
    "auto_scroll": True,
    "show_timestamps": False,
    "line_wrap": True,
}

# Diagnostic Update Intervals
UPDATE_INTERVALS = {
    "real_time_metrics": 2,  # seconds - for real-time monitoring
    "full_diagnostics": 10,  # seconds - for full system scan
    "background_check": 30,  # seconds - for background monitoring
}
