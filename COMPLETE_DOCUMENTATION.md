# AI PC Troubleshooting Agent - Complete Documentation

## Overview

The **AI PC Troubleshooting Agent** is a comprehensive offline Windows troubleshooting application built with CustomTkinter. It intelligently diagnoses PC issues and provides detailed recommendations through a conversational chat interface.

### Key Capabilities

- **Real-time System Monitoring**: CPU, RAM, Disk, Temperature, Network
- **Intelligent Issue Detection**: Identifies problem types automatically
- **Process Analysis**: Shows resource-consuming applications
- **Severity Assessment**: Categorizes issues as Critical, High, Medium, or Low
- **Smart Recommendations**: Context-aware solutions based on analysis
- **No Internet Required**: Completely offline operation
- **Modern GUI**: Intuitive chat-based interface

---

## Architecture

### Project Structure

```
troubleshooting_ai_agent/
├── main.py                    # Original GUI application
├── enhanced_main.py          # Enhanced version with features
├── diagnostics.py            # Windows diagnostics module
├── troubleshooting_engine.py # AI reasoning engine
├── advanced_diagnostics.py   # Extended diagnostics tools
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── run.bat                   # Windows batch launcher
├── launch.ps1               # PowerShell launcher
├── README.md                # Main documentation
├── QUICK_START.txt          # Quick start guide
├── USAGE_GUIDE.py           # Detailed usage guide
└── COMPLETE_DOCUMENTATION.md # This file
```

### Module Overview

#### 1. **main.py** - GUI Application
- CustomTkinter-based chat interface
- Real-time diagnostics display
- User input handling
- Threading for responsive UI
- Color-coded system information

#### 2. **diagnostics.py** - System Analysis
Core diagnostic functions:
- `WindowsDiagnostics` class
- CPU monitoring (usage, temperature, per-core)
- Memory analysis (RAM, swap)
- Disk space monitoring (all partitions)
- Process analysis (top CPU/memory consumers)
- Network interface checking
- Battery status (if available)

Key Methods:
```python
get_system_info()           # Comprehensive system snapshot
get_cpu_info()             # CPU metrics
get_memory_info()          # RAM metrics
get_disk_info()            # Disk space
get_top_processes()        # Top processes
diagnose_slow_system()     # Slow system analysis
diagnose_app_failure()     # App failure diagnosis
```

#### 3. **troubleshooting_engine.py** - AI Reasoning
Intelligent analysis and recommendations:
- `TroubleshootingEngine` class
- Issue classification
- Severity determination
- Recommendation generation
- Conversation history

Issue Types:
- System Slowness
- Application Failure
- Startup Issues
- Disk Problems
- Network Issues
- General System Issues

#### 4. **advanced_diagnostics.py** - Extended Analysis
Additional system checks:
- Windows Update status
- Antivirus/Defender status
- Boot time analysis
- Disk error detection
- Service status
- Driver analysis
- System uptime
- Event Log analysis
- Comprehensive health reports

#### 5. **config.py** - Configuration
Customizable settings:
- GUI appearance (colors, fonts)
- Diagnostic thresholds
- Severity scoring
- Issue keywords
- Critical services
- Recommendations database
- Feature flags

---

## Installation & Setup

### Prerequisites

- **Windows 7, 8, 10, or 11**
- **Python 3.8+**
- **150 MB free disk space**
- **Administrator access** (recommended for full diagnostics)

### Installation Steps

#### Method 1: Automatic (Windows)
```batch
cd path\to\troubleshooting_ai_agent
run.bat
```

#### Method 2: PowerShell
```powershell
powershell -ExecutionPolicy Bypass -File launch.ps1
```

#### Method 3: Manual
```bash
cd path\to\troubleshooting_ai_agent
pip install -r requirements.txt
python main.py
```

### Dependencies

- **customtkinter>=5.2.0** - Modern GUI framework
- **psutil>=5.9.6** - System and process monitoring
- **wmi>=1.5.1** - Windows WMI interface
- **pywin32>=305** - Windows API access

---

## Usage Guide

### Starting the Application

1. **Launch**: Run main.py or use launcher script
2. **Welcome**: Agent greets you with available options
3. **Describe Issue**: Type your problem in chat
4. **Analyze**: Agent performs diagnostics
5. **Review**: Check findings and recommendations
6. **Implement**: Follow suggested solutions

### Common Issue Descriptions

| Issue Type | Example Description |
|-----------|-------------------|
| Slow System | "My PC is running very slow" |
| App Failure | "Adobe won't open" |
| Disk Space | "My C drive is almost full" |
| Network | "Internet connection is slow" |
| Startup | "Computer takes forever to boot" |
| Performance | "System is not running well" |

### Understanding Agent Response

```
Issue Type:      System Slowness
Severity:        High
─────────────────────────────────
Finding 1:       ⚠️ High CPU usage detected: 85%
Finding 2:       📊 Top CPU consumer: Google Chrome (35%)
Finding 3:       💾 Memory usage: 78%
─────────────────────────────────
Recommendation 1: • Close unnecessary background applications
Recommendation 2: • Update drivers and Windows
Recommendation 3: • Check for malware using Windows Defender
─────────────────────────────────
Next Step 1:     1. Monitor resource usage over time
Next Step 2:     2. Close resource-heavy applications
Next Step 3:     3. Run system maintenance tools
```

### Diagnostics Panel

The right side of the interface displays:

**CPU Section**
- Current usage percentage
- Number of cores
- Temperature (if available)
- Health status

**Memory Section**
- Used percentage
- Total available RAM
- Current availability
- Status

**Disk Section**
- Usage for each partition
- Percentage full
- Free space
- Drive letters

**Network Section**
- Active interfaces count
- Total interfaces
- Connection status

---

## Feature Details

### Issue Classification

The agent automatically detects issue types:

#### 1. **System Slowness**
Indicators:
- High CPU usage (>80%)
- High memory usage (>85%)
- Low disk space (<15% free)

Actions:
- Identifies resource hogs
- Checks for malware symptoms
- Recommends optimization

#### 2. **Application Failure**
Indicators:
- Insufficient memory
- Critical disk space
- Missing dependencies

Solutions:
- Resource cleanup
- Administrator mode
- Reinstallation steps

#### 3. **Startup Issues**
Indicators:
- Slow boot time
- Too many startup programs
- Service issues

Recommendations:
- Disable startup programs
- Optimize services
- Check BIOS settings

#### 4. **Disk Problems**
Indicators:
- Low disk space (<20%)
- Critical space (<5%)
- Unbalanced partitions

Solutions:
- Disk cleanup procedures
- File organization
- Storage expansion options

#### 5. **Network Issues**
Indicators:
- No active interfaces
- Disabled adapters
- Driver problems

Troubleshooting:
- Interface status
- Driver updates
- Hardware check

### Severity Levels

**Critical** (Red)
- Immediate action required
- System may become unusable
- Performance severely impacted

**High** (Yellow)
- Significant issues
- Notable performance degradation
- Action recommended soon

**Medium** (Orange)
- Moderate impact
- Some slowdown present
- Address when convenient

**Low** (Green)
- Minor issues
- Minimal impact
- Can be addressed later

### Recommendation System

Recommendations are:
- **Prioritized** by effectiveness
- **Specific** to your issue
- **Actionable** with clear steps
- **Safe** for Windows systems
- **Tested** approaches

---

## Advanced Features

### Running Diagnostics

Click "Run Full Diagnostics" button:
1. Collects CPU metrics
2. Samples memory usage
3. Scans all disk partitions
4. Checks network interfaces
5. Analyzes running processes
6. Updates display

Time: ~5-10 seconds per scan

### Conversation History

The agent maintains:
- Issue descriptions
- Analysis results
- Recommendations provided
- Severity assessments

Use this to:
- Track recurring issues
- Identify patterns
- Monitor improvements
- Compare analyses

### Real-time Monitoring

System info updates when:
- "Run Full Diagnostics" is clicked
- Issue is analyzed
- Application starts

Shows:
- CPU usage percentage
- Memory utilization
- Disk space per partition
- Current system health

---

## Configuration

### Customizing Colors

Edit `config.py`:

```python
GUI_CONFIG = {
    "header_color": "#1a1a2e",          # Dark blue
    "primary_color": "#00d4ff",         # Cyan
    "success_color": "#00ff88",         # Green
    "warning_color": "#ffaa00",         # Orange
    "error_color": "#ff6b6b",           # Red
    "info_color": "#4ecdc4",            # Teal
}
```

### Adjusting Thresholds

Edit `config.py` diagnostics thresholds:

```python
DIAGNOSTICS_THRESHOLDS = {
    "cpu": {"high": 80, "moderate": 50},
    "memory": {"critical": 95, "high": 85},
    "disk": {"critical": 95, "high": 85},
}
```

### Adding Recommendations

Edit `config.py` recommendations database:

```python
RECOMMENDATIONS = {
    "high_cpu": [
        "• Your custom recommendation here",
    ],
}
```

---

## Troubleshooting

### Common Issues

#### Python Not Found
**Error**: 'python' is not recognized
**Solution**: 
1. Install Python from python.org
2. Check "Add Python to PATH"
3. Restart Command Prompt

#### Module Not Found
**Error**: ModuleNotFoundError: No module named 'customtkinter'
**Solution**:
```bash
pip install -r requirements.txt
```

#### Permission Denied
**Error**: PermissionError or Access Denied
**Solution**:
1. Run as Administrator
2. Right-click → Run as Administrator
3. Use PowerShell with elevated privileges

#### Temperature Not Showing
**Note**: Not critical
**Solution**:
1. Run as Administrator
2. May require WMI access
3. Other diagnostics still work

#### Slow Diagnostics
**Note**: First run takes longer
**Solution**:
1. Results cache after first run
2. Close heavy applications
3. Be patient on slower systems

---

## System Requirements

### Minimum
- Windows 7 SP1 or later
- Python 3.8
- 100 MB free disk space
- 512 MB RAM

### Recommended
- Windows 10/11
- Python 3.10+
- 500 MB free disk space
- 2 GB RAM

### Administrator Access
Recommended for:
- Temperature monitoring
- Service management
- WMI data collection
- System file access

---

## Performance Considerations

### Diagnostics Impact

Running diagnostics:
- CPU: <5% increase temporarily
- Memory: ~50-100 MB additional
- Disk: Minimal (read-only)
- Network: No bandwidth used

Duration:
- Basic scan: 2-3 seconds
- Full diagnostics: 5-10 seconds
- First run: May take longer

### Optimization Tips

1. **Close unnecessary applications** before running diagnostics
2. **Run as Administrator** for complete data
3. **Run periodically** to track trends
4. **Don't leave running 24/7** - run when needed

---

## Security & Privacy

### No Data Collection
- **Offline only** - no internet required
- **Local analysis** - no data sent anywhere
- **No tracking** - no analytics or telemetry
- **No reporting** - no automated submissions

### Safe Operations
- **Read-only** - no system modifications by default
- **Safe recommendations** - proven techniques
- **No malware** - clean, verified code
- **Reversible steps** - can undo changes

### Windows Security
The agent works with:
- Windows Defender
- antivirus software
- Firewall
- Standard permissions

---

## Advanced Usage

### Command Line Arguments

Currently uses defaults, but can be extended:

```python
python main.py [options]
```

### Integration

Can be integrated with:
- IT management systems
- Monitoring solutions
- Automated maintenance scripts
- Custom tools

### Extension

Easily add:
- Custom diagnostics
- New issue types
- Additional recommendations
- External tool integration

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Enter | Send message |
| Ctrl+A | Select all (in text areas) |
| Ctrl+C | Copy selected text |

### System Tools Quick Access

| Tool | Command |
|------|---------|
| Task Manager | Ctrl+Shift+Esc |
| Event Viewer | eventvwr.msc |
| Disk Cleanup | cleanmgr.exe |
| Services | services.msc |
| Device Manager | devmgmt.msc |

---

## Tips & Best Practices

### Best Results

1. **Describe issues clearly**
   - Include what you were doing
   - Note when it started
   - Mention patterns

2. **Run diagnostics regularly**
   - Daily for monitoring
   - After major changes
   - When issues appear

3. **Follow recommendations**
   - Start with easiest steps
   - Test after each change
   - Document what works

4. **Keep system updated**
   - Windows updates
   - Driver updates
   - Application updates

### Maintenance Schedule

**Daily**
- Monitor critical processes
- Check for updates

**Weekly**
- Run full diagnostics
- Check disk space
- Verify backups

**Monthly**
- System cleanup
- Malware scan
- Driver updates

**Quarterly**
- Full system analysis
- Data backup
- Performance review

---

## Limitations

### Known Limitations

1. **Windows only** - Linux/Mac not supported
2. **Local analysis only** - no cloud features
3. **Automated fixes limited** - mostly recommendations
4. **Some data requires admin** - temperature, services
5. **Depends on Windows APIs** - WMI access needed

### Future Enhancements

Potential additions:
- Automated repair options
- Historical trending
- Predictive analysis
- Export reports
- Scheduled monitoring
- Remote diagnostics

---

## Support & Contributing

### Getting Help

1. **Read documentation**
   - README.md
   - QUICK_START.txt
   - USAGE_GUIDE.py

2. **Check configuration**
   - Review config.py
   - Verify settings
   - Check thresholds

3. **Run diagnostics**
   - Gather detailed info
   - Check system logs
   - Note specific errors

### Reporting Issues

When reporting problems:
1. Describe the issue clearly
2. Include your Windows version
3. Mention Python version
4. Provide error messages
5. List steps to reproduce

### Contributing

To improve:
1. Fork the repository
2. Make improvements
3. Test thoroughly
4. Submit changes
5. Include documentation

---

## Legal & Disclaimer

### License

This software is provided as-is for educational and personal use.

### Disclaimer

- **No warranty** - use at your own risk
- **Backup first** - before making changes
- **Professional help** - for critical issues
- **System impact** - test in safe environment

### Responsibility

Users are responsible for:
- Understanding recommendations
- Backing up data
- Testing changes
- Following best practices
- Consulting professionals

---

## Conclusion

The AI PC Troubleshooting Agent provides intelligent, comprehensive PC diagnosis and recommendations through an easy-to-use interface.

**Start by:**
1. Installing the application
2. Running full diagnostics
3. Describing your issue
4. Following recommendations
5. Monitoring improvements

For detailed help, refer to individual documentation files or the configuration settings.

**Happy troubleshooting!**

---

*Last Updated: 2026*
*Version: 1.0*
*Platform: Windows 7+*
