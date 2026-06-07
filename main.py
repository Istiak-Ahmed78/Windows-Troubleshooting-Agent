"""
AI Troubleshooting Agent GUI
Main application with CustomTkinter interface
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import json
from datetime import datetime
from diagnostics import WindowsDiagnostics, format_bytes
from troubleshooting_engine import TroubleshootingEngine


class TroubleshootingAgentGUI:
    """Main GUI for the troubleshooting agent"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AI PC Troubleshooting Agent")
        self.root.geometry("1200x800")
        
        # Initialize backends
        self.diagnostics = WindowsDiagnostics()
        self.engine = TroubleshootingEngine()
        self.current_diagnostics = None
        self.is_diagnosing = False
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create UI
        self.create_widgets()
        self.setup_layout()
        
    def create_widgets(self):
        """Create all UI widgets"""
        
        # ===== Main Container =====
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # ===== Header =====
        header = ctk.CTkFrame(self.main_container, fg_color="#1a1a2e")
        header.pack(fill="x", padx=0, pady=0)
        
        title = ctk.CTkLabel(
            header,
            text="🤖 AI PC Troubleshooting Agent",
            font=("Helvetica", 24, "bold"),
            text_color="#00d4ff"
        )
        title.pack(pady=15)
        
        subtitle = ctk.CTkLabel(
            header,
            text="Intelligent system diagnostics and problem solving",
            font=("Helvetica", 12),
            text_color="#888888"
        )
        subtitle.pack(pady=(0, 15))
        
        # ===== Main Content =====
        content = ctk.CTkFrame(self.main_container)
        content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left Panel - Chat Interface
        left_panel = ctk.CTkFrame(content)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        chat_label = ctk.CTkLabel(
            left_panel,
            text="Chat Interface",
            font=("Helvetica", 14, "bold")
        )
        chat_label.pack(pady=(0, 10))
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            left_panel,
            height=20,
            width=60,
            font=("Courier", 10),
            bg="#0f0f1e",
            fg="#e0e0e0",
            insertbackground="#00d4ff"
        )
        self.chat_display.pack(fill="both", expand=True, pady=(0, 10))
        self.chat_display.config(state="disabled")
        
        # Configure text tags
        self.chat_display.tag_config("user", foreground="#00d4ff", font=("Courier", 10, "bold"))
        self.chat_display.tag_config("agent", foreground="#00ff88", font=("Courier", 10, "bold"))
        self.chat_display.tag_config("reasoning", foreground="#ffaa00", font=("Courier", 9, "italic"))
        self.chat_display.tag_config("finding", foreground="#ff6b6b", font=("Courier", 10))
        self.chat_display.tag_config("recommendation", foreground="#4ecdc4", font=("Courier", 10))
        self.chat_display.tag_config("info", foreground="#888888", font=("Courier", 9))
        
        # Input area
        input_frame = ctk.CTkFrame(left_panel)
        input_frame.pack(fill="x", pady=(0, 0))
        
        self.user_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Describe your PC issue here...",
            font=("Helvetica", 11),
            height=40
        )
        self.user_input.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.user_input.bind("<Return>", lambda e: self.handle_user_input())
        
        self.send_btn = ctk.CTkButton(
            input_frame,
            text="Send",
            width=80,
            command=self.handle_user_input,
            font=("Helvetica", 11, "bold")
        )
        self.send_btn.pack(side="left")
        
        # Right Panel - Diagnostics & Details
        right_panel = ctk.CTkFrame(content)
        right_panel.pack(side="right", fill="both", padx=(5, 0), width=350)
        
        # Diagnostics section
        diag_label = ctk.CTkLabel(
            right_panel,
            text="System Diagnostics",
            font=("Helvetica", 14, "bold")
        )
        diag_label.pack(pady=(0, 10))
        
        # Quick diagnosis button
        self.diagnose_btn = ctk.CTkButton(
            right_panel,
            text="▶ Run Full Diagnostics",
            command=self.run_full_diagnostics,
            font=("Helvetica", 11, "bold"),
            height=35,
            fg_color="#00d4ff",
            text_color="#000000"
        )
        self.diagnose_btn.pack(fill="x", pady=(0, 10))
        
        # System info display
        self.system_info = scrolledtext.ScrolledText(
            right_panel,
            height=35,
            width=40,
            font=("Courier", 9),
            bg="#0f0f1e",
            fg="#e0e0e0"
        )
        self.system_info.pack(fill="both", expand=True)
        self.system_info.config(state="disabled")
        
        # Configure system info tags
        self.system_info.tag_config("header", foreground="#00d4ff", font=("Courier", 9, "bold"))
        self.system_info.tag_config("good", foreground="#00ff88", font=("Courier", 9, "bold"))
        self.system_info.tag_config("warning", foreground="#ffaa00", font=("Courier", 9, "bold"))
        self.system_info.tag_config("critical", foreground="#ff6b6b", font=("Courier", 9, "bold"))
        self.system_info.tag_config("value", foreground="#4ecdc4", font=("Courier", 9))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ctk.CTkLabel(
            self.main_container,
            textvariable=self.status_var,
            font=("Helvetica", 10),
            text_color="#888888"
        )
        status_bar.pack(fill="x", padx=10, pady=(5, 10))
    
    def setup_layout(self):
        """Configure grid layout"""
        pass
    
    def print_chat(self, role: str, message: str, tag: str = "info"):
        """Print message to chat display"""
        self.chat_display.config(state="normal")
        
        if role == "user":
            self.chat_display.insert("end", f"\nYou: ", "user")
            self.chat_display.insert("end", f"{message}\n", tag)
        elif role == "agent":
            self.chat_display.insert("end", f"\n🤖 Agent: ", "agent")
            self.chat_display.insert("end", f"{message}\n", tag)
        elif role == "reasoning":
            self.chat_display.insert("end", f"\n💭 Reasoning: ", "reasoning")
            self.chat_display.insert("end", f"{message}\n", "reasoning")
        elif role == "finding":
            self.chat_display.insert("end", f"\n📊 ", "finding")
            self.chat_display.insert("end", f"{message}\n", "finding")
        elif role == "recommendation":
            self.chat_display.insert("end", f"\n✓ ", "recommendation")
            self.chat_display.insert("end", f"{message}\n", "recommendation")
        
        self.chat_display.see("end")
        self.chat_display.config(state="disabled")
    
    def update_status(self, message: str):
        """Update status bar"""
        self.status_var.set(f"Status: {message}")
        self.root.update()
    
    def handle_user_input(self):
        """Handle user input from chat"""
        message = self.user_input.get().strip()
        
        if not message:
            return
        
        self.print_chat("user", message)
        self.user_input.delete(0, "end")
        
        self.send_btn.config(state="disabled")
        
        # Run in background thread
        thread = threading.Thread(target=self.process_user_issue, args=(message,))
        thread.daemon = True
        thread.start()
    
    def process_user_issue(self, issue: str):
        """Process user's issue description"""
        try:
            self.update_status("Analyzing your issue...")
            self.print_chat("agent", "I'm analyzing your PC issue. Please wait while I gather diagnostics...")
            
            self.root.after(1000)  # Brief pause for effect
            
            # Run diagnostics
            self.update_status("Running system diagnostics...")
            self.print_chat("reasoning", "Gathering system information...")
            
            self.current_diagnostics = self.diagnostics.get_system_info()
            
            self.root.after(500)
            
            # Analyze the issue
            self.update_status("Analyzing diagnostics...")
            self.print_chat("reasoning", "Analyzing your issue based on system data...")
            
            analysis = self.engine.analyze_issue(issue, self.current_diagnostics)
            
            self.root.after(500)
            
            # Display results
            self.display_analysis_results(analysis)
            
            # Update system info
            self.update_system_info_display()
            
            self.update_status("Analysis complete. Ready for next issue.")
            
        except Exception as e:
            self.print_chat("agent", f"Error: {str(e)}", "finding")
            self.update_status("Error during analysis")
        finally:
            self.send_btn.config(state="normal")
    
    def display_analysis_results(self, analysis: Dict):
        """Display analysis results in chat"""
        
        # Issue type and severity
        self.print_chat("agent", f"Issue Type: {analysis.get('issue_type', 'Unknown')}", "info")
        severity = analysis.get('severity', 'Unknown')
        tag = "critical" if severity == "Critical" else "warning" if severity in ["High", "Medium"] else "good"
        self.print_chat("agent", f"Severity Level: {severity}", tag)
        
        # Reasoning
        reasoning_list = analysis.get('reasoning', [])
        if reasoning_list:
            self.print_chat("reasoning", reasoning_list[0] if len(reasoning_list) == 1 else 
                           f"{reasoning_list[0]} (and {len(reasoning_list)-1} more)")
        
        # Findings
        findings = analysis.get('findings', [])
        if findings:
            self.print_chat("agent", "Key Findings:")
            for finding in findings[:3]:  # Show top 3
                self.print_chat("finding", finding)
            if len(findings) > 3:
                self.print_chat("info", f"...and {len(findings)-3} more findings")
        
        # Recommendations
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            self.print_chat("agent", "Recommended Solutions:")
            for i, rec in enumerate(recommendations[:5], 1):  # Show top 5
                self.print_chat("recommendation", rec)
            if len(recommendations) > 5:
                self.print_chat("info", f"...and {len(recommendations)-5} more recommendations")
        
        # Next steps
        next_steps = analysis.get('next_steps', [])
        if next_steps:
            self.print_chat("agent", "Next Steps:")
            for step in next_steps[:3]:
                self.print_chat("info", step)
    
    def run_full_diagnostics(self):
        """Run full system diagnostics"""
        self.diagnose_btn.config(state="disabled")
        thread = threading.Thread(target=self._run_diagnostics_thread)
        thread.daemon = True
        thread.start()
    
    def _run_diagnostics_thread(self):
        """Run diagnostics in background thread"""
        try:
            self.update_status("Running full diagnostics...")
            self.print_chat("agent", "Running comprehensive system diagnostics...")
            
            # Get all diagnostics
            self.current_diagnostics = self.diagnostics.get_system_info()
            
            # Display results
            self.update_system_info_display()
            
            self.update_status("Diagnostics complete.")
            
        except Exception as e:
            self.print_chat("agent", f"Error during diagnostics: {str(e)}", "finding")
            self.update_status("Error during diagnostics")
        finally:
            self.diagnose_btn.config(state="normal")
    
    def update_system_info_display(self):
        """Update system information display"""
        self.system_info.config(state="normal")
        self.system_info.delete(1.0, "end")
        
        if not self.current_diagnostics:
            self.system_info.insert("end", "No diagnostics data available\n", "info")
            self.system_info.config(state="disabled")
            return
        
        diag = self.current_diagnostics
        
        # CPU
        cpu = diag.get('cpu', {})
        self.system_info.insert("end", "━━━ CPU ━━━\n", "header")
        if cpu.get('usage_percent') is not None:
            tag = "critical" if cpu['usage_percent'] > 80 else "warning" if cpu['usage_percent'] > 50 else "good"
            self.system_info.insert("end", f"Usage: ", "value")
            self.system_info.insert("end", f"{cpu['usage_percent']:.1f}%\n", tag)
        self.system_info.insert("end", f"Cores: {cpu.get('count', 'N/A')}\n", "value")
        if cpu.get('temperature'):
            tag = "critical" if cpu['temperature'] > 85 else "warning" if cpu['temperature'] > 70 else "good"
            self.system_info.insert("end", f"Temp: ", "value")
            self.system_info.insert("end", f"{cpu['temperature']:.1f}°C\n", tag)
        self.system_info.insert("end", f"Status: {cpu.get('status', 'N/A')}\n\n", "value")
        
        # Memory
        memory = diag.get('memory', {})
        self.system_info.insert("end", "━━━ RAM ━━━\n", "header")
        tag = "critical" if memory.get('percent', 0) > 90 else "warning" if memory.get('percent', 0) > 80 else "good"
        self.system_info.insert("end", f"Used: ", "value")
        self.system_info.insert("end", f"{memory.get('percent', 0):.1f}%\n", tag)
        self.system_info.insert("end", f"Total: {format_bytes(memory.get('total', 0))}\n", "value")
        self.system_info.insert("end", f"Available: {format_bytes(memory.get('available', 0))}\n", "value")
        self.system_info.insert("end", f"Status: {memory.get('status', 'N/A')}\n\n", "value")
        
        # Disk
        disk = diag.get('disk', {})
        self.system_info.insert("end", "━━━ DISK ━━━\n", "header")
        for partition in disk.get('partitions', [])[:2]:  # Show first 2
            self.system_info.insert("end", f"\n{partition['device']}:\n", "header")
            tag = "critical" if partition['percent'] > 90 else "warning" if partition['percent'] > 80 else "good"
            self.system_info.insert("end", f"  Used: ", "value")
            self.system_info.insert("end", f"{partition['percent']:.1f}%\n", tag)
            self.system_info.insert("end", f"  Free: {format_bytes(partition['free'])}\n", "value")
        
        self.system_info.insert("end", "\n", "value")
        
        # Network
        network = diag.get('network', {})
        self.system_info.insert("end", "━━━ NETWORK ━━━\n", "header")
        interfaces = network.get('interfaces', {})
        active = sum(1 for stats in interfaces.values() if stats.get('is_up'))
        total = len(interfaces)
        self.system_info.insert("end", f"Interfaces: {active}/{total} active\n\n", "value")
        
        self.system_info.config(state="disabled")


def main():
    """Main entry point"""
    root = ctk.CTk()
    app = TroubleshootingAgentGUI(root)
    
    # Initial message
    app.print_chat("agent", "Welcome! I'm your AI PC Troubleshooting Agent.")
    app.print_chat("agent", "Describe any PC issues you're experiencing, such as:")
    app.print_chat("info", "• 'My PC is running slow'")
    app.print_chat("info", "• 'An application won't open'")
    app.print_chat("info", "• 'My disk is full'")
    app.print_chat("info", "• 'Network connection is unstable'")
    app.print_chat("agent", "\nI'll analyze your system and provide solutions!")
    
    root.mainloop()


if __name__ == "__main__":
    main()
