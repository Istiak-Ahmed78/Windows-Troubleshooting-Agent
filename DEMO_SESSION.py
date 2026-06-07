"""
DEMO SCRIPT - AI PC Troubleshooting Agent in Action
Shows the agent working through different scenarios
"""

DEMO_TRANSCRIPT = """
╔═══════════════════════════════════════════════════════════════════════╗
║                    AI PC TROUBLESHOOTING AGENT                       ║
║                          DEMO SESSION                                ║
╚═══════════════════════════════════════════════════════════════════════╝


════════════════════════════════════════════════════════════════════════
SCENARIO 1: USER HAS SLOW SYSTEM
════════════════════════════════════════════════════════════════════════

[Application Starts]
🤖 Agent: Welcome to AI PC Troubleshooting Agent!
           I can help diagnose issues like:
           • System running slow
           • Applications won't open
           • Low disk space
           • Network problems
           
           Describe your issue in the chat box below.

[User types and clicks Send]

You: My PC is running very slow, everything is lagging

🤖 Agent: I'm analyzing your PC issue. Please wait while I gather diagnostics...

💭 Reasoning: Gathering system information...

🤖 Agent: Analyzing your issue based on system data...

[Diagnostics Complete]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ANALYSIS RESULTS:

Issue Type: System Slowness
Severity Level: 🔴 HIGH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Key Findings:
📊 ⚠️  High CPU usage detected: 82.5%
📊 🎯 Top CPU consumer: Google Chrome (34%)
📊 💾 Memory usage: 85%
📊 💭 Available RAM: 3.2 GB out of 16 GB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recommended Solutions:
✓ Close unnecessary background applications
✓ Close extra Chrome tabs or browser extensions
✓ Disable Windows animations and visual effects
✓ Check Task Manager for other resource-heavy processes
✓ Update your system drivers
✓ Run Windows Update to ensure all updates are installed

Next Steps:
1. Monitor resource usage over time
2. Close Chrome tabs and restart browser
3. Run system maintenance tools
4. Restart the system
5. Check for malware with Windows Defender

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Right Panel Shows Real-Time Diagnostics]

CPU Status:
━━━━━━━━
Usage: 82.5%
Cores: 8
Status: High Usage

RAM Status:
━━━━━━━━
Used: 85%
Total: 16.00 GB
Available: 2.40 GB
Status: Warning - High Memory Usage

DISK Status:
━━━━━━━━
C: 72%
D: 45%
Status: Good

[User reviews findings and implements recommendations]

You: Thanks! I'll close Chrome and restart. Should help?

🤖 Agent: Yes! Chrome using 34% of CPU is significant. Closing it and
         restarting should provide immediate improvement. 
         After restarting, monitor your system again using the
         "Run Full Diagnostics" button to verify improvements.


════════════════════════════════════════════════════════════════════════
SCENARIO 2: USER HAS APPLICATION FAILURE
════════════════════════════════════════════════════════════════════════

[New Issue]

You: Adobe Photoshop won't open, I get an error immediately

🤖 Agent: I'm analyzing the application failure...

💭 Reasoning: Analyzing system resources for application startup...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ANALYSIS RESULTS:

Issue Type: Application Failure
Severity Level: 🟡 MEDIUM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Key Findings:
📊 Memory usage is elevated: 78%
📊 System has sufficient resources to run Photoshop
📊 Potential cause: Application corruption or missing dependencies

Possible Causes:
⚠️  Application files may be corrupted
⚠️  Missing required runtime libraries
⚠️  Compatibility issues with Windows updates
⚠️  Conflicting antivirus software

Recommended Solutions:
✓ Run Adobe Photoshop as Administrator
  (Right-click shortcut → Run as Administrator)

✓ Repair Adobe Photoshop installation
  (Control Panel → Programs → Programs and Features → 
   Adobe Photoshop → Change → Repair)

✓ Update Adobe Photoshop to latest version

✓ Temporarily disable antivirus to test if it's blocking

✓ Check Windows Event Viewer for specific error messages
  (Windows + R → eventvwr.msc)

✓ Reinstall Adobe Photoshop if other steps fail

Next Steps:
1. Try running as Administrator
2. If fails, repair installation
3. If still fails, check Event Viewer for error details
4. Update Adobe or reinstall if needed
5. Contact Adobe support with error message

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[User tries Administrator mode and it works]

You: Great! Running as Administrator worked! 

🤖 Agent: Excellent! The Administrator mode suggests a permissions issue.
         To make this permanent:
         1. Right-click Photoshop shortcut
         2. Select Properties
         3. Go to Advanced
         4. Check "Run as Administrator"
         5. Click OK
         
         This will avoid needing to do it manually each time!


════════════════════════════════════════════════════════════════════════
SCENARIO 3: USER HAS DISK SPACE ISSUE
════════════════════════════════════════════════════════════════════════

[New Issue]

You: My C drive is almost full. I keep getting warnings

🤖 Agent: Analyzing disk space usage...

💭 Reasoning: Checking all disk partitions and available space...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ANALYSIS RESULTS:

Issue Type: Disk Problem
Severity Level: 🔴 CRITICAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Key Findings:
📊 CRITICAL: Disk C: is 94% full
📊 Free space: 3.2 GB (Only 3.2 GB remaining)
📊 Windows needs ~10% free space for optimal performance
📊 System may become unstable with current space

Impact:
⚠️  System performance significantly degraded
⚠️  Cannot install Windows updates
⚠️  Applications may fail to launch
⚠️  System may become unstable
⚠️  Temporary file creation may fail

Recommended Solutions (In Order of Effectiveness):
✓ [URGENT] Run Disk Cleanup Tool (cleanmgr.exe)
  Press Windows + R, type: cleanmgr.exe, press Enter
  
✓ Delete Downloads folder old files
  Windows Explorer → Downloads → Delete old files
  
✓ Uninstall unused applications
  Control Panel → Programs → Uninstall a program
  
✓ Delete old Windows Update files
  cleanmgr.exe → Select "Previous Windows Installation(s)"
  
✓ Move files to external drive or cloud storage
  
✓ Consider upgrading to larger hard drive/SSD
  
✓ Disable or reduce System Restore size
  System Properties → System Protection → Configure

Next Steps (IMMEDIATE ACTION REQUIRED):
1. FREE UP 10+ GB OF SPACE IMMEDIATELY using Disk Cleanup
2. Uninstall unused programs
3. Delete temporary files
4. Monitor free space regularly
5. Consider adding storage

Estimated Space Savings:
- Disk Cleanup: 5-15 GB
- Uninstall programs: 10-50 GB
- Delete old files: 5-30 GB
- Total possible: 20-95 GB

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Right Panel Shows Disk Status]

DISK Status:
━━━━━━━━━━━━
C: 94% (🔴 CRITICAL - Almost Full)
  Free: 3.2 GB
  Total: 500 GB
  
D: 45% (Good)
  Free: 165 GB
  Total: 300 GB

[User runs Disk Cleanup]

You: I ran Disk Cleanup and freed up 8 GB. Better?

🤖 Agent: Good progress! You're now at 84% usage. 
         Recommended next steps:
         1. Uninstall 2-3 large unused programs (10-20 GB)
         2. Delete old files from Documents/Downloads
         3. Target getting to 70% usage for optimal performance
         
         Run Full Diagnostics again to see updated status.

[User continues cleanup and reaches 70%]

You: Got it to 70%, much better now

🤖 Agent: Excellent! 70% is a healthy level. 
         To maintain this:
         • Periodically check disk space
         • Run Disk Cleanup monthly
         • Move large files to D: drive when possible
         • Archive old documents
         • Consider scheduling automatic cleanups
         
         Your system should now perform better!


════════════════════════════════════════════════════════════════════════
SCENARIO 4: USER HAS NETWORK ISSUE
════════════════════════════════════════════════════════════════════════

[New Issue]

You: My internet connection is very slow today

🤖 Agent: Analyzing network connectivity...

💭 Reasoning: Checking network interfaces and connection status...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ANALYSIS RESULTS:

Issue Type: Network Problem
Severity Level: 🟡 MEDIUM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Key Findings:
📊 WiFi (Wireless): Connected and active ✓
📊 Ethernet: Not connected
📊 Network packets: 234,892 sent, 198,474 received
📊 Interface speed: 72 Mbps

Possible Causes:
⚠️  WiFi signal interference or congestion
⚠️  Router performance degradation
⚠️  Outdated network drivers
⚠️  Too many connected devices
⚠️  Network congestion from background apps

Recommended Solutions:
✓ Restart your WiFi router
  (Unplug for 30 seconds, plug back in, wait 2 minutes)

✓ Move closer to your WiFi router
  (Walls and distance reduce signal strength)

✓ Check for WiFi interference
  (Microwaves, cordless phones can interfere)

✓ Update network drivers
  (Device Manager → Network adapters → Right-click → Update driver)

✓ Check for bandwidth-heavy apps
  (Task Manager → Performance → Resource Monitor)

✓ Run Windows Network Troubleshooter
  (Settings → Network → Status → Troubleshoot)

✓ Use Ethernet cable if available
  (More stable than WiFi)

✓ Check with ISP if problem persists
  (May be ISP-side issue)

Next Steps:
1. Restart WiFi router (30 seconds)
2. Test speed after restart
3. If still slow, update network drivers
4. Check for interference
5. Switch to Ethernet if available

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Right Panel Shows Network Status]

NETWORK Status:
━━━━━━━━━━━━━
Interfaces: 2/3 active
WiFi (Wireless): Connected ✓
Ethernet: Disconnected
Status: Slow Connection Detected

[User restarts router]

You: I restarted the router and it's much faster now!

🤖 Agent: Great! Router restart cleared cached data and reset 
         connections. Your connection should remain stable now.
         
         To prevent future slowness:
         • Restart router monthly
         • Keep router in open location
         • Keep drivers updated
         • Monitor for interference
         • Use Ethernet for critical tasks


════════════════════════════════════════════════════════════════════════
SCENARIO 5: USER RUNS FULL DIAGNOSTICS (NO SPECIFIC ISSUE)
════════════════════════════════════════════════════════════════════════

[User clicks "Run Full Diagnostics" button with no issue]

🤖 Agent: Running comprehensive system diagnostics...

💭 Reasoning: Gathering complete system information...

[Diagnostics Progress]
  ⏳ Checking CPU... ✓
  ⏳ Analyzing Memory... ✓
  ⏳ Scanning Disks... ✓
  ⏳ Checking Network... ✓
  ⏳ Analyzing Processes... ✓

💭 Reasoning: System resources appear normal...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SYSTEM HEALTH REPORT:

Overall Status: ✅ GOOD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CPU Status: ✅ GOOD
  Usage: 28%
  Temperature: 52°C
  Status: Normal operation

Memory Status: ✅ GOOD
  Used: 45%
  Available: 8.8 GB / 16 GB
  Status: Healthy

Disk Status: ✅ GOOD
  C: 65% (Good)
  D: 38% (Good)
  Status: Adequate space

Network Status: ✅ GOOD
  WiFi: Connected
  Ethernet: Available
  Status: Normal

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

System Recommendations:
✓ System is running optimally
✓ No critical issues detected
✓ All metrics within healthy ranges
✓ Perform routine maintenance:
  • Windows Update check
  • Antivirus scan
  • Disk cleanup (monthly)
  • Driver updates

Next Steps:
1. Maintain current status with regular maintenance
2. Monitor resources periodically
3. Keep Windows and drivers updated
4. Run antivirus scans regularly
5. Schedule monthly disk cleanup

Your system is healthy! Keep up the good maintenance.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Right Panel Shows Current System Status]

CPU Status:
━━━━━━━━
Usage: 28%
Status: ✅ GOOD

Memory Status:
━━━━━━━━
Used: 45%
Available: 8.8 GB
Status: ✅ GOOD

Disk Status:
━━━━━━━━
C: 65% ✅
D: 38% ✅
Status: ✅ GOOD

Network Status:
━━━━━━━━
Interfaces: 2/2 active ✅
Status: ✅ GOOD


════════════════════════════════════════════════════════════════════════
END OF DEMO SESSION
════════════════════════════════════════════════════════════════════════

Summary of Agent Capabilities Demonstrated:

✅ Automatic Issue Classification
   - System Slowness (high CPU/Memory)
   - Application Failure (resource constraints)
   - Disk Problems (low space)
   - Network Issues (connectivity)
   - General Health (comprehensive scan)

✅ Intelligent Analysis
   - Resource usage detection
   - Severity assessment
   - Root cause identification
   - Impact analysis

✅ Smart Recommendations
   - Prioritized solutions
   - Step-by-step instructions
   - Expected outcomes
   - Prevention tips

✅ Real-time Diagnostics
   - CPU, Memory, Disk monitoring
   - Network interface checking
   - Process analysis
   - Health status display

✅ User-Friendly Interface
   - Chat-based conversation
   - Natural language understanding
   - Clear formatting
   - Color-coded severity

════════════════════════════════════════════════════════════════════════

To run this demo yourself:
  1. Start the application (run.bat or python main.py)
  2. Try the same issue descriptions
  3. Review the agent's analysis
  4. Follow the recommendations
  5. Monitor your system improvements

The agent will provide specific recommendations based on your actual
system status, so results may vary from this demo.

Happy troubleshooting!

════════════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(DEMO_TRANSCRIPT)
