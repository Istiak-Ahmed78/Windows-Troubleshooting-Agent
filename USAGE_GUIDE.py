"""
Usage Guide and Examples for AI PC Troubleshooting Agent
"""

USAGE_EXAMPLES = """
╔═════════════════════════════════════════════════════════════════════╗
║          AI PC TROUBLESHOOTING AGENT - USAGE GUIDE                 ║
╚═════════════════════════════════════════════════════════════════════╝

========================================================================
1. GETTING STARTED
========================================================================

Installation:
  1. Download/clone the project
  2. Run: pip install -r requirements.txt
  3. Launch with: python main.py
  
  OR simply double-click: run.bat (Windows)

First Run:
  • The agent will greet you with available options
  • Describe your issue in natural language
  • Agent will analyze and provide solutions

========================================================================
2. EXAMPLE ISSUES AND HOW TO DESCRIBE THEM
========================================================================

SLOW SYSTEM ISSUES:
─────────────────
User: "My PC is running very slow, everything is lagging"
Agent Response:
  ✓ Detects: System Slowness
  ✓ Runs: CPU, Memory, Disk diagnostics
  ✓ Provides: Resource analysis and optimization tips

User: "Everything freezes for a few seconds randomly"
Agent Response:
  ✓ Analyzes for: High CPU/Memory usage patterns
  ✓ Identifies: Resource bottlenecks
  ✓ Recommends: Background app closure

---

APPLICATION FAILURE ISSUES:
──────────────────────────
User: "Adobe Photoshop won't open anymore"
Agent Response:
  ✓ Detects: Application Failure
  ✓ Checks: Available memory and disk space
  ✓ Suggests: Administrator mode, reinstall, updates

User: "I get an error every time I try to open Chrome"
Agent Response:
  ✓ Analyzes: System resources
  ✓ Identifies: Possible causes (memory, corrupted files)
  ✓ Provides: Troubleshooting steps

---

DISK SPACE ISSUES:
─────────────────
User: "My C drive is almost full"
Agent Response:
  ✓ Detects: Low Disk Space
  ✓ Analyzes: Disk usage by partition
  ✓ Recommends: Cleanup procedures, file deletion, archiving

User: "I'm getting 'disk full' messages"
Agent Response:
  ✓ Identifies: Critical disk space
  ✓ Prioritizes: Immediate action required
  ✓ Lists: Quick cleanup options

---

NETWORK/CONNECTIVITY ISSUES:
───────────────────────────
User: "My internet connection is very slow"
Agent Response:
  ✓ Detects: Network Issue
  ✓ Checks: Network interfaces status
  ✓ Provides: Connection troubleshooting steps

User: "WiFi keeps disconnecting"
Agent Response:
  ✓ Analyzes: Network stability
  ✓ Checks: Driver status
  ✓ Suggests: Router restart, driver updates

---

STARTUP/BOOT ISSUES:
───────────────────
User: "My computer takes forever to start up"
Agent Response:
  ✓ Detects: Slow Startup
  ✓ Identifies: Startup program analysis
  ✓ Recommends: Disable unnecessary startup items

---

GENERAL PERFORMANCE:
───────────────────
User: "My computer is just not running well in general"
Agent Response:
  ✓ Performs: Comprehensive diagnostics
  ✓ Analyzes: All system components
  ✓ Provides: Complete optimization guide

========================================================================
3. USING THE DIAGNOSTICS PANEL
========================================================================

Right Panel Features:
─────────────────────
• System Diagnostics: Shows real-time system status
• CPU Section: Usage %, cores, temperature
• RAM Section: Memory usage, available space
• Disk Section: Partition usage for each drive
• Network Section: Active interfaces count

"Run Full Diagnostics" Button:
─────────────────────────────
Click to perform comprehensive analysis:
  1. Collects CPU, Memory, Disk data
  2. Checks network interfaces
  3. Analyzes top processes
  4. Updates display with current status

Color Coding:
─────────────
  Green (✓)   = Good / Normal
  Yellow (⚠)  = Warning / Moderate Issue
  Red (✗)     = Critical / Immediate Action Needed

========================================================================
4. UNDERSTANDING AGENT RESPONSES
========================================================================

Response Structure:
──────────────────
Issue Type:    Categorizes your problem
Severity:      Low | Medium | High | Critical

Findings:      What the agent discovered
  • Shows specific problems found
  • Includes metrics and percentages
  • Lists top resource consumers

Recommendations:  Step-by-step solutions
  • Prioritized by effectiveness
  • Easy to understand
  • Actionable steps

Next Steps:    Sequence to follow
  1. Do this first
  2. Then do this
  3. Finally do this

========================================================================
5. CONVERSATION TIPS
========================================================================

Be Specific:
────────────
Good:   "My computer is running slow when I have 10 Chrome tabs open"
Bad:    "It's slow"

Include Patterns:
─────────────────
Good:   "Slowness happens every afternoon around 3 PM"
Bad:    "Sometimes it's slow"

Mention Apps:
──────────────
Good:   "Excel and Outlook are causing my computer to freeze"
Bad:    "Some programs crash"

Describe Duration:
──────────────────
Good:   "This started happening last week"
Bad:    "It's been bad"

========================================================================
6. COMMON SCENARIOS
========================================================================

SCENARIO 1: Office Computer Running Slow
─────────────────────────────────────────
Issue:    "Office suite is slow, taking forever to open files"
Steps:
  1. Tell agent: "My Office programs are running slow"
  2. Review diagnostics panel
  3. Follow recommendations to close unnecessary apps
  4. Check for large files consuming resources
  5. Consider upgrading RAM if this is frequent

SCENARIO 2: Gaming Performance Issues
──────────────────────────────────────
Issue:    "My games are stuttering and lagging"
Steps:
  1. Tell agent: "Games are stuttering and lagging"
  2. Check CPU/Memory usage from diagnostics
  3. Close background apps affecting gaming
  4. Update GPU drivers (recommended by agent)
  5. Monitor temperature during gaming

SCENARIO 3: New Application Won't Launch
────────────────────────────────────────
Issue:    "Recently installed software crashes immediately"
Steps:
  1. Tell agent: "[App Name] won't open"
  2. Check available system resources
  3. Try running as Administrator
  4. Reinstall if still failing
  5. Check Windows Event Viewer for details

SCENARIO 4: Disk Space Critical
───────────────────────────────
Issue:    "Getting disk full warning"
Steps:
  1. Tell agent: "My C drive is full"
  2. Review disk diagnostics
  3. Run Disk Cleanup (cleanmgr.exe)
  4. Uninstall unused programs
  5. Archive old files to external drive

========================================================================
7. ADVANCED TIPS
========================================================================

Run Multiple Diagnostics:
────────────────────────
• Run diagnostics multiple times to identify intermittent issues
• Compare results to see trends
• Check history to track improvements

Check Event Viewer:
──────────────────
Agent may suggest checking Windows Event Viewer for detailed errors:
  1. Press Windows key + R
  2. Type: eventvwr.msc
  3. Go to Windows Logs > System
  4. Look for errors around the time issue occurred

Task Manager Usage:
──────────────────
Agent recommends Task Manager to close processes:
  1. Press Ctrl+Shift+Esc
  2. Click "Processes" tab
  3. Sort by CPU or Memory
  4. Right-click high consumers > End Task

PowerShell Commands:
───────────────────
For advanced users, agent may reference PowerShell commands:
  • Most can be run from admin command prompt
  • Copy and paste commands from Event Viewer
  • Research before running unfamiliar commands

========================================================================
8. WHEN TO SEEK ADDITIONAL HELP
========================================================================

Seek Help When:
────────────────
✗ Hardware failure (hard drive sounds, no boot)
✗ Blue screen errors repeatedly
✗ Malware suspected (strange popups, slowness even when idle)
✗ Physical damage visible
✗ Critical data loss situation

Provide to Support:
───────────────────
• Screenshot of agent diagnostics
• Recent changes made to system
• When the issue started
• Exact error messages
• Steps already tried

========================================================================
9. MAINTENANCE RECOMMENDATIONS
========================================================================

Weekly:
───────
• Run full diagnostics
• Check disk space
• Close unnecessary background apps

Monthly:
────────
• Run Windows Update
• Check for malware
• Update drivers
• Clear temporary files

Quarterly:
──────────
• Full system scan
• Backup important data
• Check storage devices
• Review startup programs

========================================================================
10. KEYBOARD SHORTCUTS & QUICK ACTIONS
========================================================================

GUI Navigation:
────────────────
Ctrl+C         Copy selected text from diagnostics
Ctrl+A         Select all in chat area
Ctrl+L         Clear chat (manual operation)
Enter          Send message to agent
Shift+Enter    New line in message (if multi-line supported)

System Tools Quick Access:
──────────────────────────
Task Manager:       Ctrl+Shift+Esc
Event Viewer:       Windows key + R, type: eventvwr.msc
Disk Cleanup:       Windows key + R, type: cleanmgr.exe
Services:           Windows key + R, type: services.msc
Device Manager:     Windows key + R, type: devmgmt.msc
System Properties:  Windows key + Break or Pause key

========================================================================

For more help, refer to README.md or modify config.py for custom settings.
"""

print(__doc__)

if __name__ == "__main__":
    print(USAGE_EXAMPLES)
