"""
AI PC Troubleshooting Agent
Enhanced Integrated Main Module
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext
import threading
import time
from typing import Dict
from diagnostics import WindowsDiagnostics, format_bytes
from troubleshooting_engine import TroubleshootingEngine
from config import GUI_CONFIG


class EnhancedTroubleshootingAgent(ctk.CTk):
    """Enhanced troubleshooting agent with all features"""

    def __init__(self):
        super().__init__()

        self.title(GUI_CONFIG["window_title"])
        self.geometry(GUI_CONFIG["window_size"])

        ctk.set_appearance_mode(GUI_CONFIG["theme"])
        ctk.set_default_color_theme(GUI_CONFIG["color_theme"])

        self.diagnostics = WindowsDiagnostics()
        self.engine = TroubleshootingEngine()
        self.current_diagnostics = None

        self.create_widgets()
        self.show_welcome_message()

    def create_widgets(self):
        """Create all UI widgets"""
        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True, padx=0, pady=0)

        header = ctk.CTkFrame(main, fg_color=GUI_CONFIG["header_color"])
        header.pack(fill="x", padx=0, pady=0)

        title = ctk.CTkLabel(
            header,
            text=GUI_CONFIG["window_title"],
            font=("Helvetica", 24, "bold"),
            text_color=GUI_CONFIG["primary_color"]
        )
        title.pack(pady=15)

        subtitle = ctk.CTkLabel(
            header,
            text="Intelligent System Diagnostics & Troubleshooting",
            font=("Helvetica", 12),
            text_color="#888888"
        )
        subtitle.pack(pady=(0, 15))

        content = ctk.CTkFrame(main)
        content.pack(fill="both", expand=True, padx=10, pady=10)

        left = ctk.CTkFrame(content)
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))

        chat_label = ctk.CTkLabel(left, text="Chat Interface", font=("Helvetica", 14, "bold"))
        chat_label.pack(pady=(0, 10))

        self.chat = scrolledtext.ScrolledText(
            left, height=20, width=60,
            font=("Courier", 10),
            bg=GUI_CONFIG["background_color"],
            fg=GUI_CONFIG["text_color"],
            insertbackground=GUI_CONFIG["primary_color"]
        )
        self.chat.pack(fill="both", expand=True, pady=(0, 10))
        self.chat.config(state="disabled")

        self.chat.tag_config("user", foreground=GUI_CONFIG["primary_color"], font=("Courier", 10, "bold"))
        self.chat.tag_config("agent", foreground=GUI_CONFIG["success_color"], font=("Courier", 10, "bold"))
        self.chat.tag_config("reasoning", foreground=GUI_CONFIG["warning_color"], font=("Courier", 9, "italic"))
        self.chat.tag_config("finding", foreground=GUI_CONFIG["error_color"], font=("Courier", 10))
        self.chat.tag_config("recommendation", foreground=GUI_CONFIG["info_color"], font=("Courier", 10))
        self.chat.tag_config("info", foreground="#888888", font=("Courier", 9))

        input_frame = ctk.CTkFrame(left)
        input_frame.pack(fill="x")

        self.input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Describe your PC issue...",
            font=("Helvetica", 11),
            height=40
        )
        self.input.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.input.bind("<Return>", lambda e: self.process_user_input())

        self.send_btn = ctk.CTkButton(
            input_frame,
            text="Send",
            width=80,
            command=self.process_user_input,
            font=("Helvetica", 11, "bold")
        )
        self.send_btn.pack(side="left")

        right = ctk.CTkFrame(content)
        right.pack(side="right", fill="both", padx=(5, 0), width=350)

        diag_label = ctk.CTkLabel(right, text="System Diagnostics", font=("Helvetica", 14, "bold"))
        diag_label.pack(pady=(0, 10))

        self.diagnose_btn = ctk.CTkButton(
            right,
            text="> Run Full Diagnostics",
            command=self.run_diagnostics,
            font=("Helvetica", 11, "bold"),
            height=35,
            fg_color=GUI_CONFIG["primary_color"],
            text_color="#000000"
        )
        self.diagnose_btn.pack(fill="x", pady=(0, 10))

        self.system_info = scrolledtext.ScrolledText(
            right, height=35, width=40,
            font=("Courier", 9),
            bg=GUI_CONFIG["background_color"],
            fg=GUI_CONFIG["text_color"]
        )
        self.system_info.pack(fill="both", expand=True)
        self.system_info.config(state="disabled")

        self.system_info.tag_config("header", foreground=GUI_CONFIG["primary_color"], font=("Courier", 9, "bold"))
        self.system_info.tag_config("good", foreground=GUI_CONFIG["success_color"], font=("Courier", 9, "bold"))
        self.system_info.tag_config("warning", foreground=GUI_CONFIG["warning_color"], font=("Courier", 9, "bold"))
        self.system_info.tag_config("critical", foreground=GUI_CONFIG["error_color"], font=("Courier", 9, "bold"))

        self.status = tk.StringVar(value="Ready")
        status_bar = ctk.CTkLabel(main, textvariable=self.status, font=("Helvetica", 10), text_color="#888888")
        status_bar.pack(fill="x", padx=10, pady=(5, 10))

    def show_welcome_message(self):
        """Show welcome message"""
        self.add_chat("agent", "Welcome to AI PC Troubleshooting Agent!")
        self.add_chat("agent", "I can help diagnose issues like:")
        self.add_chat("agent", "  - System running slow")
        self.add_chat("agent", "  - Applications won't open")
        self.add_chat("agent", "  - Low disk space")
        self.add_chat("agent", "  - Network problems")
        self.add_chat("agent", "\nDescribe your issue in the chat box below.")

    def add_chat(self, role: str, message: str, tag: str = "info"):
        """Add message to chat"""
        self.chat.config(state="normal")
        if role == "user":
            self.chat.insert("end", f"\nYou: ", "user")
            self.chat.insert("end", f"{message}\n", tag)
        elif role == "agent":
            self.chat.insert("end", f"\nAgent: ", "agent")
            self.chat.insert("end", f"{message}\n", tag)
        elif role == "info":
            self.chat.insert("end", f"\n{message}\n", "info")
        self.chat.see("end")
        self.chat.config(state="disabled")

    def process_user_input(self):
        """Process user message"""
        message = self.input.get().strip()
        if not message:
            return

        self.add_chat("user", message)
        self.input.delete(0, "end")
        self.send_btn.config(state="disabled")

        thread = threading.Thread(target=self.analyze_issue, args=(message,))
        thread.daemon = True
        thread.start()

    def analyze_issue(self, issue: str):
        """Analyze user issue"""
        try:
            self.status.set("Analyzing...")
            self.add_chat("agent", "Analyzing your issue... Please wait.")

            self.current_diagnostics = self.diagnostics.get_system_info()
            analysis = self.engine.analyze_issue(issue, self.current_diagnostics)

            self.display_analysis(analysis)
            self.update_system_display()

            self.status.set("Ready")

        except Exception as e:
            self.add_chat("agent", f"Error: {str(e)}", "finding")
            self.status.set("Error")
        finally:
            self.send_btn.config(state="normal")

    def display_analysis(self, analysis: Dict):
        """Display analysis results"""
        self.add_chat("agent", f"Issue Type: {analysis.get('issue_type')}")
        self.add_chat("agent", f"Severity: {analysis.get('severity')}",
                     "critical" if analysis.get('severity') == "Critical" else "warning")

        for finding in analysis.get('findings', [])[:3]:
            self.add_chat("agent", finding, "finding")

        for rec in analysis.get('recommendations', [])[:5]:
            self.add_chat("agent", rec, "recommendation")

    def run_diagnostics(self):
        """Run full diagnostics"""
        self.diagnose_btn.config(state="disabled")
        thread = threading.Thread(target=self._diagnose_thread)
        thread.daemon = True
        thread.start()

    def _diagnose_thread(self):
        """Diagnostics thread"""
        try:
            self.status.set("Running diagnostics...")
            self.current_diagnostics = self.diagnostics.get_system_info()
            self.update_system_display()
            self.status.set("Ready")
        except Exception as e:
            self.add_chat("agent", f"Error: {str(e)}", "finding")
            self.status.set("Error")
        finally:
            self.diagnose_btn.config(state="normal")

    def update_system_display(self):
        """Update system info display"""
        self.system_info.config(state="normal")
        self.system_info.delete(1.0, "end")

        if not self.current_diagnostics:
            self.system_info.insert("end", "No data\n")
            self.system_info.config(state="disabled")
            return

        d = self.current_diagnostics

        self.system_info.insert("end", "--- CPU ---\n", "header")
        cpu = d.get('cpu', {})
        self.system_info.insert("end", f"Usage: {cpu.get('usage_percent', 0):.1f}%\n")
        self.system_info.insert("end", f"Status: {cpu.get('status', 'N/A')}\n\n")

        self.system_info.insert("end", "--- RAM ---\n", "header")
        mem = d.get('memory', {})
        tag = "critical" if mem.get('percent', 0) > 90 else "warning" if mem.get('percent', 0) > 80 else "good"
        self.system_info.insert("end", f"Used: {mem.get('percent', 0):.1f}%\n", tag)
        self.system_info.insert("end", f"Available: {format_bytes(mem.get('available', 0))}\n\n")

        self.system_info.insert("end", "--- DISK ---\n", "header")
        for p in d.get('disk', {}).get('partitions', [])[:2]:
            tag = "critical" if p.get('percent', 0) > 90 else "warning" if p.get('percent', 0) > 80 else "good"
            self.system_info.insert("end", f"{p['device']}: {p.get('percent', 0):.1f}%\n", tag)

        self.system_info.config(state="disabled")


def main():
    """Main entry point"""
    app = EnhancedTroubleshootingAgent()
    app.mainloop()


if __name__ == "__main__":
    main()
