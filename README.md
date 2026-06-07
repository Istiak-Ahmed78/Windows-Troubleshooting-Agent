# AI PC Troubleshooting Agent

A comprehensive offline Windows troubleshooting agent with a modern GUI built using CustomTkinter. The agent intelligently analyzes PC issues and provides detailed diagnostics and solutions.

## Features

✨ **Smart Issue Detection**
- Automatically identifies issue types (slow system, app failure, disk issues, etc.)
- Analyzes system resources in real-time
- Provides severity assessment

🔍 **Comprehensive Diagnostics**
- CPU usage and temperature monitoring
- RAM and memory analysis
- Disk space and partition monitoring
- Network interface checking
- Process and application monitoring
- Battery status (if available)

💡 **Intelligent Recommendations**
- Context-aware solution suggestions
- Step-by-step troubleshooting guides
- Severity-based prioritization
- Detailed reasoning for findings

🎨 **Modern GUI**
- Real-time chat interface
- Live system monitoring
- Color-coded severity indicators
- Responsive and intuitive design

## Requirements

- Windows OS
- Python 3.8+
- Required packages (see requirements.txt)

## Installation

1. Clone or download the project:
```bash
cd troubleshooting_ai_agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Note: Some features like temperature monitoring may require elevated privileges (Run as Administrator).

## Usage

### Basic Usage

1. Run the application:
```bash
python main.py
```

2. Describe your PC issue in the chat box:
   - "My PC is running slow"
   - "An application won't open"
   - "My disk is full"
   - "Network is unstable"

3. The agent will:
   - Analyze your issue
   - Run system diagnostics
   - Display findings and recommendations
   - Suggest next steps

### Running Diagnostics

Click the "Run Full Diagnostics" button to get a comprehensive analysis of your system's current state.

## Project Structure

```
troubleshooting_ai_agent/
├── main.py                      # Main GUI application
├── diagnostics.py              # Windows system diagnostics module
├── troubleshooting_engine.py   # AI reasoning and analysis engine
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Module Details

### diagnostics.py
Handles all system diagnostics:
- `WindowsDiagnostics`: Main class for system analysis
- Methods for CPU, memory, disk, network monitoring
- Health analysis functions
- Windows-specific system checks

### troubleshooting_engine.py
Implements AI reasoning:
- `TroubleshootingEngine`: Core reasoning engine
- Issue classification and analysis
- Recommendation generation
- Conversation history tracking

### main.py
GUI application:
- `TroubleshootingAgentGUI`: Main interface
- Chat-based communication
- Real-time diagnostics display
- Threading for responsive UI

## Issue Types Detected

The agent can diagnose:

1. **System Slowness**
   - High CPU/Memory/Disk usage
   - Background process analysis
   - Malware/bloatware detection suggestions

2. **Application Failures**
   - Resource insufficiency
   - Compatibility issues
   - Missing dependencies

3. **Startup Issues**
   - Slow boot times
   - Startup program analysis
   - Service optimization

4. **Disk Problems**
   - Low disk space
   - Partition usage
   - Storage optimization

5. **Network Issues**
   - Interface status
   - Connectivity problems
   - Driver issues

## Tips for Best Results

1. **Run as Administrator**: For full diagnostics access, especially for temperature and service monitoring
2. **Background Apps**: Close unnecessary apps before diagnostics for accurate readings
3. **Multiple Diagnostics**: Run multiple times to identify intermittent issues
4. **System Logs**: Check Windows Event Viewer for detailed error information
5. **Updates**: Keep Windows and drivers updated for optimal performance

## Troubleshooting

### Temperature Not Showing
- May require administrator privileges
- Some systems don't expose temperature data
- Not critical for other diagnostics

### Limited Service Information
- Run as Administrator for full service access
- Some system services may require elevated privileges

### Performance Impact
- Diagnostics take a few seconds to complete
- Does not significantly impact system performance
- Results are cached during the session

## Future Enhancements

Potential improvements:
- Historical data tracking
- Malware detection integration
- Automated fixes for common issues
- System optimization recommendations
- Performance trend analysis
- Export reports functionality
- Remote diagnostic capability

## License

Open source - feel free to modify and use as needed

## Support

For issues or suggestions, modify the code as needed for your specific requirements.

## Disclaimer

Always backup important data before making system changes. The agent provides recommendations based on diagnostics but should be used in conjunction with professional IT support for critical issues.
